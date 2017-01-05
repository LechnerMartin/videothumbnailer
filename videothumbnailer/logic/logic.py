import cv2
import numpy as np
from io import BytesIO

from PIL import Image as PILImage
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch, mm, cm
#from reportlab.lib.utils import ImageReader
#from reportlab.pdfgen.pdfimages import PDFImage


from videothumbnailer.datamodel.datamodel import DataModel
from videothumbnailer.io.fileio import FileIo
from videothumbnailer.datamodel.datatypes import TimeContainer, Chapter
from videothumbnailer.logic.dataserializer import DataSerializer

class Callback:
    def callback_marks_changed(self):
        pass

    def callback_chapters_changed(self):
        pass

class ThumbnailerLogic:

    def __init__(self, player, callback=Callback()):
        self.player = player
        self.callback = callback
        self.datamodel = DataModel()
        self.serializer = DataSerializer()
        self.fileio = FileIo()
        self.is_playing = False
        self.is_paused = True


    def load_media(self, mediaurl):
        self.player.load_media(mediaurl)

        metadata = self.fileio.read_yaml(mediaurl)
        model = self.serializer.deserialize(metadata)
        model.set_media_url(mediaurl)

        self.datamodel = model
        for mark in model.get_marks():
            self.__mark_position_at_time(mark)

        self.callback.callback_marks_changed()


    def toggle_play_pause(self):
        if self.is_playing == False or self.is_paused == True:
            self.player.play()
            self.is_playing = True
            self.is_paused = False
        else:
            self.player.pause()
            self.is_paused = True

    def step(self):
        self.player.step()
        self.is_paused = True

    def stop(self):
        self.player.stop()
        self.is_playing = False
        self.is_paused = False

    def get_mediatitle(self):
        return self.player.get_meta(0)

    def get_duration(self):
        return self.player.get_duration()

    def get_current_time(self):
        return self.player.get_current_time()

    def get_current_chapter(self, timecontainer):
        return self.datamodel.get_chapter_for_timestamp(timecontainer)

    def set_current_time(self, timecontainer):
        self.player.set_current_time(timecontainer)

    def mark_position(self):
        time = self.player.get_current_time()
        self.__mark_position_at_time(time)
        self.callback.callback_marks_changed()

    def __mark_position_at_time(self, time):
        image = self.player.get_screenshot(time)
        self.datamodel.add_mark(time, image)

    def get_marks(self):
        return self.datamodel.get_marks()

    def get_marks_for_chapter(self, chapter):
        return self.datamodel.get_marks_for_chapter(chapter)

    def get_model(self):
        return self.datamodel

    def delete_mark(self, timecontainer):
        self.datamodel.delete(timecontainer)
        self.callback.callback_marks_changed()

    def clear_marks(self):
        self.datamodel.clear()

    def jump_to(self, timecontainer):
        self.player.set_current_time(timecontainer)

    def export_data(self):
        url = self.datamodel.full_media_url
        data = self.serializer.serialize(self.datamodel)
        self.fileio.write_yaml(url, data)

    def add_chapter(self, chapter):
        if chapter.timestamp is None:
            time = self.player.get_current_time()
            chapter.timestamp = time
        self.datamodel.add_chapter(chapter)
        self.callback.callback_chapters_changed()

    def get_chapters(self):
        return self.datamodel.get_chapters()

    def delete_chapter(self, timestamp):
        self.datamodel.delete_chapter(timestamp)
        self.callback.callback_chapters_changed()


    def get_preview_image(self, timestamp = TimeContainer(0)):
        chapter = self.datamodel.get_chapter_for_timestamp(timestamp)
        images = self.datamodel.get_images(chapter)
        imagecount = len(images)
        if imagecount < 1:
            return None

        geometry = np.shape(images[0])
        blank_image = np.zeros(geometry, np.uint8)
        blank_image[:,:,:] = 255
        xy = self.datamodel.get_xy_size(imagecount)
        nr_of_matrixcells = xy.x * xy.y

        while len(images) < nr_of_matrixcells:
            images.append(blank_image)

        img = None
        for i in range(xy.y):
            hrow = np.hstack((images[i*xy.x:(i+1)*xy.x]))
            if img is None:
                img = hrow
            else:
                img = np.vstack((img, hrow))

        return img

    def export_jpg_images(self):
        basefilename = self.datamodel.full_media_url

        for chapter in self.datamodel.get_chapters():
            timestamp = chapter.timestamp
            img = self.get_preview_image(timestamp)
            if img is None:
                continue

            filename = "{}.{}.jpg".format(basefilename, timestamp.milliseconds)
            cv2.imwrite(filename, img, [cv2.IMWRITE_JPEG_QUALITY,35])

        #cv2.imwrite(filename, img)

        # blank_image = np.ones((20,20,3), np.uint8)
        # blank_image[:] = (255,0,0)
        # filled_image = np.ones((20,20,3), np.uint8)
        # filled_image[:] = (0,0,255)
        #
        # hrow0 = np.hstack((blank_image,filled_image,blank_image,filled_image,blank_image,filled_image))
        # hrow1 = np.hstack((filled_image,blank_image,filled_image,blank_image,filled_image,blank_image))
        # img = np.vstack((hrow0, hrow1))
        # for i in range(2):
        #    img = np.vstack((img, img))
        # return img

    def export_pdf(self):
        filename = self.datamodel.full_media_url + ".pdf"
        pdf = SimpleDocTemplate(filename)
        pdfcontent = []
        styles = getSampleStyleSheet()
        pdfcontent.append(Paragraph(self.get_mediatitle(), styles["Title"]))

        for chapter in self.datamodel.get_chapters():
            self.__add_chapter_to_pdf(chapter, pdfcontent)
            pdfcontent.append(Spacer(1, 12))
        pdf.build(pdfcontent)

    def __add_chapter_to_pdf(self, chapter, pdfcontent):
        timestamp = chapter.timestamp
        styles = getSampleStyleSheet()
        title = "{}\t{}".format(chapter.title, timestamp)
        description = chapter.description.replace('\n','<br />\n')
        pdfcontent.append(Paragraph(title, styles["Heading2"]))
        pdfcontent.append(Paragraph(description, styles["Normal"]))
        img = self.get_preview_image(timestamp)
        if img is not None:
            img1 = self.create_pdf_image(img)
            pdfcontent.append(Image(img1, width=18*cm,height=25*cm,kind='proportional'))

    def create_pdf_image(self, img):
        file = BytesIO()
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        image = PILImage.fromarray(img)
        image.save(file, 'jpeg')
        file.name = 'test.jpg'
        file.seek(0)
        return file

