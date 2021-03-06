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

        #self.centralwidget = QtWidgets.QWidget(MainWindow)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctr+S"), window, self.save_file_action)
        QtWidgets.QShortcut(QtGui.QKeySequence("F4"), window, self.toggle_play_pause)

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
        self.buttonDeleteChapter.clicked.connect(self.delete_chapter)
        self.buttonUpdateChapter.clicked.connect(self.update_chapter)
        self.buttonMoveChapter.clicked.connect(self.move_chapter)

        self.buttonSkipForwardLarge.clicked.connect(self.skip_forward_large)
        self.buttonSkipForwardSmall.clicked.connect(self.skip_forward_small)
        self.buttonSkipBackwardLarge.clicked.connect(self.skip_backward_large)
        self.buttonSkipBackwardSmall.clicked.connect(self.skip_backward_small)
        self.largeskip = 15000
        self.smallskip = 5000


#        self.marksListWidget.currentItemChanged.connect(self.listClicked)
#       self.connect(self.listWidget, QtCore.SIGNAL("currentItemChanged (QListWidgetItem*,QListWidgetItem*)"), self.listClicked)

        self.marksTreeWidget.currentItemChanged.connect(self.treeClicked)

        self.sliderVideoPosition.sliderPressed.connect(self.timer.stop)
        self.sliderVideoPosition.valueChanged.connect(self.videosliderposition_changed)
        self.sliderVideoPosition.sliderReleased.connect(self.videosliderposition_final_reached)

        self.actionFileOpen.triggered.connect(self.load_file_action)
        self.actionOpen.triggered.connect(self.load_file_action)
        self.actionFileSave.triggered.connect(self.save_file_action)

        self.timer.setInterval(100)
        self.timer.timeout.connect(self.statusChanged)

        self.current_chapter = Chapter(TimeContainer(0), "Default", "")

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
            chap_qti.setData(0, QtCore.Qt.UserRole, QtCore.QVariant(chap.timestamp))
            chap_qti.setText(1,chap.title)
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
        self.current_chapter = current_chapter
        #chap_qti.setExpanded(True);
        self.nrOfMarkedFrames.setText(str(self.logic.get_model().size()))
        self.__refresh_preview(current_time)


    def callback_chapters_changed(self):
        self.callback_marks_changed()


    def get_videoframehandle(self):
        return self.videoFrame.winId()


    def add_chapter(self):
        chapter = self.__get_chapter_from_chapterview(None)
        self.logic.add_chapter(chapter)


    def delete_chapter(self):
        self.logic.delete_chapter(self.current_chapter.timestamp)


    def update_chapter(self):
        chap = self.__get_chapter_from_chapterview(self.current_chapter.timestamp)
        self.logic.add_chapter(chap)


    def move_chapter(self):
        chap = self.current_chapter
        self.logic.delete_chapter(chap.timestamp)
        chap.timestamp = self.logic.get_current_time()
        self.logic.add_chapter(chap)


    def load_file_action(self):
        self.load_file()


    def save_file_action(self):
        time = QtCore.QDateTime.currentDateTime().toString()
        self.savetimeLbl.setText(time)
        self.logic.export_data()


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
        self.timer.start()

    def toggle_play_pause(self):
        self.logic.toggle_play_pause()
        self.statusChanged()

    def save_preview_and_status(self):
        self.logic.export_jpg_images()
        self.logic.export_pdf()

    def skip_forward_large(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.logic.set_current_time(TimeContainer(millisecods + self.largeskip))

    def skip_forward_small(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.logic.set_current_time(TimeContainer(millisecods + self.smallskip))

    def skip_backward_large(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.logic.set_current_time(TimeContainer(millisecods - self.largeskip))

    def skip_backward_small(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.logic.set_current_time(TimeContainer(millisecods - self.smallskip))




    def closeEvent(self):
        self.logic.export_data()

    def videosliderposition_final_reached(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.logic.set_current_time(TimeContainer(millisecods))
        self.timer.start()

    def videosliderposition_changed(self):
        millisecods = self.sliderVideoPosition.sliderPosition()
        self.display_current_videotime(TimeContainer(millisecods))


    def treeClicked(self, newitem, previtem):
        if newitem is None:
            return
        timestamp = newitem.data(0, QtCore.Qt.UserRole)
        if timestamp is None:
            return
        self.logic.jump_to(timestamp)
        self.__refreshChapterView(timestamp)

    def __refreshChapterView(self, timestamp):
        chapter = self.logic.get_current_chapter(timestamp)
        if chapter is None:
            return
        chap = self.__get_chapter_from_chapterview(self.current_chapter.timestamp)

        if chap != self.current_chapter:
            self.logic.add_chapter(chap)
        self.current_chapter = chapter
        self.__set_chapterview_from_chapter(chapter)
        self.__refresh_preview(chapter.timestamp)

    def __set_chapterview_from_chapter(self, chapter):
        self.lineEditChapterTitel.setText(chapter.title)
        self.textEditChapterDescription.setPlainText(chapter.description)

    def __get_chapter_from_chapterview(self, timestamp):
        title = self.lineEditChapterTitel.text()
        description = self.textEditChapterDescription.toPlainText()
        return Chapter(timestamp, title, description)



    def mark(self):
        self.logic.mark_position()

    def delete_mark(self):
        item = self.marksTreeWidget.currentItem()
        if item == None:
            return
        data = item.data(0, QtCore.Qt.UserRole)
        self.logic.delete_mark(data)


    def clear_marks(self):
        self.logic.clear_marks()


    def __refresh_preview(self, timestamp):
        model = self.logic.get_model()
        cvImg = self.logic.get_preview_image(timestamp)

        self.nrOfMarkedFrames.setText(str(model.size()))
        xy = model.get_xy_size(10)
        self.labelImageGeometry.setText("{}x{}".format(xy.x, xy.y))

        qimage = self.convert_cv2img_to_qimage(cvImg)
        pixmap = self.get_scaled_pixmap_for_label(self.labelMontageArea, qimage)
        self.labelMontageArea.setPixmap(pixmap)

    def get_scaled_pixmap_for_label(self, preview_area, qimage):
        pixmap = QtGui.QPixmap(qimage)
        pixmap = pixmap.scaled(preview_area.width(), preview_area.height())
        return pixmap

    def refresh_chapterview(self):
        self.listChapters.clear()
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