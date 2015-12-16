from __future__ import absolute_import
from __future__ import print_function
import datetime
import json
import re
from pytz import timezone, utc
from collections import OrderedDict
import six

TIME_RE = re.compile('^([0-9]+):([0-9]+)(am|pm)$')


class Internal(object):
    CHICAGOTIME = timezone('US/Central')

    @classmethod
    def localize(cls, dt):
        return cls.CHICAGOTIME.localize(dt)

    @classmethod
    def parse_reltime(cls, now, s, ampm):
        if s is None:
            return None

        # print 'parsing: %s, %s, %s' % (now, s, ampm)

        m = TIME_RE.match(s)
        if not m:
            if ampm is not None:
                m = TIME_RE.match(s + ampm)
                if not m:
                    # print '%s was not right... not even with ampm' % s
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
        hour_ago = now - datetime.timedelta(hours=1)

        potential_times = [
            dt for dt in [
                cls.localize(datetime.datetime(year=now.year, month=now.month, day=now.day, **kw)),
                cls.localize(datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, **kw))
            ]
            if dt > hour_ago
        ]

        chosen_time = None
        chosen_diff = None

        for potential_time in potential_times:
            diff = abs(potential_time - now)
            if chosen_diff is None:
                chosen_diff = diff
                chosen_time = potential_time
            elif diff < chosen_diff:
                chosen_diff = diff
                chosen_time = potential_time

        return chosen_time

    @classmethod
    def parse_train_number(cls, train_num):
        """
        :param train_num: string, train number from metra rail or acquity endpoint.
        :return: integer train number
        """

        # one time I observed that KX65 showed online, but 365 showed in the
        # station screens. What... but that is what it is.

        return int(train_num.replace('KX', '3'))

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
        elif a is None and b is None:
            return None
        return f(a, b)

    @classmethod
    def parse_datetime(cls, odd_time):
        # The time is coming back from Metra in UTC. Treat it as such and then convert it to Chicago local time
        unixtime = int(odd_time.strip('/Date()')) / 1000
        return utc.localize(datetime.datetime.utcfromtimestamp(unixtime)).astimezone(cls.CHICAGOTIME)


def get_acquity_request_parameters(line_id, origin_station_id, destination_station_id):
    return {
        'headers': {
            'Content-Type': 'application/json; charset=UTF-8'
        },
        'payload': json.dumps({
            "stationRequest": {
                "Corridor": line_id,
                "Destination": destination_station_id,
                "Origin": origin_station_id
            }
        }),
        'url': 'http://12.205.200.243/AJAXTrainTracker.svc/GetAcquityTrainData'
    }


def get_gtd_request_parameters(line_id, origin_station_id, destination_station_id):
    return {
        'query': {
            'line': line_id.upper(),
            'origin': origin_station_id,
            'destination': destination_station_id
        },
        'url': 'http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_train_data.json',
    }


def get_stations_request_parameters(line_id):
    return {
        'url': 'http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_stations_from_line.json',
        'query': {
            'trackerNumber': 0,
            'trainLineId': line_id
        }
    }


def get_lines_request_parameters():
    return {
        'url': 'http://goroo.com/getRealTimeMetraRoutes.htm',
        'query': {
        }
    }


def interpret_stations_response(lines_data):
    if not isinstance(lines_data, six.text_type):
        lines_data = lines_data.decode('utf8')

    stations = json.loads(lines_data, object_pairs_hook=OrderedDict)['stations']

    return [{'id': station['id'], 'name': station['name'].strip()} for station in list(stations.values())]


def interpret_arrival_times(line_id, origin_station_id, destination_station_id, verbose=False, acquity_data=None, gtd_data=None):
    """
    :param acquity_data: the parsed JSON from the acquity train data endpoint
    :param gtd_data: the parsed JSON from the get_train_data endpoint
    :returns: list of arrivals
    """

    now = Internal.parse_datetime(acquity_data['responseTime'])
    if now.year < 2014:
        # in this case, the acquity endpoint is breaking and lying about when now is. It claims to
        # be in the year 1900.
        now = Internal.localize(datetime.datetime.utcnow())

    if verbose:
        print('now = %s' % repr(now))

    def difference_greaterthan(a, b, hours):
        return abs(a - b) > datetime.timedelta(hours=hours)

    def build_arrival(now, train):
        r = {'estimated_dpt_time': Internal.parse_datetime(train['estimated_dpt_time']),
             'scheduled_dpt_time': Internal.parse_datetime(train['scheduled_dpt_time']),
             'as_of': now,
             'dpt_station': train['dpt_station'],
             'train_num': Internal.parse_train_number(train['train_num']),
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
    for (k, v) in six.iteritems(acquity_data):
        if k.startswith('train'):
            a = build_arrival(now, v)
            if a is not None:
                arrivals.append(a)
                arrival_bytrain[a['train_num']] = a

    for (k, v) in six.iteritems(gtd_data):
        if k.startswith('train'):
            if 'error' in v:
                continue

            # see above also
            train_num = Internal.parse_train_number(v['train_num'])

            if train_num not in arrival_bytrain:
                arrival_bytrain[train_num] = {
                    'train_num': train_num,
                    'as_of': now,
                }

            a = arrival_bytrain[train_num]
            a['gps'] = v['hasData']
            a['on_time'] = not v['hasDelay']
            a['en_route'] = not v['notDeparted']

            a['scheduled_dpt_time'] = Internal.min_datetime(
                a.get('scheduled_dpt_time'),
                Internal.parse_reltime(
                    now,
                    v.get('scheduled_dpt_time'),
                    v.get('schDepartInTheAM')
                )
            )
            a['estimated_dpt_time'] = Internal.min_datetime(
                a.get('estimated_dpt_time'),
                Internal.parse_reltime(
                    now,
                    v.get('estimated_dpt_time'),
                    v.get('estDepartInTheAM')
                )
            )

            a['scheduled_arv_time'] = Internal.max_datetime(
                a.get('scheduled_arv_time'),
                Internal.parse_reltime(
                    now,
                    v.get('scheduled_arv_time'),
                    v.get('schArriveInTheAM')
                )
            )
            a['estimated_arv_time'] = Internal.max_datetime(
                a.get('estimated_arv_time'),
                Internal.parse_reltime(
                    now,
                    v.get('estimated_arv_time'),
                    v.get('estArriveInTheAM')
                )
            )

    return_arrivals = []

    for train_num, a in list(arrival_bytrain.items()):
        for k in ['gps', 'on_time', 'en_route', 'scheduled_dpt_time', 'estimated_dpt_time', 'scheduled_arv_time', 'estimated_arv_time']:
            a[k] = a.get(k)
        return_arrivals.append(a)

    return return_arrivals


def interpret_lines_response(lines_data):
    lines = json.loads(lines_data)

    twitters = {
        'BNSF': 'MetraBNSF',
        'HC':   'MetraHC',
        'ME':   'MetraMED',
        'MD-N': 'MetraMDN',
        'MD-W': 'MetraMDW',
        'NCS': 'MetraNCS',
        'RI': 'MetraRID',
        'SWS': 'metraSWS',
        'UP-N': 'MetraUPN',
        'UP-NW': 'MetraUPNW',
        'UP-W':  'MetraUPW',
    }

    def shorten_line_name(text):
        remove_start = 'Metra'
        remove_end = 'Line'

        if text.endswith(remove_end):
            text = text[:-len(remove_end)]

        words_left = len([s for s in text.split(' ') if s])

        # only strip off the "Metra" if there are at least 3 words.
        if words_left > 2 and text.startswith(remove_start):
            text = text[len(remove_start):]

        return text.strip()

    return [
        {
            'id': line['id'],
            'name': shorten_line_name(line['text']),
            'twitter': twitters.get(line['id'])
        }
        for line in lines
    ]
