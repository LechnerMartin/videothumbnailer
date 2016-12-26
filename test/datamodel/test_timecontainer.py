import unittest

from assertpy import assert_that
from videothumbnailer.datamodel.datatypes import TimeContainer


class TimeContainerTest(unittest.TestCase):
    """
    - not settable
    - add position ?
    - Make: total, current, percent?

    """

    TEST_TIME_MS = (22*3600 +23 *60 +44)*1000 +123 #32:23:44.123

    def test_milliseconds_can_be_returned(self):
        time = TimeContainer(123456789)
        assert_that(time.milliseconds).is_equal_to(123456789)

    def test_milliseonds_to_time(self):
        time = TimeContainer(self.TEST_TIME_MS)
        assert_that(time.strftime("%H:%M:%S.%f")).is_equal_to("22:23:44.123000")

    def test_tostring(self):
        time = TimeContainer(self.TEST_TIME_MS)
        assert_that(str(time)).is_equal_to("22:23:44")

    def test_that_negative_time_is_changed_to_zero_time(self):
        time = TimeContainer(-1)
        assert_that(time.strftime("%H:%M:%S")).is_equal_to("00:00:00")

    def test_equals(self):
        assert_that(TimeContainer(56789)).is_equal_to(TimeContainer(56789))

