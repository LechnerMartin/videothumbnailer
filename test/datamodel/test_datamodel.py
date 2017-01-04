import unittest

from assertpy import assert_that

from videothumbnailer.datamodel.datamodel import DataModel
from videothumbnailer.datamodel.datatypes import Chapter, Xy, TimeContainer as TC


class DataModelTest(unittest.TestCase):
    def setUp(self):
        self.model = DataModel()
        self.defaultchapter = Chapter(TC(0), "Default", "")

    def test_inital_empty(self):
        assert_that(self.model.size()).is_equal_to(0)

    def test_set_media_url(self):
        mediaurl = "/root/someuser/test.avi"
        self.model.set_media_url(mediaurl)
        assert_that(self.model.full_media_url).is_equal_to(mediaurl)

    def test_add_mark(self):
        self.model.add_mark(TC(4567), "img")
        assert_that(self.model.size()).is_equal_to(1)
        assert_that(self.model.get_by_idx(0).milliseconds).is_equal_to(4567)
        assert_that(self.model.get_images()).is_equal_to(["img"])

    def test_add_mark_adds_images(self):
        image = "a"
        self.model.add_mark(TC(5767), image)
        assert_that(self.model.get_images()).is_equal_to(["a"])

    def test_add_mark_twice_is_ignored(self):
        self.model.add_mark(TC(4567), None)
        self.model.add_mark(TC(4567), None)
        assert_that(self.model.size()).is_equal_to(1)

    def test_add_mark_twice_is_not_ignored_if_image_was_not_there(self):
        self.model.add_mark(TC(4567), None)
        self.model.add_mark(TC(4567), "a")
        assert_that(self.model.size()).is_equal_to(1)
        assert_that(self.model.get_images()).is_equal_to(["a"])

    def test_delete_mark(self):
        self.model.add_mark(TC(4567), None)
        self.model.delete(TC(4567))
        assert_that(self.model.size()).is_equal_to(0)

    def test_delete_mark_not_workink_if_wrong_id(self):
        self.model.add_mark(TC(4567), None)
        self.model.delete(TC(4568))
        assert_that(self.model.size()).is_equal_to(1)

    def test_get_marks_sorted(self):
        self.model.add_mark(TC(4567), None)
        self.model.add_mark(TC(1234), "img2")
        assert_that(self.model.get_marks()).is_equal_to([TC(1234), TC(4567)])


    def test_get_marks_for_chapter(self):
        self.model.add_mark(TC(199), "img1")
        self.model.add_mark(TC(201), "img3")
        chapter = Chapter(TC(200), "","")
        self.model.add_chapter(chapter)
        marks = self.model.get_marks_for_chapter(chapter)
        assert_that(marks).is_equal_to([TC(201)])

    def test_get_marks_for_chapter_with_same_timestamp(self):
        self.model.add_mark(TC(200), "img2")
        self.model.add_mark(TC(201), "img3")
        chapter = Chapter(TC(200), "","")
        self.model.add_chapter(chapter)
        marks = self.model.get_marks_for_chapter(chapter)
        assert_that(marks).is_equal_to([TC(200), TC(201)])

    def test_get_marks_for_chapter_before_other(self):
        self.model.add_mark(TC(199), "img1")
        self.model.add_mark(TC(200), "img2")
        self.model.add_mark(TC(201), "img3")
        self.model.add_mark(TC(301), "img3")
        chapter = Chapter(TC(200), "","")
        self.model.add_chapter(chapter)
        self.model.add_chapter(Chapter(TC(300), "", ""))
        marks = self.model.get_marks_for_chapter(chapter)
        assert_that(marks).is_equal_to([TC(200), TC(201)])

    def test_get_marks_for_not_existing_chapter_returns_empty_list(self):
        assert_that(self.model.get_marks_for_chapter(Chapter(TC(1), "", ""))).is_equal_to([])

    def test_get_marks_for_empty_chapter_returns_empty_list(self):
        self.model.add_chapter(Chapter(TC(1), "", ""))
        assert_that(self.model.get_marks_for_chapter(Chapter(TC(1), "", ""))).is_equal_to([])

    def test_get_marks_for_None_chapter_returns_until_first_chapter(self):
        self.model.add_mark(TC(1), "img1")
        self.model.add_mark(TC(3), "img2")
        self.model.add_chapter(Chapter(TC(2), "", ""))
        assert_that(self.model.get_marks_for_chapter(None)).is_equal_to([TC(1)])


    def test_get_next_chapter(self):
        self.model.add_chapter(Chapter(TC(101),"",""))
        self.model.add_chapter(Chapter(TC(103),"",""))
        assert_that(self.model.get_next_chapter(TC(102))).is_equal_to(Chapter(TC(103), "", ""))

    def test_get_previous_chapter(self):
        self.model.add_chapter(Chapter(TC(101),"",""))
        self.model.add_chapter(Chapter(TC(103),"",""))
        assert_that(self.model.get_previous_chapter(TC(102))).is_equal_to(Chapter(TC(101), "", ""))


    def test_get_chapter_for_timestamp(self):
        self.model.add_chapter(Chapter(TC(101),"a","da"))
        self.model.add_chapter(Chapter(TC(103),"b","db"))
        assert_that(self.model.get_chapter_for_timestamp(TC(102))).is_equal_to(Chapter(TC(101), "a", "da"))
        assert_that(self.model.get_chapter_for_timestamp(TC(103))).is_equal_to(Chapter(TC(103), "b", "db"))
        assert_that(self.model.get_chapter_for_timestamp(TC(100))).is_equal_to(Chapter(TC(0), "Default", ""))

        # same timestamp - what is next /previous?

    def test_get_images_are_sorted(self):
        self.model.add_mark(TC(4567), "img1")
        self.model.add_mark(TC(1234), "img2")
        self.model.add_mark(TC(5678), "img3")
        assert_that(self.model.get_images()).is_equal_to(["img2", "img1", "img3"])

    def test_get_images_ignores_empty_images(self):
        image = "img"
        self.model.add_mark(TC(4567), None)
        self.model.add_mark(TC(1234), image)
        assert_that(self.model.get_images()).is_equal_to(["img"])


    def test_get_images_works_only_within_chapter(self):
        chapter = Chapter(TC(2),"","")
        self.model.add_mark(TC(1), "img1")
        self.model.add_chapter(chapter)
        self.model.add_mark(TC(5), "img2")
        self.model.add_mark(TC(7), "img3")
        assert_that(self.model.get_images(self.defaultchapter)).is_equal_to(["img1"])
        assert_that(self.model.get_images(chapter)).is_equal_to(["img2", "img3"])

    def test_add_chapter(self):
        chapter = Chapter(TC(123), "x", "y")
        self.model.add_chapter(chapter)
        assert_that(self.model.get_chapter(TC(123))).is_equal_to(chapter)


    def test_add_chapter_updates_chapter_at_timestamp(self):
        c = Chapter(TC(1024), "s", "t")
        cup = Chapter(TC(1024), "k", "v")
        self.model.add_chapter(c)
        assert_that(self.model.get_chapters()).is_equal_to([self.defaultchapter,c])
        self.model.add_chapter(cup)
        assert_that(self.model.get_chapters()).is_equal_to([self.defaultchapter,cup])



    def test_add_chapter_multiple_times_only_adds_once(self):
        c1 = Chapter(TC(1024), "s", "t")
        c2 = Chapter(TC(1024), "s", "t")
        self.model.add_chapter(c1)
        self.model.add_chapter(c1)
        self.model.add_chapter(c2)
        self.model.add_chapter(c2)

        assert_that(self.model.get_chapters()).is_length(2)
        assert_that(self.model.get_chapters()).is_equal_to([self.defaultchapter,c1])



    def test_get_chapter(self):
        assert_that(self.model.get_chapter(Chapter(None, "", ""))).is_equal_to(None)


    def test_get_chapters_empty_returns_default_chapter(self):
        assert_that(self.model.get_chapters()).is_equal_to([self.defaultchapter])


    def test_get_chapters(self):
        chapter = Chapter(TC(124), "s", "t")
        self.model.add_chapter(chapter)
        assert_that(self.model.get_chapters()).is_equal_to([self.defaultchapter,chapter])


    def test_get_chapters_is_sorted(self):
        c1 = Chapter(TC(1224), "s", "t")
        c2 = Chapter(TC(124), "s", "t")
        c3 = Chapter(TC(1024), "s", "t")
        self.model.add_chapter(c1)
        self.model.add_chapter(c2)
        self.model.add_chapter(c3)
        assert_that(self.model.get_chapters()).is_equal_to([self.defaultchapter,c2, c3, c1])


    def test_delete_chapter_with_same_timestamp(self):
        self.model.add_chapter(Chapter(TC(123),"", ""))
        self.model.delete_chapter(TC(123))
        assert_that(self.model.get_chapters()).is_length(1)


    def test_delete_chapter_works_not_if_timestamp_is_different(self):
        self.model.add_chapter(Chapter(TC(123),"", ""))
        self.model.delete_chapter(TC(124))
        assert_that(self.model.get_chapters()).is_length(2)

    def test_iterator(self):
        self.model.add_mark(TC(4567), None)
        result =[]
        for mark in self.model:
            result.append(mark)
        assert_that(result).is_equal_to([TC(4567)])

    def test_marks_are_sorted(self):
        self.model.add_mark(TC(4567), None)
        self.model.add_mark(TC(1567), None)
        assert_that(self.model.get_by_idx(0)).is_equal_to(TC(1567))

    def test_clear_marks(self):
        self.model.clear()
        assert_that(self.model.size()).is_equal_to(0)
        assert_that(self.model.get_images()).is_equal_to([])

    def test_autocalculate_frames_per_row_and_column_from_empty_marks(self):
        assert_that(self.model.get_xy_size(0)).is_equal_to(Xy(0, 0))

    def test_autocalculate_frames_per_row_and_column_from_marks(self):
        assert_that(self.model.get_xy_size(10)).is_equal_to(Xy(4, 3))

    def test_calculate_frames_per_row_and_column_with_x_speicfied(self):
        assert_that(self.model.get_xy_size(9, 5)).is_equal_to(Xy(5, 2))
        assert_that(self.model.get_xy_size(9, 1)).is_equal_to(Xy(1, 9))


