from __future__ import absolute_import
from __future__ import print_function

import sys
import time
import json
import base64
import pprint

import weakref
import threading
import bisect
import functools
import types

import requests

# from .metraapi_internal import Internal, , \
#    ,

from . import metraapi_internal as internal
import metraapi.gis
import metraapi.gtfs


class MetraException(Exception):

    """Base for all exceptions in this API binding."""


class InvalidRouteException(MetraException):

    """The user of this library has requested an invalid route that cannot be calculated."""


class InvalidStationException(MetraException):

    """The station requested does not exist."""


class InvalidLineException(MetraException):

    """The line requested does not exist."""


@functools.total_ordering
class CacheEntry(object):

    def __init__(self, value, expire_deadline):
        self.value = value
        self.expire_deadline = expire_deadline

    def __lt__(self, other):
        return self.expire_deadline < other.expire_deadline

    def __eq__(self, other):
        return self.expire_deadline == other.expire_deadline


class Cache(object):

    class TTL(object):
        LINES = 3600.0
        STATIONS = 300.0
        ARRIVALS = 5.0
        GIS_DATA = 3600.0 * 24 * 7
        GTFS_DATA = 3600.0 * 24 * 7

    def __init__(self):
        self.lock = threading.Lock()
        self.cache_lookup = weakref.WeakValueDictionary()
        self.cache_expire_queue = list()

    def insert(self, cache_key, value, now, ttl):
        with self.lock:
            if cache_key not in self.cache_lookup:
                entry = CacheEntry(value, now + ttl)
                bisect.insort_right(self.cache_expire_queue, entry)
                self.cache_lookup[cache_key] = entry
            else:
                # TODO it might be nice to re-up the TTL, it'll still expire
                # at the old time as of now.
                self.cache_lookup[cache_key].value = value

    def get(self, cache_key, now):
        self.do_expires(now)
        entry = self.cache_lookup.get(cache_key)
        if entry is not None:
            if entry.expire_deadline < now:
                return None
            return entry

    def do_expires(self, now):
        with self.lock:
            i = 0
            for e in self.cache_expire_queue:
                if e.expire_deadline > now:
                    break
                i += 1

            if i > 0:
                self.cache_expire_queue = self.cache_expire_queue[i:]

    @classmethod
    def get_function_identifier(cls, f):
        if isinstance(f, types.FunctionType):
            return '%s.%s' % (f.__module__, f.__name__)
        elif isinstance(f, types.MethodType):
            f_key = '%s.%s.%s' % (f.im_class.__module__, f.im_class, f.__name__)
        else:
            return f.__name__

    def cached(self, ttl):
        def decorate(f):
            @functools.wraps(f)
            def inner(*a, **kw):
                function_identifier = self.get_function_identifier(f)
                cache_key = base64.b64encode(json.dumps([function_identifier, a, kw]).encode('utf-8'))
                now = time.time()

                cache_entry = self.get(cache_key, now)
                if cache_entry is None:
                    #print('cache miss for %s' % function_identifier)
                    v = f(*a, **kw)
                    self.insert(cache_key, v, now, ttl)
                    return v
                else:
                    #print('cache hit for %s' % function_identifier)
                    return cache_entry.value

            return inner
        return decorate

cache = Cache()


@cache.cached(Cache.TTL.LINES)
def get_lines(hard_code=False):
    if hard_code:
        lines_data = json.dumps([
            {
                'id': line_id,
                'text': line_name,
            }
            for (line_id, line_name) in [
                ('BNSF', 'BNSF Railway'),
                ('HC', 'Heritage Corridor'),
                ('ME', 'Metra Electric District'),
                ('MD-N', 'Milwaukee District North'),
                ('MD-W', 'Milwaukee District West'),
                ('NCS', 'North Central Service'),
                ('RI', 'Rock Island District'),
                ('SWS', 'South West Service'),
                ('UP-N', 'Union Pacific North'),
                ('UP-NW', 'Union Pacific Northwest'),
                ('UP-W', 'Union Pacific West')
            ]
        ])
    else:
        params = internal.get_lines_request_parameters()

        lines_data = requests.get(params['url'], params=params['query']).text

    return internal.interpret_lines_response(lines_data)


@cache.cached(Cache.TTL.STATIONS)
def get_stations_from_line(line_id):
    params = internal.get_stations_request_parameters(line_id)

    stations_data = requests.get(params['url'], params=params['query']).text

    return internal.interpret_stations_response(stations_data)


@cache.cached(Cache.TTL.GIS_DATA)
def find_gis_station(long_name, geographic_filter=None):
    return metraapi.gis.Stations.find_station(long_name, geographic_filter=geographic_filter)


@cache.cached(Cache.TTL.GTFS_DATA)
def find_gtfs_stop(stop_id):
    return metraapi.gtfs.MetraGTFS.get_stop(stop_id)


@cache.cached(Cache.TTL.STATIONS)
def get_station_objects(line_id):
    return [
        Station(line_id, s['id'], s['name'])
        for s in get_stations_from_line(line_id)
    ]


@cache.cached(Cache.TTL.LINES)
def get_line_objects():
    return dict([(l['id'], Line(l['id'], l['name'], l['twitter'])) for l in get_lines()])


def get_line_object(line_id):
    l = get_line_objects().get(line_id)
    if l is None:
        raise InvalidLineException
    return l


class Metra(object):

    @property
    def lines(self):
        return get_line_objects()

    def line(self, line_id):
        return get_line_object(line_id)


class Line(object):

    def __init__(self, _id, name, twitter):
        self.id = _id
        self.name = name
        self.twitter = twitter

    def todict(self):
        return {
            'id': self.id,
            'name': self.name,
            'twitter': self.twitter
        }

    def __repr__(self):
        return '%s (%s)' % (self.name, self.id)

    def __eq__(self, o):
        return (type(self) == type(o)) and (self.id == o.id)

    @property
    def stations(self):
        return get_station_objects(self.id)

    def station(self, station_id):
        for station in self.stations:
            if station.id == station_id:
                return station
        raise InvalidStationException


def ref_accessor(attr, getter):
    def dec(f):
        @functools.wraps(f)
        def inner(self, *a, **kw):
            fields = f(self, *a, **kw)
            attr_object = getattr(self, attr)

            def field_transform(field):
                if isinstance(field, tuple):
                    return field
                else:
                    return (field, field)

            if isinstance(fields, list):
                transformed_fields = [field_transform(field) for field in fields]
                if attr_object is not None:
                    return dict([
                        (field_to, getter(attr_object, field_from))
                        for
                        (field_from, field_to) in transformed_fields
                    ])
                else:
                    return dict([
                        (field_to, None)
                        for
                        (field_from, field_to) in transformed_fields
                    ])
            else:
                if attr_object is not None:
                    return getter(attr_object, fields)
                else:
                    return None
        return inner
    return dec


class Station(object):

    def __init__(self, line_id, _id, name):
        self.line_id = line_id
        self.id = _id
        self.name = name

    @property
    def line(self):
        return get_line_object(self.line_id)

    @property
    def gtfs_stop(self):
        return find_gtfs_stop(self.id)

    @property
    @ref_accessor('gtfs_stop', dict.get)
    def wheelchair_boarding(self):
        return 'wheelchair_boarding'

    @property
    @ref_accessor('gtfs_stop', dict.get)
    def url(self):
        return 'stop_url'

    @property
    @ref_accessor('gtfs_stop', dict.get)
    def coordinates(self):
        return [
            ('stop_lat', 'latitude'),
            ('stop_lon', 'longitude')
        ]

    @property
    def gis_station(self):
        coords = self.coordinates
        if coords is None:
            return find_gis_station(self.name)
        else:
            return find_gis_station(self.name, geographic_filter={
                'latitude': coords['latitude'],
                'longitude': coords['longitude'],
                'distance_km': 1.0,
            })

    @property
    def location(self):
        location_dictionary = dict()
        location_dictionary.update(self.coordinates)
        location_dictionary.update(self.postal_location)
        return location_dictionary

    @property
    @ref_accessor('gis_station', getattr)
    def postal_location(self):
        return ['municipality', 'address']

    @property
    @ref_accessor('gis_station', getattr)
    def fare_zone(self):
        return 'fare_zone'

    @property
    @ref_accessor('gis_station', getattr)
    def bike_parking(self):
        return 'bike_parking'

    def __eq__(self, o):
        return (type(self) == type(o)) and (self.id == o.id)

    def __repr__(self):
        return self.id

    def __str__(self):
        return repr(self)

    def runs_to(self, arv_station):
        if self.line != arv_station.line:
            raise InvalidRouteException(
                "%s and %s are on different lines. This API and library do not support calculating transfers." % (self, arv_station))

        runs = list()
        for arv in get_arrival_times(self.line.id, self.id, arv_station.id):
            runs.append(Run(self, arv_station, **arv))

        runs.sort()

        return runs


class Run(object):

    def __init__(self, _dpt_station, _arv_station, **kwargs):
        # defining characteristics
        self.line = _dpt_station.line
        self.dpt_station = _dpt_station
        self.arv_station = _arv_station
        self.train_number = kwargs['train_num']

        # properties (True, False, None for unknown)
        self.en_route = kwargs['en_route']
        self.gps = kwargs['gps']
        self.on_time = kwargs['on_time']

        # still no idea what this is, but we may as well pass it through
        self.state = kwargs.get('state')

        # datetimes
        self.estimated_dpt_time = kwargs['estimated_dpt_time']
        self.estimated_arv_time = kwargs['estimated_arv_time']
        self.scheduled_dpt_time = kwargs['scheduled_dpt_time']
        self.scheduled_arv_time = kwargs['scheduled_arv_time']
        self.as_of = kwargs['as_of']

    @property
    def dpt_time(self):
        if self.estimated_dpt_time is None:
            return self.scheduled_dpt_time
        else:
            return self.estimated_dpt_time

    @property
    def arv_time(self):
        if self.estimated_arv_time is None:
            return self.scheduled_arv_time
        else:
            return self.estimated_arv_time

    def __cmp__(self, o):
        if type(self) != type(o):
            return 0

        return cmp(self.dpt_time, o.dpt_time)

    def __lt__(self, o):
        if type(self) != type(o):
            return False

        return self.dpt_time < o.dpt_time

    def __repr__(self):
        LKUP = {
            True: "ON",
            False: "OFF",
            None: 'UNK'
        }
        LKUP2 = {
            True: "y",
            False: "n",
            None: '?'
        }
        gps = LKUP[self.gps]
        on_time = LKUP2[self.on_time]
        en_route = LKUP2[self.en_route]

        def jt(dt):
            """Just time - turn a datetime into a string that only contains the time."""
            if dt is None:
                return '?'

            return dt.strftime("%H:%M")

        return "Train #%d %s->%s DPT @ %s (sched %s), ARV @ %s (sched %s). GPS:%s, ONTIME:%s. ENROUTE:%s. (as of %s)" % (self.train_number, self.dpt_station, self.arv_station, jt(self.estimated_dpt_time), jt(self.scheduled_dpt_time), jt(self.estimated_arv_time), jt(self.scheduled_arv_time), self.gps, self.on_time, self.en_route, jt(self.as_of))


@cache.cached(Cache.TTL.ARRIVALS)
def get_arrival_times(line_id, origin_station_id, destination_station_id, verbose=False):

    # acquity request
    params = internal.get_acquity_request_parameters(line_id, origin_station_id, destination_station_id)

    result = requests.post(params['url'], headers=params['headers'], data=params['payload'])

    d = result.json()['d']
    acquity_data = json.loads(d)

    if verbose:
        print('data from %s:' % params['url]'])
        pprint.pprint(acquity_data)

    # gtd request
    params = internal.get_gtd_request_parameters(line_id, origin_station_id, destination_station_id)
    gtd_data = requests.get(params['url'], params=params['query']).json()

    if verbose:
        print('data from %s:' % params['url'])
        pprint.pprint(gtd_data)

    return internal.interpret_arrival_times(line_id, origin_station_id, destination_station_id,
                                            acquity_data=acquity_data, gtd_data=gtd_data)


if __name__ == '__main__':
    met = Metra()

    try:
        line = met.line(sys.argv[1])
    except IndexError:
        for line in met.lines.values():
            print('%s%s%s' % (line.id.ljust(6), line.name.ljust(25), line.twitter))
        sys.exit(0)

    station_problem = False
    insufficient_stations = False
    dpt = None
    try:
        dpt = line.station(sys.argv[2].upper())
        arv = line.station(sys.argv[3].upper())
    except IndexError:
        station_problem = True
        insufficient_stations = True
    except InvalidStationException:
        print('One or more of the requested stations is not valid. Valid stations:')
        station_problem = True

    if station_problem:
        if insufficient_stations and dpt is not None:
            print('Station Info %s (%s)' % (dpt.id, line.id))
            print('')
            for field_text, field_attr in [
                    ('ID', 'id'),
                    ('Name', 'name'),
                    ('Fare Zone', 'fare_zone'),
                    ('Wheelchair Boarding', 'wheelchair_boarding'),
                    ('Bike parking spots', 'bike_parking'),
                ]:
                v = getattr(dpt, field_attr)
                if v is not None:
                    print((' %s:' % field_text).ljust(24) + ('%s' % v))

            loc = dpt.location
            if len([v for v in loc.values() if v]) == 0:
                print(' Location:             Unknown')
            else:
                print(' Location:')
                for field_text, field_key, field_fmt in [
                        ('Latitude', 'latitude', '%0.8f'),
                        ('Longitude', 'longitude', '%0.8f'),
                        ('Address', 'address', '%s'),
                        ('City', 'municipality', '%s'),
                    ]:
                    v = loc.get(field_key)
                    if v:
                        print(('   %s:' % field_text).ljust(24) + (field_fmt % v))

        else:
            for station in line.stations:
                print(station)

        sys.exit(0)

    runs = dpt.runs_to(arv)

    if not runs:
        print('There are no trains presently.')
        sys.exit(0)

    for run in runs:
        print(run)
