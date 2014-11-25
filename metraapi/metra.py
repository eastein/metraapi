import sys
import time
import requests
import json
from collections import OrderedDict
import datetime
import re

TIME_RE = re.compile('^([0-9]+):([0-9]+)(am|pm)$')


def parse_reltime(s, now):
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
        datetime.datetime(year=now.year, month=now.month, day=now.day, **kw),
        datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, **kw)
    ]

    potential_times.sort(cmp=lambda a, b: cmp(abs(a - now), abs(b - now)))
    return potential_times[0]


def max_datetime(a, b):
    return cmp_datetime_core(max, a, b)


def min_datetime(a, b):
    return cmp_datetime_core(min, a, b)


def cmp_datetime_core(f, a, b):
    if a is None and b is not None:
        return b
    elif a is not None and b is None:
        return a
    return f(a, b)


def parse_datetime(odd_time):
    unixtime = int(odd_time.strip('/Date()')) / 1000
    return datetime.datetime.fromtimestamp(unixtime)


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

    return [{'id': station['id'], 'name': station['name']} for station in stations.values()]


def get_arrival_times(line_id, origin_station_id, destination_station_id):
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
    result = requests.post('http://12.205.200.243/AJAXTrainTracker.svc/GetAcquityTrainData',
                           headers=headers, data=json.dumps(payload))

    d = result.json()['d']
    data = json.loads(d)

    def difference_greaterthan(a, b, hours):
        return abs(a - b) > datetime.timedelta(hours=hours)

    def build_arrival(now, train):
        r = {'estimated_dpt_time': parse_datetime(train['estimated_dpt_time']),
             'scheduled_dpt_time': parse_datetime(train['scheduled_dpt_time']),
             'dpt_station': train['dpt_station'],
             'train_num': int(train['train_num']),
             'state': train['RunState']}
        # if the train number is 0, it's not a valid prediction
        if r['train_num'] == 0:
            return
        # if the estimated time is way off from the request time, then it doesn't make sense either
        if difference_greaterthan(now, r['estimated_dpt_time'], 24):
            return
        return r

    now = parse_datetime(data['responseTime'])

    arrivals = []
    arrival_bytrain = {}
    for (k, v) in data.iteritems():
        if k.startswith('train'):
            a = build_arrival(now, v)
            if a is not None:
                arrivals.append(a)
                arrival_bytrain[a['train_num']] = a

    # FIXME this API only
    more_arrivals = requests.get('http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_train_data.json',
                                 params={'line': line.upper(), 'origin': origin_station_id, 'destination': destination_station_id})

    now = datetime.datetime.now()

    more_arrivals = more_arrivals.json()

    for (k, v) in more_arrivals.iteritems():
        if k.startswith('train'):
            if 'error' in v:
                continue

            train_num = int(v['train_num'])
            if train_num in arrival_bytrain:
                a = arrival_bytrain[train_num]
                a['gps'] = v['hasData']
                a['on_time'] = not v['hasDelay']
                a['en_route'] = not v['notDeparted']
                a['scheduled_dpt_time'] = min_datetime(
                    a.get('scheduled_dpt_time'), parse_reltime(v.get('scheduled_dpt_time'), now))
                a['estimated_dpt_time'] = min_datetime(
                    a.get('estimated_dpt_time'), parse_reltime(v.get('estimated_dpt_time'), now))
                a['scheduled_arv_time'] = min_datetime(
                    a.get('scheduled_arv_time'), parse_reltime(v.get('scheduled_arv_time'), now))
                a['estimated_arv_time'] = min_datetime(
                    a.get('estimated_arv_time'), parse_reltime(v.get('estimated_arv_time'), now))

    for a in arrivals:
        for k in ['gps', 'on_time', 'en_route', 'scheduled_dpt_time', 'estimated_dpt_time', 'scheduled_arv_time', 'estimated_arv_time']:
            a[k] = a.get(k)

    return arrivals

if __name__ == '__main__':
    try :
        line = sys.argv[1]
    except IndexError :
        lines = get_lines()
        for line in lines:
            print "%(id)s: %(name)s" % line
        sys.exit(0)

    try :
        dpt = sys.argv[2]
        arv = sys.argv[3]
    except IndexError :
        stations = get_stations_from_line(line)
        for station in stations:
            print "%(id)s: %(name)s" % station
        sys.exit(0)

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

    times = get_arrival_times(line, dpt, arv)

    if not times:
        print 'There are no trains presently.'
        sys.exit(0)

    for arrival in times:
        arrival['gps'] = LKUP[arrival['gps']]
        arrival['on_time'] = LKUP2[arrival['on_time']]
        arrival['en_route'] = LKUP2[arrival['en_route']]
        print "Train %(train_num)s DPT %(dpt_station)s %(estimated_dpt_time)s (sched %(scheduled_dpt_time)s).  ARV %(estimated_arv_time)s (sched %(scheduled_arv_time)s). GPS:%(gps)s, ONTIME:%(on_time)s. ENROUTE:%(en_route)s." % arrival
