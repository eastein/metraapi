import datetime
import pytz
import metraapi.metra
import unittest
import nose.exc


class ArrivalTests(unittest.TestCase):

    def test_1ad(self):
        raise nose.exc.SkipTest("This test is incomplete, it has no assertions.")

        acquity_data = {u'requestTime': u'/Date(-62135575200000)/',
                        u'responseTime': u'/Date(1425401841199)/',
                        u'train1': {u'DateAge': 0,
                                        u'RunState': 0,
                                        u'dpt_station': u'OTC',
                                        u'estimated_dpt_time': u'/Date(-2208967200000)/',
                                        u'is_duplicate': False,
                                        u'is_modified': False,
                                        u'scheduled_dpt_time': u'/Date(-2208967200000)/',
                                        u'timestamp': u'/Date(1425401841199)/',
                                        u'train_num': u'0000'},
                        u'train2': {u'DateAge': 0,
                                    u'RunState': 0,
                                    u'dpt_station': u'OTC',
                                    u'estimated_dpt_time': u'/Date(-2208967200000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(-2208967200000)/',
                                    u'timestamp': u'/Date(1425401841199)/',
                                    u'train_num': u'0000'},
                        u'train3': {u'DateAge': 0,
                                    u'RunState': 0,
                                    u'dpt_station': u'OTC',
                                    u'estimated_dpt_time': u'/Date(-2208967200000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(-2208967200000)/',
                                    u'timestamp': u'/Date(1425401841199)/',
                                    u'train_num': u'0000'}}

        gtd_data = {u'arrivalStopName': u'Ravenswood',
                    u'departureStopName': u'Chicago OTC',
                    u'train1': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'am',
                                u'schDepartInTheAM': u'am',
                                u'scheduled_arv_time': u'11:48',
                                u'scheduled_arv_time_note': u'11:48',
                                u'scheduled_dpt_time': u'11:35',
                                u'scheduled_dpt_time_note': u'11:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'323',
                                u'trip_id': u'UP-N_UN323_V1_AA'},
                    u'train10': {u'bikesText': u'',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'05:34',
                                 u'scheduled_arv_time_note': u'05:34',
                                 u'scheduled_dpt_time': u'05:21',
                                 u'scheduled_dpt_time_note': u'05:21',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'347',
                                 u'trip_id': u'UP-N_UN347_V1_AA'},
                    u'train11': {u'bikesText': u'',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'05:49',
                                 u'scheduled_arv_time_note': u'05:49',
                                 u'scheduled_dpt_time': u'05:35',
                                 u'scheduled_dpt_time_note': u'05:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'349',
                                 u'trip_id': u'UP-N_UN349_V1_AA'},
                    u'train12': {u'bikesText': u'',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'06:04',
                                 u'scheduled_arv_time_note': u'06:04',
                                 u'scheduled_dpt_time': u'05:50',
                                 u'scheduled_dpt_time_note': u'05:50',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'353',
                                 u'trip_id': u'UP-N_UN353_V1_AA'},
                    u'train13': {u'bikesText': u'',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'06:13',
                                 u'scheduled_arv_time_note': u'06:13',
                                 u'scheduled_dpt_time': u'06:00',
                                 u'scheduled_dpt_time_note': u'06:00',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'355',
                                 u'trip_id': u'UP-N_UN355_V1_AA'},
                    u'train14': {u'bikesText': u'',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'06:57',
                                 u'scheduled_arv_time_note': u'06:57',
                                 u'scheduled_dpt_time': u'06:44',
                                 u'scheduled_dpt_time_note': u'06:44',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'359',
                                 u'trip_id': u'UP-N_UN359_V1_AA'},
                    u'train15': {u'bikesText': u'Yes',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'07:48',
                                 u'scheduled_arv_time_note': u'07:48',
                                 u'scheduled_dpt_time': u'07:35',
                                 u'scheduled_dpt_time_note': u'07:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'361',
                                 u'trip_id': u'UP-N_UN361_V1_AA'},
                    u'train16': {u'bikesText': u'Yes',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'08:48',
                                 u'scheduled_arv_time_note': u'08:48',
                                 u'scheduled_dpt_time': u'08:35',
                                 u'scheduled_dpt_time_note': u'08:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'363',
                                 u'trip_id': u'UP-N_UN363_V1_AA'},
                    u'train17': {u'bikesText': u'Yes',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'09:48',
                                 u'scheduled_arv_time_note': u'09:48',
                                 u'scheduled_dpt_time': u'09:35',
                                 u'scheduled_dpt_time_note': u'09:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'365',
                                 u'trip_id': u'UP-N_UN365_V1_AA'},
                    u'train18': {u'bikesText': u'Yes',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'10:48',
                                 u'scheduled_arv_time_note': u'10:48',
                                 u'scheduled_dpt_time': u'10:35',
                                 u'scheduled_dpt_time_note': u'10:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'367',
                                 u'trip_id': u'UP-N_UN367_V1_AA'},
                    u'train19': {u'bikesText': u'Yes',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'pm',
                                 u'schDepartInTheAM': u'pm',
                                 u'scheduled_arv_time': u'11:48',
                                 u'scheduled_arv_time_note': u'11:48',
                                 u'scheduled_dpt_time': u'11:35',
                                 u'scheduled_dpt_time_note': u'11:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'369',
                                 u'trip_id': u'UP-N_UN369_V1_AA'},
                    u'train2': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'12:48',
                                u'scheduled_arv_time_note': u'12:48',
                                u'scheduled_dpt_time': u'12:35',
                                u'scheduled_dpt_time_note': u'12:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'325',
                                u'trip_id': u'UP-N_UN325_V1_AA'},
                    u'train20': {u'bikesText': u'Yes',
                                 u'hasData': False,
                                 u'hasDelay': False,
                                 u'isRed': False,
                                 u'notDeparted': True,
                                 u'schArriveInTheAM': u'am',
                                 u'schDepartInTheAM': u'am',
                                 u'scheduled_arv_time': u'12:48',
                                 u'scheduled_arv_time_note': u'12:48',
                                 u'scheduled_dpt_time': u'12:35',
                                 u'scheduled_dpt_time_note': u'12:35',
                                 u'selected': False,
                                 u'shouldHaveData': True,
                                 u'status': 1,
                                 u'timestamp': u'10:57:21am',
                                 u'train_num': u'301',
                                 u'trip_id': u'UP-N_UN301_V1_AA'},
                    u'train3': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'01:48',
                                u'scheduled_arv_time_note': u'01:48',
                                u'scheduled_dpt_time': u'01:35',
                                u'scheduled_dpt_time_note': u'01:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'327',
                                u'trip_id': u'UP-N_UN327_V1_AA'},
                    u'train4': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'02:48',
                                u'scheduled_arv_time_note': u'02:48',
                                u'scheduled_dpt_time': u'02:35',
                                u'scheduled_dpt_time_note': u'02:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'329',
                                u'trip_id': u'UP-N_UN329_V1_AA'},
                    u'train5': {u'bikesText': u'',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'03:33',
                                u'scheduled_arv_time_note': u'03:33',
                                u'scheduled_dpt_time': u'03:20',
                                u'scheduled_dpt_time_note': u'03:20',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'331',
                                u'trip_id': u'UP-N_UN331_V1_AA'},
                    u'train6': {u'bikesText': u'',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'03:45',
                                u'scheduled_arv_time_note': u'03:45',
                                u'scheduled_dpt_time': u'03:32',
                                u'scheduled_dpt_time_note': u'03:32',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'333',
                                u'trip_id': u'UP-N_UN333_V1_AA'},
                    u'train7': {u'bikesText': u'',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'04:48',
                                u'scheduled_arv_time_note': u'04:48',
                                u'scheduled_dpt_time': u'04:35',
                                u'scheduled_dpt_time_note': u'04:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'339',
                                u'trip_id': u'UP-N_UN339_V1_AA'},
                    u'train8': {u'bikesText': u'',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'05:15',
                                u'scheduled_arv_time_note': u'05:15',
                                u'scheduled_dpt_time': u'05:03',
                                u'scheduled_dpt_time_note': u'05:03',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'341',
                                u'trip_id': u'UP-N_UN341_V1_AA'},
                    u'train9': {u'bikesText': u'',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'05:27',
                                u'scheduled_arv_time_note': u'05:27',
                                u'scheduled_dpt_time': u'05:13',
                                u'scheduled_dpt_time_note': u'05:13',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'10:57:21am',
                                u'train_num': u'345',
                                u'trip_id': u'UP-N_UN345_V1_AA'}}

    def test_ravenswood_to_otc_evening(self):
        acquity_data = {u'requestTime': u'/Date(-62135575200000)/',
                        u'responseTime': u'/Date(1425689047282)/',
                        u'train1': {u'DateAge': 0,
                                    u'RunState': 1,
                                    u'dpt_station': u'RAVENSWOOD',
                                    u'estimated_dpt_time': u'/Date(1425690840000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(1425690720000)/',
                                    u'timestamp': u'/Date(1425689047266)/',
                                    u'train_num': u'356'},
                        u'train2': {u'DateAge': 0,
                                    u'RunState': 2,
                                    u'dpt_station': u'RAVENSWOOD',
                                    u'estimated_dpt_time': u'/Date(1425694200000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(1425694200000)/',
                                    u'timestamp': u'/Date(1425689047266)/',
                                    u'train_num': u'358'},
                        u'train3': {u'DateAge': 0,
                                    u'RunState': 0,
                                    u'dpt_station': u'RAVENSWOOD',
                                    u'estimated_dpt_time': u'/Date(1425697800000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(1425697800000)/',
                                    u'timestamp': u'/Date(1425689047266)/',
                                    u'train_num': u'KX60'}}

        gtd_data = {u'arrivalStopName': u'Chicago OTC',
                    u'departureStopName': u'Ravenswood',
                    u'train1': {u'bikesText': u'Yes',
                                u'estArriveInTheAM': u'pm',
                                u'estDepartInTheAM': u'pm',
                                u'estimated_arv_time': u'07:32',
                                u'estimated_arv_time_note': u'07:32 ',
                                u'estimated_dpt_time': u'07:14',
                                u'estimated_dpt_time_note': u'07:14 ',
                                u'hasData': True,
                                u'hasDelay': True,
                                u'isRed': False,
                                u'notDeparted': False,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'07:30',
                                u'scheduled_arv_time_note': u'07:30',
                                u'scheduled_dpt_time': u'07:12',
                                u'scheduled_dpt_time_note': u'07:12',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'356',
                                u'trip_id': u'UP-N_UN356_V1_B'},
                    u'train2': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'08:25',
                                u'scheduled_arv_time_note': u'08:25',
                                u'scheduled_dpt_time': u'08:10',
                                u'scheduled_dpt_time_note': u'08:10',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'358',
                                u'trip_id': u'UP-N_UN358_V1_B'},
                    u'train3': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'09:25',
                                u'scheduled_arv_time_note': u'09:25',
                                u'scheduled_dpt_time': u'09:10',
                                u'scheduled_dpt_time_note': u'09:10',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'KX60',
                                u'trip_id': u'UP-N_UN360_V1_B'},
                    u'train4': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'10:30',
                                u'scheduled_arv_time_note': u'10:30',
                                u'scheduled_dpt_time': u'10:15',
                                u'scheduled_dpt_time_note': u'10:15',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'362',
                                u'trip_id': u'UP-N_UN362_V1_B'},
                    u'train5': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'10:55',
                                u'scheduled_arv_time_note': u'10:55',
                                u'scheduled_dpt_time': u'10:40',
                                u'scheduled_dpt_time_note': u'10:40',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'364',
                                u'trip_id': u'UP-N_UN364_V1_B'},
                    u'train6': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'11:55',
                                u'scheduled_arv_time_note': u'11:55',
                                u'scheduled_dpt_time': u'11:40',
                                u'scheduled_dpt_time_note': u'11:40',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'366',
                                u'trip_id': u'UP-N_UN366_V1_B'},
                    u'train7': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'am',
                                u'schDepartInTheAM': u'am',
                                u'scheduled_arv_time': u'01:10',
                                u'scheduled_arv_time_note': u'01:10',
                                u'scheduled_dpt_time': u'12:55',
                                u'scheduled_dpt_time_note': u'12:55',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'06:44:07pm',
                                u'train_num': u'368',
                                u'trip_id': u'UP-N_UN368_V1_B'}}

        arrivals = metraapi.metra.get_arrival_times(
            'UP-N', 'RAVENSWOOD', 'OTC', acquity_data=acquity_data, gtd_data=gtd_data)
        self.assertGreaterEqual(len(arrivals), 3)

        train_356 = filter(lambda a: a['train_num'] == 356, arrivals)[0]
        train_358 = filter(lambda a: a['train_num'] == 358, arrivals)[0]
        train_360 = filter(lambda a: a['train_num'] == 360, arrivals)[0]

        self.assertTrue(train_356['gps'])
        self.assertEquals(train_356['train_num'], 356)
        self.assertFalse(train_358['gps'])

        # TODO make this test more thorough
        sch_arv_time_0 = train_360['scheduled_arv_time']

        self.assertEquals(sch_arv_time_0.year, 2015)
        self.assertEquals(sch_arv_time_0.month, 3)
        self.assertEquals(sch_arv_time_0.day, 6)
        self.assertEquals(sch_arv_time_0.hour, 21)
        self.assertEquals(sch_arv_time_0.minute, 25)

    def test_acquity_data_0trains_degraded_behaviour(self):
        acquity_data = {u'requestTime': u'/Date(-62135575200000)/',
                        u'responseTime': u'/Date(1428975468376)/',
                        u'train1': {u'DateAge': 0,
                                    u'RunState': 0,
                                    u'dpt_station': u'OTC',
                                    u'estimated_dpt_time': u'/Date(-2208967200000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(-2208967200000)/',
                                    u'timestamp': u'/Date(1428975468376)/',
                                    u'train_num': u'0000'},
                        u'train2': {u'DateAge': 0,
                                    u'RunState': 0,
                                    u'dpt_station': u'OTC',
                                    u'estimated_dpt_time': u'/Date(-2208967200000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(-2208967200000)/',
                                    u'timestamp': u'/Date(1428975468376)/',
                                    u'train_num': u'0000'},
                        u'train3': {u'DateAge': 0,
                                    u'RunState': 0,
                                    u'dpt_station': u'OTC',
                                    u'estimated_dpt_time': u'/Date(-2208967200000)/',
                                    u'is_duplicate': False,
                                    u'is_modified': False,
                                    u'scheduled_dpt_time': u'/Date(-2208967200000)/',
                                    u'timestamp': u'/Date(1428975468376)/',
                                    u'train_num': u'0000'}}
        gtd_data = {u'arrivalStopName': u'Ravenswood',
                    u'departureStopName': u'Chicago OTC',
                    u'train1': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'09:48',
                                u'scheduled_arv_time_note': u'09:48',
                                u'scheduled_dpt_time': u'09:35',
                                u'scheduled_dpt_time_note': u'09:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'08:37:48pm',
                                u'train_num': u'365',
                                u'trip_id': u'UP-N_UN365_V1_F'},
                    u'train2': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'10:48',
                                u'scheduled_arv_time_note': u'10:48',
                                u'scheduled_dpt_time': u'10:35',
                                u'scheduled_dpt_time_note': u'10:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'08:37:48pm',
                                u'train_num': u'367',
                                u'trip_id': u'UP-N_UN367_V1_F'},
                    u'train3': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'pm',
                                u'schDepartInTheAM': u'pm',
                                u'scheduled_arv_time': u'11:48',
                                u'scheduled_arv_time_note': u'11:48',
                                u'scheduled_dpt_time': u'11:35',
                                u'scheduled_dpt_time_note': u'11:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'08:37:48pm',
                                u'train_num': u'369',
                                u'trip_id': u'UP-N_UN369_V1_F'},
                    u'train4': {u'bikesText': u'Yes',
                                u'hasData': False,
                                u'hasDelay': False,
                                u'isRed': False,
                                u'notDeparted': True,
                                u'schArriveInTheAM': u'am',
                                u'schDepartInTheAM': u'am',
                                u'scheduled_arv_time': u'12:48',
                                u'scheduled_arv_time_note': u'12:48',
                                u'scheduled_dpt_time': u'12:35',
                                u'scheduled_dpt_time_note': u'12:35',
                                u'selected': False,
                                u'shouldHaveData': True,
                                u'status': 1,
                                u'timestamp': u'08:37:48pm',
                                u'train_num': u'301',
                                u'trip_id': u'UP-N_UN301_V1_F'}}
        now = datetime.datetime(2015, 4, 13, 20, 37, 48, tzinfo=pytz.timezone('US/Central'))
        arrivals = metraapi.metra.get_arrival_times(
            'UP-N', 'OTC', 'RAVENSWOOD', acquity_data=acquity_data, gtd_data=gtd_data)

        self.assertEquals(len(arrivals), 4)
