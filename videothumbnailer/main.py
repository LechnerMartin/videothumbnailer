import os
import sys

from videothumbnailer.gui.gui_logic import VideoThumbnailerGui
from videothumbnailer.player.player import MediaPlayer
from videothumbnailer.logic.logic import ThumbnailerLogic

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from PyQt5 import QtWidgets

# time.sleep(50.0/1000)


def connect_app():
    player = MediaPlayer()
    logic = ThumbnailerLogic(player)

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    prog = VideoThumbnailerGui(main_window, logic)
    player.set_framehandle(prog.get_videoframehandle())

    prog.load_file(args.inputfile)
    #prog.load_file("/home/mlechner/private/iai/2013-09-24_RXX_Iai_Koho_Seigan_Nuki_Kacem_01.mp4")

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='videothumbnailer')
    parser.add_argument("-i", "--inputfile")
    args = parser.parse_args()

    connect_app()
