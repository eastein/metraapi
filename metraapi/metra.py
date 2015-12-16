from __future__ import absolute_import
from __future__ import print_function

import sys
import time
import json
import pprint

import requests

# from .metraapi_internal import Internal, , \
#    ,

from . import metraapi_internal as internal


class MetraException(Exception):

    """Base for all exceptions in this API binding."""


class InvalidRouteException(MetraException):

    """The user of this library has requested an invalid route that cannot be calculated."""


class InvalidStationException(MetraException):

    """The station requested does not exist."""


class InvalidLineException(MetraException):

    """The line requested does not exist."""


STATIONS_CACHETIME = 60.0


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


def get_stations_from_line(line_id):
    params = internal.get_stations_request_parameters(line_id)

    stations_data = requests.get(params['url'], params=params['query']).text

    return internal.interpret_stations_response(stations_data)


class Metra(object):

    def __init__(self):
        self._lines = dict([(l['id'], Line(l['id'], l['name'], l['twitter'])) for l in get_lines()])

    @property
    def lines(self):
        return self._lines

    def line(self, line_id):
        if line_id not in self._lines:
            raise InvalidLineException

        return self._lines[line_id]


class Line(object):

    def __init__(self, _id, name, twitter):
        self.id = _id
        self.name = name
        self.twitter = twitter
        self._sc = None
        self._scts = None

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
        now = time.time()

        if (self._sc is None) or (self._scts < (now - STATIONS_CACHETIME)):
            self._scts = now
            self._sc = [Station(self, s['id'], s['name']) for s in get_stations_from_line(self.id)]

        return self._sc

    def station(self, station_id):
        for station in self.stations:
            if station.id == station_id:
                return station
        raise InvalidStationException


class Station(object):

    def __init__(self, line, _id, name):
        self.line = line
        self.id = _id
        self.name = name

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
        line = met.lines[sys.argv[1]]
    except IndexError:
        for line in met.lines.values():
            print('%s%s%s' % (line.id.ljust(6), line.name.ljust(25), line.twitter))
        sys.exit(0)

    station_problem = False

    try:
        dpt = line.station(sys.argv[2].upper())
        arv = line.station(sys.argv[3].upper())
    except IndexError:
        station_problem = True
    except InvalidStationException:
        print('One or more of the requested stations is not valid. Valid stations:')
        station_problem = True

    if station_problem:
        for station in line.stations:
            print(station)
        sys.exit(0)

    runs = dpt.runs_to(arv)

    if not runs:
        print('There are no trains presently.')
        sys.exit(0)

    for run in runs:
        print(run)
