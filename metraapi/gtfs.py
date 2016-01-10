import os
import os.path
import threading
import zipfile
import csv


class MetraGTFS(object):
    STOP_DATA = None
    STOP_ID_INDEX = None

    LOAD_LOCK = threading.Lock()
    INDEX_LOCK = threading.Lock()

    DATA_SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GTFSData010916.zip')

    @classmethod
    def get_stop_id_index(cls):
        with cls.INDEX_LOCK:
            if cls.STOP_ID_INDEX is None:
                sii = {}
                for stop in cls.get_stop_data():
                    sii[stop['stop_id']] = stop
                cls.STOP_ID_INDEX = sii

        return cls.STOP_ID_INDEX

    @classmethod
    def get_stop_data(cls):
        with cls.LOAD_LOCK:
            if cls.STOP_DATA is None:
                stop_data = []

                gtfs_zip = zipfile.ZipFile(cls.DATA_SOURCE, mode='r')

                stops_fh = gtfs_zip.open('stops.txt', mode='r')

                for rec in csv.DictReader(stops_fh):
                    stop = dict([
                        (k.strip(), v.strip())
                        for (k, v)
                        in rec.items()
                    ])
                    stop['wheelchair_boarding'] = bool(int(stop['wheelchair_boarding']))
                    for k in ['stop_lat', 'stop_lon']:
                        stop[k] = float(stop[k])

                    stop_data.append(stop)
                cls.STOP_DATA = stop_data

        return cls.STOP_DATA

    @classmethod
    def get_stop(cls, stop_id):
        return cls.get_stop_id_index().get(stop_id)
