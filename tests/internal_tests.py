import unittest
import nose.exc
import metraapi.metra
import datetime
import metraapi.metraapi_internal


class TimeTests(unittest.TestCase):
    MORNING_LOCAL = metraapi.metraapi_internal.Internal.localize(datetime.datetime(2015, 4, 15, 8, 50, 18, 779317))
    EVENING_LOCAL = metraapi.metraapi_internal.Internal.localize(datetime.datetime(2015, 4, 15, 18, 50, 18, 779317))

    def test_reltime_1255am_tomorrow(self):
        expect_local = metraapi.metraapi_internal.Internal.localize(datetime.datetime(2015, 4, 16, 0, 55, 0, 0))
        self.assertEquals(metraapi.metraapi_internal.Internal.parse_reltime(self.EVENING_LOCAL, "12:55", 'am'), expect_local)
        self.assertEquals(metraapi.metraapi_internal.Internal.parse_reltime(self.MORNING_LOCAL, "12:55", 'am'), expect_local)

    def test_reltime_morning_train(self):
        expect_morning = metraapi.metraapi_internal.Internal.localize(datetime.datetime(2015, 4, 15, 10, 25, 0, 0))
        expect_evening = metraapi.metraapi_internal.Internal.localize(datetime.datetime(2015, 4, 16, 10, 25, 0, 0))
        self.assertEquals(metraapi.metraapi_internal.Internal.parse_reltime(self.EVENING_LOCAL, "10:25", 'am'), expect_evening)
        self.assertEquals(metraapi.metraapi_internal.Internal.parse_reltime(self.MORNING_LOCAL, "10:25", 'am'), expect_morning)
