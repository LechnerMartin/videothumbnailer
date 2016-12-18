import unittest
from unittest.mock import Mock

from assertpy import assert_that

from videothumbnailer.logic.logic import ThumbnailerLogic, DataModel, Xy, FileIo
from videothumbnailer.player.player import MediaPlayer, TimeContainer


class XyTest(unittest.TestCase):
    def test_equality(self):
        assert_that(Xy(1,2)).is_equal_to(Xy(1,2))

    def test_inequlity(self):
        assert_that(Xy(1,2)).is_not_equal_to(Xy(2,1))


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






class LogicTest(unittest.TestCase):
    """
    Get status: playing paused stopped no_media

    """
    def setUp(self):
        self.mock_player = Mock(spec = MediaPlayer )
        self.mock_fileio = Mock(spec = FileIo )
        self.mock_fileio.read_yaml = Mock(return_value=None)

        self.logic = ThumbnailerLogic(self.mock_player)
        self.logic.fileio = self.mock_fileio

    def test_initial_status(self):
        pass

    def test_mark(self):
        self.mock_player.get_current_time = Mock(return_value=TimeContainer(455))
        self.mock_player.get_screenshot = Mock(return_value="screenshot")
        self.logic.mark_position()
        model = self.logic.get_model()
        assert_that(model.size()).is_equal_to(1)
        assert_that(model.get_by_idx(0)).is_equal_to(TimeContainer(455))
        assert_that(model.get_images()).is_equal_to(["screenshot"])
        assert_that(self.mock_player.get_screenshot.assert_called_once_with(TimeContainer(455)))


    def test_delete_mark(self):
        self.mock_player.get_current_time = Mock(return_value=TimeContainer(455))
        self.logic.mark_position()
        marks = self.logic.get_model()
        self.logic.delete_mark(TimeContainer(455))
        assert_that(marks.size()).is_equal_to(0)


    def test_get_current_time(self):
        self.mock_player.get_current_time = Mock(return_value=TimeContainer(123))
        time = self.logic.get_current_time()
        assert_that(time.milliseconds).is_equal_to(123)

    def test_getTitle(self):
        self.mock_player.get_meta = Mock(return_value='Hello.avi')
        assert_that(self.logic.get_mediatitle()).is_equal_to("Hello.avi")
        assert_that(self.mock_player.get_meta.assert_called_once_with(0))

    def test_jump_to_location(self):
        self.logic.jump_to(TimeContainer(500))
        assert_that(self.mock_player.set_current_time.assert_called_once_with(TimeContainer(500)))


    def test_data_seraialisation_export(self):
        mediaurl = "/r/a/test.avi"
        self.logic.load_media(mediaurl)
        self.logic.datamodel.add_mark(TimeContainer(4567), None)

        self.logic.export_data()

        self.mock_fileio.write_yaml.assert_called_once_with(mediaurl, {"Mediaurl": mediaurl, "Marks": [4567]})

    def test_load_media(self):
        mediaurl = "/root/someuser/test.avi"
        self.logic.load_media(mediaurl)
        assert_that(self.logic.get_model().full_media_url).is_equal_to(mediaurl)

    def test_load_meda_including_data_serialisation_import_throw_no_error(self):
        self.mock_fileio.read_yaml = Mock(return_value={})
        self.logic.load_media("k")

    def test_load_meda_including_data_serialisation_import(self):
        mediaurl = "/r/test.avi"
        self.mock_fileio.read_yaml = Mock(return_value={"Mediaurl": mediaurl, "Marks": [4711]})

        self.logic.load_media(mediaurl)

        self.mock_fileio.read_yaml.assert_called_once_with(mediaurl)
        self.mock_player.get_screenshot.assert_called_once_with(TimeContainer(4711))
        assert_that(self.logic.datamodel.size()).is_equal_to(1)


    def test_generate_previewimage(self):
        import numpy as np
        image = np.ones((20,20,3), np.uint8)
        self.logic.datamodel.add_mark(TimeContainer(1), image)

        img = self.logic.get_preview_image()

        assert_that(img.size).is_equal_to(20*20*3)
        assert_that(img.all()).is_equal_to(image.all())

    def test_export_image(self):
        import numpy as np
        import cv2
        import os

        image1 = np.ones((20,20,3), np.uint8)
        image1[:] = (255,0,0)
#        image2 = np.ones((20,20,3), np.uint8)
#        image2[:] = (0,0,255)
        mediapath = os.getcwd() + "/output/test.avi"
        self.logic.datamodel.add_mark(TimeContainer(1), image1)

        self.logic.load_media(mediapath)
        img = self.logic.get_preview_image()
        assert_that(img.size).is_greater_than(10)

        self.logic.export_jpg_image()

        image = cv2.imread(mediapath +".jpg")
        assert_that(image).is_not_none()
        assert_that(image.size).is_equal_to(20*20*3)
        #assert_that(image.quality).is_equal_to(50)

        # extract to extra writer?
        # export, xy size
        # export filetype


