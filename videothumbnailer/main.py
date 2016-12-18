import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..'))

from PyQt5 import QtCore, QtGui, QtWidgets

from videothumbnailer.gui.ui_videothumbnailer import Ui_MainWindow
from videothumbnailer.logic.logic import ThumbnailerLogic
from videothumbnailer.player.player import MediaPlayer, TimeContainer


# time.sleep(50.0/1000)

class VideoThumbnailerGui(Ui_MainWindow):
    def __init__(self, window):
        Ui_MainWindow.__init__(self)
        self.setupUi(window)
        self.timer = QtCore.QTimer()

        player = MediaPlayer()
        player.set_framehandle(self.videoFrame.winId())

        self.logic = ThumbnailerLogic(player)
        # make connections
        self.pushButtonTest.clicked.connect(self.statusChanged)

        self.pushButtonStop.clicked.connect(self.logic.stop)
        self.pushButtonPlayPause.clicked.connect(self.toggle_play_pause)
        self.pushButtonStep.clicked.connect(self.logic.step)
        self.pushButtonMark.clicked.connect(self.mark)

        self.pushButtonDeleteMark.clicked.connect(self.delete_mark)
        self.pushButtonClearMarks.clicked.connect(self.clear_marks)

        self.pushButtonSave.clicked.connect(self.save_preview_and_status)

        self.marksListWidget.currentItemChanged.connect(self.listClicked)
#       self.connect(self.listWidget, QtCore.SIGNAL("currentItemChanged (QListWidgetItem*,QListWidgetItem*)"), self.listClicked)

        self.sliderVideoPosition.sliderPressed.connect(self.timer.stop)
        self.sliderVideoPosition.valueChanged.connect(self.videosliderposition_changed)
        self.sliderVideoPosition.sliderReleased.connect(self.videosliderposition_final_reached)

        self.timer.setInterval(100)
        self.timer.timeout.connect(self.statusChanged)

        #self.ocvcap = cv2.VideoCapture(filename)
        #time.sleep (50.0 / 1000.0);

        #def addInputTextToListbox(self):
          #  txt = self.myTextInput.text()
      #  self.listWidget.addItem(txt)

    def load_file(self, filename=None):
        if filename is None:
#            options = QtWidgets.QFileDialog.Options()
 #           options |= QtWidgets.QFileDialog.DontUseNativeDialog
  #          fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Video Files (*.avi)", options=options)
   #         filename = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))
            return
        if not filename:
            return

        self.logic.load_media(filename)
        self.new_video_loaded()

        self.statusChanged()
        self.refresh_marks()
        self.timer.start()

    def toggle_play_pause(self):
        self.logic.toggle_play_pause()
        self.statusChanged()

    def save_preview_and_status(self):
        self.logic.export_jpg_image()
        self.logic.export_data()

    def closeEvent(self):
        self.logic.export_data()

    def videosliderposition_final_reached(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.logic.set_current_time(TimeContainer(millisecods))
        self.timer.start()

    def videosliderposition_changed(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.display_current_videotime(TimeContainer(millisecods))

    def listClicked(self, newitem, previtem):
        if newitem == None:
            return
        data = newitem.data(QtCore.Qt.UserRole)
        self.logic.jump_to(data)

    def mark(self):
        self.logic.mark_position()
        self.refresh_marks()

    def delete_mark(self):
        item = self.marksListWidget.currentItem()
        if item == None:
            return
        data = item.data(QtCore.Qt.UserRole)
        self.logic.delete_mark(data)
        self.refresh_marks()

    def clear_marks(self):
        self.logic.clear_marks()
        self.refresh_marks()


    def refresh_marks(self):
        model = self.logic.get_model()
        cvImg = self.logic.get_preview_image()

        self.refresh_listview(model)
        self.refresh_preview(cvImg, model)

    def refresh_preview(self, cvImg, model):
        xy = model.get_xy_size()
        self.labelImageGeometry.setText("{}x{}".format(xy.x, xy.y))

        qimage = self.convert_cv2img_to_qimage(cvImg)
        pixmap = self.get_scaled_pixmap_for_label(self.labelMontageArea, qimage)
        self.labelMontageArea.setPixmap(pixmap)

    def get_scaled_pixmap_for_label(self, preview_area, qimage):
        pixmap = QtGui.QPixmap(qimage)
        pixmap = pixmap.scaled(preview_area.width(), preview_area.height())
        return pixmap

    def refresh_listview(self, model):
        self.marksListWidget.clear()
        for mark in model:
            text = "{} ({})".format(str(mark), mark.milliseconds)
            item = QtWidgets.QListWidgetItem(text, self.marksListWidget)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(mark))
        self.nrOfMarkedFrames.setText(str(model.size()))

    def convert_cv2img_to_qimage(self, cvImg):
        if cvImg == None:
            return QtGui.QImage()

        height, width, channel = cvImg.shape
        bytesPerLine = 3 * width
        qimage = QtGui.QImage(cvImg.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        return qimage

    def new_video_loaded(self):
        self.videoName.setText(self.logic.get_mediatitle())
        self.duration = self.logic.get_duration()
        self.videoDuration.setText(str(self.duration))
        self.sliderVideoPosition.setMaximum(self.duration.milliseconds)

    def statusChanged(self):
        current_time = self.logic.get_current_time()
        self.currentTimeMs.setText(str(current_time.milliseconds))
        self.currentTime.setText(str(current_time))
        self.sliderVideoPosition.setValue(current_time.milliseconds)

        if self.logic.is_paused:
            self.pushButtonPlayPause.setText("Play")
        else:
            self.pushButtonPlayPause.setText("Pause")
        if not self.logic.is_playing:
            self.pushButtonPlayPause.setText("Play")

    def display_current_videotime(self, timecontainer):
        self.currentTimeMs.setText(str(timecontainer.milliseconds))
        self.currentTime.setText(str(timecontainer))



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='videothumbnailer')
    parser.add_argument("-i", "--inputfile")
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    prog = VideoThumbnailerGui(main_window)
    prog.load_file(args.inputfile)
    #prog.load_file("/home/mlechner/private/iai/2013-09-24_RXX_Iai_Koho_Seigan_Nuki_Kacem_01.mp4")

    main_window.show()
    sys.exit(app.exec_())
