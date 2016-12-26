import unittest

from assertpy import assert_that

from videothumbnailer.datamodel.datatypes import Chapter, Xy


class ChapterTest(unittest.TestCase):
    def test_equality(self):
        assert_that(Chapter(123,"a", "b")).is_equal_to(Chapter(123,"a", "b"))

    def test_inequlity(self):
        assert_that(Chapter(123,"a", "b")).is_not_equal_to(Chapter(13,"a", "b"))
        assert_that(Chapter(123,"a", "b")).is_not_equal_to(Chapter(123,"x", "b"))
       # assert_that(Chapter(123,"a", "b")).is_not_equal_to(Chapter(123,"a", "x"))


class XyTest(unittest.TestCase):
    def test_equality(self):
        assert_that(Xy(1,2)).is_equal_to(Xy(1,2))

    def test_inequlity(self):
        assert_that(Xy(1,2)).is_not_equal_to(Xy(2,1))

    def test_compare_with_none(self):
        assert_that(Xy(1,2)).is_not_equal_to(None)