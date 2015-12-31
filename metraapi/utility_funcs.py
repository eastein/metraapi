from __future__ import absolute_import
from __future__ import unicode_literals

import re
import math

# By Magnus Hetland (http://hetland.org/), props!


def levenshtein(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


# naive implementation of LCS
def longest_common_substring(a, b):
    l = 0
    ss = ''
    for a_s in range(len(a)):
        for a_l in range(len(a) - a_s + 1):
            ss_ = a[a_s:a_s + a_l]
            if ss_ in b and len(ss_) > l:
                l = len(ss_)
                ss = ss_
    return ss


# Haversine formula example in Python
# Author: Wayne Dyck
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def points_wkt(wkt):
    point_string = re.match('^multipoint[ ]*\((.*)\)$', wkt.strip().lower()).groups()[0]
    if point_string is not None:
        return [
            (float(lat), float(lon))
            for
            (lon, lat)
            in [
                pointset.split(' ')
                for pointset
                in point_string.split(',')
            ]

        ]
    return points


def point_wkt(wkt):
    points = points_wkt(wkt)
    if not points:
        return None

    lat_sum = 0.0
    lon_sum = 0.0
    for lat, lon in points:
        lat_sum += lat
        lon_sum += lon

    point_count = len(points)

    return (
        lat_sum / point_count,
        lon_sum / point_count
    )
