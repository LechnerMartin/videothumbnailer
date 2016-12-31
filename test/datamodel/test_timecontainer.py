import unittest

from assertpy import assert_that
from videothumbnailer.datamodel.datatypes import TimeContainer as TC


class TimeContainerTest(unittest.TestCase):
    """
    - not settable
    - add position ?
    - Make: total, current, percent?

    """

    TEST_TIME_MS = (22*3600 +23 *60 +44)*1000 +123 #32:23:44.123

    def test_milliseconds_can_be_returned(self):
        time = TC(123456789)
        assert_that(time.milliseconds).is_equal_to(123456789)

    def test_milliseonds_to_time(self):
        time = TC(self.TEST_TIME_MS)
        assert_that(time.strftime("%H:%M:%S.%f")).is_equal_to("22:23:44.123000")

    def test_tostring(self):
        time = TC(self.TEST_TIME_MS)
        assert_that(str(time)).is_equal_to("22:23:44")

    def test_that_negative_time_is_changed_to_zero_time(self):
        time = TC(-1)
        assert_that(time.strftime("%H:%M:%S")).is_equal_to("00:00:00")

    def test_equals(self):
        assert_that(TC(56789)).is_equal_to(TC(56789))
        assert_that(TC(2) == TC(2)).is_true()

    def test_comparison(self):
        assert_that(TC(2) > TC(1)).is_true()
        assert_that(TC(5) < TC(6)).is_true()
        assert_that(TC(7) >= TC(6)).is_true()
        assert_that(TC(-1) >= TC(-6)).is_true()