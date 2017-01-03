import unittest
from unittest.mock import Mock
from assertpy import assert_that

import vlc


from videothumbnailer.datamodel.datatypes import TimeContainer as TC
from videothumbnailer.player.player import MediaPlayer

class PlayerTest(unittest.TestCase):

    def setUp(self):
        #self.vlc = vlc.Instance()
        #self.vlcp self.instance.media_player_new()
        #self.ocvcap = None

        self.vlc_mock = Mock(spec=vlc.MediaPlayer)
        self.player = MediaPlayer()
        self.player.player = self.vlc_mock

    def test_set_current_time_called_with_none_should_just_return(self):
        self.player.set_current_time(None)
        self.vlc_mock.set_time.assert_not_called()