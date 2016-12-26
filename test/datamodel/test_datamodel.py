import unittest

from assertpy import assert_that

from videothumbnailer.datamodel.datamodel import DataModel
from videothumbnailer.datamodel.datatypes import Chapter, Xy, TimeContainer
from videothumbnailer.player.player import TimeContainer


class DataModelTest(unittest.TestCase):
    def setUp(self):
        self.model = DataModel()
        self.model.add_mark(TimeContainer(4567), None)

    def test_inital_empty(self):
        assert_that(DataModel().size()).is_equal_to(0)

    def test_set_media_url(self):
        mediaurl = "/root/someuser/test.avi"
        self.model.set_media_url(mediaurl)

        assert_that(self.model.full_media_url).is_equal_to(mediaurl)

    def test_add_marks(self):
        assert_that(self.model.size()).is_equal_to(1)
        assert_that(self.model.get_by_idx(0).milliseconds).is_equal_to(4567)
        assert_that(self.model.get_images()).is_equal_to([None])

    def test_add_adds_images(self):
        image = "a"
        self.model.add_mark(TimeContainer(5767), image)

        assert_that(self.model.get_images()).is_equal_to([None,"a"])

    def test_images_are_sorted(self):
        blank_image = "b"
        filled_image = "f"
        self.model.add_mark(TimeContainer(1234), filled_image)
        self.model.add_mark(TimeContainer(5678), blank_image)
        assert_that(self.model.get_images()).is_equal_to(["f", None, "b"])

    def test_add_marks_twice_is_ignored(self):
        self.model.add_mark(TimeContainer(4567), None)
        assert_that(self.model.size()).is_equal_to(1)

    def test_add_marks_twice_is_not_ignored_if_image_was_not_there(self):
        self.model.add_mark(TimeContainer(4567), "a")
        assert_that(self.model.size()).is_equal_to(1)
        assert_that(self.model.get_images()).is_equal_to(["a"])

    def test_delete_mark(self):
        self.model.delete(TimeContainer(4567))
        assert_that(self.model.size()).is_equal_to(0)

    def test_delete_mark_not_workink_if_wrong_id(self):
        self.model.delete(TimeContainer(4568))
        assert_that(self.model.size()).is_equal_to(1)

    def test_get_chapter(self):
        assert_that(self.model.get_chapter(Chapter(None, "", ""))).is_equal_to(None)

    def test_get_chapters_empty(self):
        assert_that(self.model.get_chapters()).is_equal_to([])

    def test_get_chapters(self):
        chapter = Chapter(TimeContainer(124), "s", "t")
        self.model.add_chapter(chapter)
        assert_that(self.model.get_chapters()).is_equal_to([chapter])

    def test_add_chapter(self):
        chapter = Chapter(TimeContainer(123), "x", "y")
        self.model.add_chapter(chapter)
        assert_that(self.model.get_chapter(TimeContainer(123))).is_equal_to(chapter)

    def test_iterator(self):
        result =[]
        for mark in self.model:
            result.append(mark)
        assert_that(result).is_equal_to([TimeContainer(4567)])

    def test_marks_are_sorted(self):
        self.model.add_mark(TimeContainer(1567), None)
        assert_that(self.model.get_by_idx(0)).is_equal_to(TimeContainer(1567))

    def test_clear_marks(self):
        self.model.clear()
        assert_that(self.model.size()).is_equal_to(0)
        assert_that(self.model.get_images()).is_equal_to([])

    def test_autocalculate_frames_per_row_and_column_from_empty_marks(self):
        marks = DataModel()
        assert_that(marks.size()).is_equal_to(0)
        assert_that(marks.get_xy_size()).is_equal_to(Xy(0, 0))

    def test_autocalculate_frames_per_row_and_column_from_marks(self):
        marks = self.get_filled_marks(10)
        assert_that(marks.size()).is_equal_to(10)
        assert_that(marks.get_xy_size()).is_equal_to(Xy(4, 3))

    def test_calculate_frames_per_row_and_column_with_x_speicfied(self):
        marks = self.get_filled_marks(9)
        assert_that(marks.size()).is_equal_to(9)
        assert_that(marks.get_xy_size(5)).is_equal_to(Xy(5, 2))
        assert_that(marks.get_xy_size(1)).is_equal_to(Xy(1, 9))


    def get_filled_marks(self, count):
        marks = DataModel()
        for i in range(count):
            marks.add_mark(TimeContainer(i), None)
        return marks