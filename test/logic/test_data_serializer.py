import unittest
from unittest.mock import Mock

from assertpy import assert_that

from videothumbnailer.datamodel.datatypes import Chapter, TimeContainer as TC
from videothumbnailer.io.fileio import FileIo
from videothumbnailer.logic.dataserializer import DataSerializer
from videothumbnailer.datamodel.datamodel import DataModel

class DataSerializerTest(unittest.TestCase):
    def setUp(self):
        self.model = DataModel()
        self.mediaurl = "/r/test.avi"


    def test_serialize_empty_model(self):
        model = DataModel()
        serializer = DataSerializer()
        expected = {}

        #assert_that(serializer.serialize(model)).is_equal_to(expected)

    def test_serialize(self):
        self.model.add_mark(TC(4567), None)
        self.model.add_chapter(Chapter(TC(1567),"t1", "d1"))
        serializer = DataSerializer()

        expected = {"Marks": [4567],
                    "Chapters": [
                        {"Timestamp": 0, "Title" : "Default", "Description" : ""},
                        {"Timestamp": 1567, "Title" : "t1", "Description" : "d1"}
                    ]}

        assert_that(serializer.serialize(self.model)).is_equal_to(expected)


    def test_deserialize(self):
        serializer = DataSerializer()
        data = { "Marks": [4567, 1234],
            "Chapters": [
                {"Timestamp": 0, "Title" : "Default", "Description" : ""},
                {"Timestamp": 1567, "Title" : "t1", "Description" : "d1"}
            ]}

        model = serializer.deserialize(data)

        assert_that(model.size()).is_equal_to(2)
        assert_that(model.get_marks()).is_equal_to([TC(1234), TC(4567)])
        assert_that(model.get_chapters()).is_length(2)
        assert_that(model.get_chapters()).is_equal_to(
            [Chapter(TC(0), "Default", ""), Chapter(TC(1567),"t1","d1")])


    def test_deserialize_missing_information(self):
        serializer = DataSerializer()
        data = {}

        self.model = serializer.deserialize(data)

        assert_that(self.model.size()).is_equal_to(0)
        assert_that(self.model.get_chapters()).is_length(1)
        assert_that(self.model.get_chapters()).is_equal_to(
            [Chapter(TC(0), "Default", "")])
