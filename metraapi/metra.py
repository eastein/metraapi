import sys
import time
import requests
import json
from collections import OrderedDict
import datetime
import re
from pytz import utc, timezone
import pprint

TIME_RE = re.compile('^([0-9]+):([0-9]+)(am|pm)$')


class MetraException(Exception):

    """Base for all exceptions in this API binding."""


class InvalidRouteException(MetraException):

    """The user of this library has requested an invalid route that cannot be calculated."""


class InvalidStationException(MetraException):

    """The station requested does not exist."""


class InvalidLineException(MetraException):

    """The line requested does not exist."""


STATIONS_CACHETIME = 60.0


class Internal(object):
    CHICAGOTIME = timezone('US/Central')

    @classmethod
    def localize(cls, dt):
        return cls.CHICAGOTIME.localize(dt)

    @classmethod
    def parse_reltime(cls, s, now):
        if s is None:
            return None

        m = TIME_RE.match(s)
        if not m:
            return

        h, m, ampm = m.groups(1)
        h = int(h)
        if h == 12:
            h = 0

        kw = {
            'hour': h + {
                'am': 0,
                'pm': 12
            }[ampm],
            'minute': int(m),
            'second': 0
        }

        tomorrow = datetime.timedelta(days=1) + now

        potential_times = [
            cls.localize(datetime.datetime(year=now.year, month=now.month, day=now.day, **kw)),
            cls.localize(datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, **kw))
        ]

        potential_times.sort(cmp=lambda a, b: cmp(abs(a - now), abs(b - now)))
        return potential_times[0]

    @classmethod
    def jt(self, dt):
        """Just time - turn a datetime into a string that only contains the time."""
        if dt is None:
            return '?'

        return dt.strftime("%H:%M")

    @classmethod
    def max_datetime(cls, a, b):
        return cls.cmp_datetime_core(max, a, b)

    @classmethod
    def min_datetime(cls, a, b):
        return cls.cmp_datetime_core(min, a, b)

    @classmethod
    def cmp_datetime_core(cls, f, a, b):
        if a is None and b is not None:
            return b
        elif a is not None and b is None:
            return a
        return f(a, b)

    @classmethod
    def parse_datetime(cls, odd_time):
        # The time is coming back from Metra in UTC. Treat it as such and then convert it to Chicago local time
        unixtime = int(odd_time.strip('/Date()')) / 1000
        return utc.localize(datetime.datetime.utcfromtimestamp(unixtime)).astimezone(cls.CHICAGOTIME)


def get_lines():
    return [
        {
            'id': v[0],
            'name': v[1]
        }
        for v in [
            ('UP-N', 'Union Pacific North'),
            ('MD-N', 'Milwaukee District North'),
            ('NCS', 'North Central Service'),
            ('UP-NW', 'Union Pacific Northwest'),
            ('MD-W', 'Milwaukee District West'),
            ('UP-W', 'Union Pacific West'),
            ('BNSF', 'BNSF Railway'),
            ('HC', 'Heritage Corridor'),
            ('SWS', 'SouthWest Service'),
            ('RI', 'Rock Island District'),
            ('ME', 'Metra Electric District'),
        ]
    ]


def get_stations_from_line(line_id):
    result = requests.get('http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_stations_from_line.json',
                          params={'trackerNumber': 0, 'trainLineId': line_id})
    stations = result.json(object_pairs_hook=OrderedDict)['stations']

    return [{'id': station['id'], 'name': station['name'].strip()} for station in stations.values()]


class Metra(object):

    def __init__(self):
        self._lines = dict([(l['id'], Line(l['id'], l['name'])) for l in get_lines()])

    @property
    def lines(self):
        return self._lines

    def line(self, line_id):
        if line_id not in self._lines:
            raise InvalidLineException

        return self._lines[line_id]


class Line(object):

    def __init__(self, _id, name):
        self.id = _id
        self.name = name
        self._sc = None
        self._scts = None

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
        self.state = kwargs['state']

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
        jt = Internal.jt
        return "Train #%d %s->%s DPT @ %s (sched %s), ARV @ %s (sched %s). GPS:%s, ONTIME:%s. ENROUTE:%s. (as of %s)" % (self.train_number, self.dpt_station, self.arv_station, jt(self.estimated_dpt_time), jt(self.scheduled_dpt_time), jt(self.estimated_arv_time), jt(self.scheduled_arv_time), self.gps, self.on_time, self.en_route, jt(self.as_of))


def get_arrival_times(line_id, origin_station_id, destination_station_id, verbose=False, acquity_data=None, gtd_data=None):
    """
    :param acquity_data: the parsed JSON from the acquity train data endpoint
    :param gtd_data: the parsed JSON from the get_train_data endpoint
    :returns: list of arrivals
    """

    if acquity_data is None:
        headers = {
            'Content-Type': 'application/json; charset=UTF-8'
        }
        payload = {
            "stationRequest": {
                "Corridor": line_id,
                "Destination": destination_station_id,
                "Origin": origin_station_id
            }
        }
        TRAINDATA_URL = 'http://12.205.200.243/AJAXTrainTracker.svc/GetAcquityTrainData'
        result = requests.post(TRAINDATA_URL, headers=headers, data=json.dumps(payload))

        d = result.json()['d']
        acquity_data = json.loads(d)

        if verbose:
            print 'data from %s:' % TRAINDATA_URL
            pprint.pprint(acquity_data)

    if gtd_data is None:
        ARRIVALS_URL = 'http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_train_data.json'
        gtd_data = requests.get(
            ARRIVALS_URL, params={'line': line_id.upper(), 'origin': origin_station_id, 'destination': destination_station_id}).json()

        if verbose:
            print 'data from %s:' % ARRIVALS_URL
            pprint.pprint(gtd_data)

    now = Internal.parse_datetime(acquity_data['responseTime'])

    def difference_greaterthan(a, b, hours):
        return abs(a - b) > datetime.timedelta(hours=hours)

    def build_arrival(now, train):
        # one time I observed that KX65 showed online, but 365 showed in the
        # station screens. What... but that is what it is. Metra, you are odd.
        r = {'estimated_dpt_time': Internal.parse_datetime(train['estimated_dpt_time']),
             'scheduled_dpt_time': Internal.parse_datetime(train['scheduled_dpt_time']),
             'as_of': now,
             'dpt_station': train['dpt_station'],
             'train_num': int(train['train_num'].replace('KX', '3')),
             'state': train['RunState']}
        # if the train number is 0, it's not a valid prediction
        if r['train_num'] == 0:
            return
        # if the estimated time is way off from the request time, then it doesn't make sense either
        if difference_greaterthan(now, r['estimated_dpt_time'], 24):
            return
        return r

    arrivals = []
    arrival_bytrain = {}
    for (k, v) in acquity_data.iteritems():
        if k.startswith('train'):
            a = build_arrival(now, v)
            if a is not None:
                arrivals.append(a)
                arrival_bytrain[a['train_num']] = a

    for (k, v) in gtd_data.iteritems():
        if k.startswith('train'):
            if 'error' in v:
                continue

            # see above also
            train_num = int(v['train_num'].replace('KX', '3'))
            if train_num in arrival_bytrain:
                a = arrival_bytrain[train_num]
                a['gps'] = v['hasData']
                a['on_time'] = not v['hasDelay']
                a['en_route'] = not v['notDeparted']
                a['scheduled_dpt_time'] = Internal.min_datetime(
                    a.get('scheduled_dpt_time'), Internal.parse_reltime(v.get('scheduled_dpt_time'), now))
                a['estimated_dpt_time'] = Internal.min_datetime(
                    a.get('estimated_dpt_time'), Internal.parse_reltime(v.get('estimated_dpt_time'), now))
                a['scheduled_arv_time'] = Internal.max_datetime(
                    a.get('scheduled_arv_time'), Internal.parse_reltime(v.get('scheduled_arv_time'), now))
                a['estimated_arv_time'] = Internal.max_datetime(
                    a.get('estimated_arv_time'), Internal.parse_reltime(v.get('estimated_arv_time'), now))

    for a in arrivals:
        for k in ['gps', 'on_time', 'en_route', 'scheduled_dpt_time', 'estimated_dpt_time', 'scheduled_arv_time', 'estimated_arv_time']:
            a[k] = a.get(k)

    return arrivals

if __name__ == '__main__':
    met = Metra()

    try:
        line = met.lines[sys.argv[1]]
    except IndexError:
        lines = get_lines()
        for line in lines:
            print "%(id)s: %(name)s" % line
        sys.exit(0)

    stations = line.stations
    station_problem = False

    try:
        dpt = line.station(sys.argv[2].upper())
        arv = line.station(sys.argv[3].upper())
    except IndexError:
        station_problem = True
    except InvalidStationException:
        print 'One or more of the requested stations is not valid. Valid stations:'
        station_problem = True

    if station_problem:
        for station in stations:
            print station
        sys.exit(0)

    runs = dpt.runs_to(arv)

    if not runs:
        print 'There are no trains presently.'
        sys.exit(0)

    for run in runs:
        print run
