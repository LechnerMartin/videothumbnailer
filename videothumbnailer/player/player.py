import sys
import vlc
import datetime
import cv2


class TimeContainer:

    def __init__(self, milliseconds):
        if milliseconds < 0:
            milliseconds = 0
        self.milliseconds = milliseconds
        self.__datetime = datetime.datetime.utcfromtimestamp(milliseconds/1000.0)

    def strftime(self, formatstring):
        return self.__datetime.strftime(formatstring)

    def __str__(self):
        return self.__datetime.strftime("%H:%M:%S")

    def __eq__(self, other):
        return self.milliseconds == other.milliseconds

    def __hash__(self):
        return hash(self.milliseconds)

class MediaPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.ocvcap = None
        # i=vlc.Instance('--no-audio', '--fullscreen')
        # i.audio_get_volume()

    def set_framehandle(self, win_id):
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.player.set_xwindow(win_id)
        elif sys.platform == "win32":  # for Windows
            self.player.set_hwnd(win_id)
        elif sys.platform == "darwin":  # for MacOS
            self.player.set_nsobject(win_id)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def step(self):
        self.player.next_frame()

    def stop(self):
        self.player.stop()

    def get_meta(self, idx):
        # self.media.parse()
        return self.media.get_meta(idx)

    def get_duration(self):
        duration = self.media.get_duration()
        return TimeContainer(duration)

    def get_current_time(self):
        time = self.player.get_time()
        return TimeContainer(time)

    def set_current_time(self, timecontainer):
        self.player.set_time(timecontainer.milliseconds - 10)

    def load_media(self, mediaurl):
        self.media = self.instance.media_new(mediaurl)
        self.media.parse()
        self.player.set_media(self.media)
        self.ocvcap = cv2.VideoCapture(mediaurl)


    def get_screenshot(self, time):
        self.ocvcap.set(cv2.CAP_PROP_POS_MSEC,time.milliseconds)
        ret,frame = self.ocvcap.read()
        return frame
