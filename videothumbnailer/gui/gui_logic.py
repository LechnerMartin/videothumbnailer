from PyQt5 import QtCore, QtWidgets, QtGui

from videothumbnailer.datamodel.datatypes import Chapter, TimeContainer
from videothumbnailer.gui.ui_videothumbnailer import Ui_MainWindow
from videothumbnailer.logic.logic import ThumbnailerLogic
from videothumbnailer.player.player import MediaPlayer


class VideoThumbnailerGui(Ui_MainWindow):
    def __init__(self, window, logic):
        super(VideoThumbnailerGui, self).__init__()
        #Ui_MainWindow.__init__(self)
        self.setupUi(window)
        self.logic = logic

        self.timer = QtCore.QTimer()

        # make connections
        self.pushButtonTest.clicked.connect(self.statusChanged)

        self.pushButtonStop.clicked.connect(self.logic.stop)
        self.pushButtonPlayPause.clicked.connect(self.toggle_play_pause)
        self.pushButtonStep.clicked.connect(self.logic.step)
        self.pushButtonMark.clicked.connect(self.mark)

        self.pushButtonDeleteMark.clicked.connect(self.delete_mark)
        self.pushButtonClearMarks.clicked.connect(self.clear_marks)

        self.pushButtonSave.clicked.connect(self.save_preview_and_status)

        self.buttonAddChapter.clicked.connect(self.add_chapter)


        self.marksListWidget.currentItemChanged.connect(self.listClicked)
#       self.connect(self.listWidget, QtCore.SIGNAL("currentItemChanged (QListWidgetItem*,QListWidgetItem*)"), self.listClicked)

        self.marksTreeWidget.currentItemChanged.connect(self.treeClicked)

        self.sliderVideoPosition.sliderPressed.connect(self.timer.stop)
        self.sliderVideoPosition.valueChanged.connect(self.videosliderposition_changed)
        self.sliderVideoPosition.sliderReleased.connect(self.videosliderposition_final_reached)

        self.actionFileOpen.triggered.connect(self.load_file_action)
        self.actionOpen.triggered.connect(self.load_file_action)

        self.timer.setInterval(100)
        self.timer.timeout.connect(self.statusChanged)

        #self.ocvcap = cv2.VideoCapture(filename)
        #time.sleep (50.0 / 1000.0);

        #def addInputTextToListbox(self):
          #  txt = self.myTextInput.text()
      #  self.listWidget.addItem(txt)

    def callback_marks_changed(self):

        self.marksTreeWidget.clear()
        chapters = self.logic.get_chapters()

        for chap in chapters :
            if chap is None :
                chap = Chapter(TimeContainer(0),"Default", "")
            chap_qti = QtWidgets.QTreeWidgetItem()
            chap_qti.setText(0,str(chap.timestamp))
            chap_qti.setText(1,chap.title)
            chap_qti.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(chap.timestamp))
            chap_qti.setData(1, QtCore.Qt.UserRole, QtCore.QVariant(chap))
            self.marksTreeWidget.addTopLevelItem(chap_qti)
            chap_qti.setExpanded(True);

            marks = self.logic.get_marks_for_chapter(chap)
            for mark in marks:
                mark_qti = QtWidgets.QTreeWidgetItem(chap_qti)
                mark_qti.setText(0, str(mark))
                mark_qti.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(mark))

        current_tree_chapter = None
        current_time = self.logic.get_current_time()
        current_chapter = self.logic.get_current_chapter(current_time)
        it = QtWidgets.QTreeWidgetItemIterator(self.marksTreeWidget);
        while it.value():
            treechapter  = it.value()
            if current_chapter == treechapter.data(1, QtCore.Qt.UserRole):
                current_tree_chapter = treechapter
            it += 1
        self.marksTreeWidget.scrollToItem(current_tree_chapter, QtWidgets.QAbstractItemView.PositionAtTop)
        treechapter.setExpanded(True)

            #chap_qti.setExpanded(True);


    def callback_chapters_changed(self):
        self.callback_marks_changed()


    def get_videoframehandle(self):
        return self.videoFrame.winId()

    def add_chapter(self):
        title = self.lineEditChapterTitel.text()
        description = self.textEditChapterDescription.toPlainText()
        self.logic.add_chapter(Chapter(None, title, description))
        self.refresh_chapterview()



    def load_file_action(self):
        self.load_file()

    def load_file(self, filename=None):
        if filename is None:
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
            #dlg.setFilter("Audio files (*.mp3,*.wav,*.ogg,*.mp4)")
            #dlg.setFilter("Video files (*.mp4,*.avi,*.mpg,*.flv)")

            filenames = []
            if dlg.exec_():
                filenames = dlg.selectedFiles()

            if len(filenames) > 0:
                filename = filenames[0]

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

    def treeClicked(self, newitem, previtem):
        if newitem == None:
            return
        data = newitem.data(0, QtCore.Qt.UserRole)
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

        self.refresh_listview()
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

    def refresh_listview(self):
        self.marksListWidget.clear()
        marks = self.logic.get_marks()
        for mark in marks:
            text = "{} ({})".format(str(mark), mark.milliseconds)
            item = QtWidgets.QListWidgetItem(text, self.marksListWidget)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(mark))
        self.nrOfMarkedFrames.setText(str(len(marks)))

    def refresh_chapterview(self):
        chapters = self.logic.get_chapters()
        for chapter in chapters:
            text = "{} {}".format(str(chapter.timestamp), chapter.title)
            item = QtWidgets.QListWidgetItem(text, self.listChapters)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(chapter))




    def convert_cv2img_to_qimage(self, cvImg):
        if cvImg is None:
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