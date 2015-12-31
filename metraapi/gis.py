import os
import threading
import re
import itertools
import csv
import utility_funcs


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

    def __repr__(self):
        return '<Station name=%s>' % self.name


class Stations(object):
    STATION_DATA = None
    LOAD_LOCK = threading.Lock()
    DATA_SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MetraStations.csv')

    @classmethod
    def load_station_data(cls):
        with cls.LOAD_LOCK:
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

                yield Station(
                    name, shortname, lines, branch_id, station_id,
                    latitude, longitude, address, municipality,
                    bike_parking, fare_zone
                )

    @classmethod
    def get_station_data(cls):
        if cls.STATION_DATA is None:
            cls.STATION_DATA = [s for s in cls.load_station_data()]

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
    def find_station(cls, name):
        normalized_needle = cls.normalize_for_compare(name)
        needle_len = len(normalized_needle)

        ret = None
        min_metric = 10000

        for station in cls.get_station_data():
            normalized_name = cls.normalize_for_compare(station.name)
            haystack_len = len(normalized_name)
            smaller_len = min(needle_len, haystack_len)

            for permuted_normalized_needle in cls.permute_name(normalized_name):
                lcs = utility_funcs.longest_common_substring(permuted_normalized_needle, normalized_needle)
                lcs_len = len(lcs)

                # if the least common substring is significantly smaller than the
                # smaller string... then it can't be right
                if lcs_len < smaller_len * 0.8:
                    continue

                levenshtein_dist = utility_funcs.levenshtein(permuted_normalized_needle, normalized_needle)

                length_difference = abs(needle_len - haystack_len)

                metric = levenshtein_dist - lcs_len

                if metric < min_metric:
                    min_metric = metric
                    ret = station

        return ret
