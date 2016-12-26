import unittest
from unittest.mock import Mock

from assertpy import assert_that


import sys
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, QtTest
from videothumbnailer.gui.gui_logic import VideoThumbnailerGui
from videothumbnailer.logic.logic import ThumbnailerLogic
from videothumbnailer.datamodel.datamodel import DataModel
from videothumbnailer.datamodel.datatypes import Chapter, TimeContainer
from videothumbnailer.player.player import MediaPlayer


app = QtWidgets.QApplication(sys.argv)


class GuiTest(unittest.TestCase):

    def setUp(self):
        self.main_window = QtWidgets.QMainWindow()
        self.logic_mock = Mock(spec=ThumbnailerLogic)
        self.model_mock = Mock(spec=DataModel)
        self.player_mock = Mock(spec=MediaPlayer)
        self.form = VideoThumbnailerGui(self.main_window, self.logic_mock)

        self.logic_mock.get_model = Mock(return_value=self.model_mock)
        self.form.logic = self.logic_mock
       # main_window.show()

    def test_default_states(self):
        assert_that(self.form.sliderVideoPosition.value()).is_equal_to(0)

    def test_play_pressed(self):
        self.form.sliderVideoPosition.setMaximum(1000)
        self.logic_mock.get_current_time = Mock(return_value=TimeContainer(455))
        self.logic_mock.is_paused = Mock(return_value=False)
        self.logic_mock.is_playing = Mock(return_value=False)

        QtTest.QTest.mouseClick(self.form.pushButtonPlayPause, QtCore.Qt.LeftButton)

        self.logic_mock.toggle_play_pause.assert_called_with()
        assert_that(self.form.sliderVideoPosition.value()).is_equal_to(455)

    def test_add_chapter_pressed(self):
        self.form.lineEditChapterTitel.setText("title")
        self.form.textEditChapterDescription.setText("text")
        self.model_mock.get_chapters = Mock(return_value=[])

        QtTest.QTest.mouseClick(self.form.buttonAddChapter, QtCore.Qt.LeftButton)

        self.logic_mock.add_chapter.assert_called_once_with(Chapter(None, "title", "text"))
        self.model_mock.get_chapters.assert_called_once_with()

    # Update chapter
    # Delete Chapter (Confirmation?)

    def test_display_chapter_information(self):
        self.model_mock.get_chapters = Mock(return_value=[Chapter(TimeContainer(2300), "ctitle", "descr")])
        self.logic_mock.get_model = Mock(return_value=self.model_mock)

        self.form.refresh_chapterview()

        assert_that(self.form.listChapters.item(0).text()).is_equal_to("00:00:02 ctitle")
        pass
