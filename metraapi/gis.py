import os
import threading
import re
import itertools
import csv
import metraapi.utility_funcs as utility_funcs


class Station(object):

    def __init__(self, name, shortname, lines, branch_id, station_id, latitude, longitude, address, municipality, bike_parking, fare_zone):
        self.name = name
        self.shortname = shortname
        self.lines = lines
        self.branch_id = branch_id
        self.station_id = station_id

        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.municipality = municipality

        self.bike_parking = bike_parking
        self.fare_zone = fare_zone

        self._normalized_name = None
        self._permuted_normalized_name = None

    @property
    def permuted_normalized_name(self):
        if self._permuted_normalized_name is None:
            self._permuted_normalized_name = Stations.permute_name(self.normalized_name)
        return self._permuted_normalized_name

    @property
    def normalized_name(self):
        if self._normalized_name is None:
            self._normalized_name = Stations.normalize_for_compare(self.name)
        return self._normalized_name

    def __repr__(self):
        return '<Station name=%s>' % self.name


class Stations(object):
    STATION_DATA = None
    LINE_NAME_INDEX = None

    LOAD_LOCK = threading.Lock()
    INDEX_LOCK = threading.Lock()
    DATA_SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MetraStations.csv')

    @classmethod
    def get_line_name_index(cls):
        with cls.INDEX_LOCK:
            if cls.LINE_NAME_INDEX is None:
                lni = {}
                for station in cls.get_station_data():
                    for line in station.lines:
                        lni.setdefault(line, dict())
                        lni[line][station.normalized_name] = station
                cls.LINE_NAME_INDEX = lni

        return cls.LINE_NAME_INDEX

    @classmethod
    def get_station_data(cls):
        with cls.LOAD_LOCK:
            if cls.STATION_DATA is None:
                station_data = []

                reader = csv.DictReader(open(cls.DATA_SOURCE))

                for row in reader:
                    name = row['LONGNAME']
                    shortname = row['NAME']

                    text_lines = row['LINES'].strip()
                    if text_lines:
                        lines = [line.strip() for line in text_lines.split(',')]
                    else:
                        lines = []
                    branch_id = int(row['BRANCH_ID'])
                    station_id = int(float(row['STATION_ID']))

                    lat_lon = utility_funcs.point_wkt(row['WKT'])
                    if lat_lon:
                        latitude, longitude = lat_lon
                    else:
                        latitude, longitude = (0, 0)

                    address = row['ADDRESS']
                    municipality = row['MUNICIPALI']

                    bike_parking = int(row['BIKEPKNG'])
                    fare_zone = row['FAREZONE']

                    station_object = Station(
                        name, shortname, lines, branch_id, station_id,
                        latitude, longitude, address, municipality,
                        bike_parking, fare_zone
                    )

                    station_data.append(station_object)

                cls.STATION_DATA = station_data

        return cls.STATION_DATA

    @classmethod
    def expand_abbreviation(cls, token):
        return {
            'st': 'street',
            'rd': 'road',
            'ave': 'avenue',
            'pk': 'park',
        }.get(token, token)

    @classmethod
    def normalize_for_compare(cls, s):
        chunks = re.sub('[^a-z0-9]+', ' ', s.lower()).strip().split(' ')
        return ' '.join([
            cls.expand_abbreviation(chunk)
            for chunk
            in chunks
        ])

    @classmethod
    def permute_name(cls, name):
        return [
            ' '.join(name_chunks)
            for name_chunks in
            itertools.permutations(name.split(' '))
        ]

    @classmethod
    def geographic_test(cls, station_object, geographic_filter):
        if geographic_filter is None:
            return None, True

        dist = utility_funcs.distance((station_object.latitude, station_object.longitude),
                                      (geographic_filter['latitude'], geographic_filter['longitude']))

        acceptable = dist <= geographic_filter['distance_km']

        return dist, acceptable

    @classmethod
    def find_station(cls, name, geographic_filter=None):
        normalized_needle = cls.normalize_for_compare(name)

        matches = []
        for line, station_idx in cls.get_line_name_index().items():
            # TODO linefilter: don't inspect stations from other lines.
            # right now we are checking all lines because it's not a parameter
            # and we haven't normalized between the GIS line names and the ones from the API
            station_obj = station_idx.get(normalized_needle)
            if station_obj is not None:
                matches.append(station_obj)

        if len(matches) == 1:
            if cls.geographic_test(matches[0], geographic_filter):
                return matches[0]

        needle_len = len(normalized_needle)

        ret = None
        min_metric = None

        for station in cls.get_station_data():
            geographic_metric, geographically_acceptable = cls.geographic_test(station, geographic_filter)
            # if out of distance range, Abort.
            if not geographically_acceptable:
                continue

            # TODO linefilter: don't inspect stations from other lines. There are situations like Lake Forest where
            # the same name is used on multiple lines for separate stations.

            normalized_name = station.normalized_name
            haystack_len = len(normalized_name)
            smaller_len = min(needle_len, haystack_len)

            for permuted_normalized_haystack in station.permuted_normalized_name:
                if geographic_filter is None:
                    # here, if no geographic filter is specified the best we can do is an perfect match
                    if permuted_normalized_haystack == normalized_needle:
                        return station

                lcs = utility_funcs.longest_common_substring(permuted_normalized_haystack, normalized_needle)
                lcs_len = len(lcs)

                # if the least common substring is significantly smaller than the
                # smaller string... then it can't be right
                if lcs_len < smaller_len * 0.25:
                    continue

                levenshtein_dist = utility_funcs.levenshtein(permuted_normalized_haystack, normalized_needle)

                length_difference = abs(needle_len - haystack_len)

                metric = levenshtein_dist - lcs_len + geographic_metric

                if min_metric is None or metric < min_metric:
                    min_metric = metric
                    #print 'new minimum metric: %0.7f for station %s' % (min_metric, station.name)
                    ret = station

        return ret
