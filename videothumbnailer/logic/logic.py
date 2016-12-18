import cv2
import numpy as np
from videothumbnailer.player.player import TimeContainer
import yaml
from pathlib import Path

class FileIo:
    def write_yaml(self, filenamewithoutextension, data):
        text = yaml.dump(data)
        with open(filenamewithoutextension + ".yml", "w") as f : f.write(text)

    def read_yaml(self, filenamewithoutextension):
        filename = filenamewithoutextension + ".yml"
        file = Path(filename)
        if not file.is_file():
            return None

        with open(filename, "r") as f : text = f.read()
        return yaml.safe_load(text)

class Xy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: {}, y: {}".format(self.x, self.y)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

class DataModel:
    def __init__(self):
        self.__marks = []
        self.__images = {}
        self.full_media_url = ""

    def set_media_url(self, media_url):
        self.full_media_url = media_url

    def size(self):
        return len(self.__marks)

    def add_mark(self, timecontainer, image):
        if timecontainer not in self.__marks:
            self.__marks.append(timecontainer)
            self.__marks.sort(key=lambda x: x.milliseconds)
        if timecontainer not in self.__images.keys() or self.__images[timecontainer] == None:
            self.__images[timecontainer] = image

    def get_by_idx(self, idx):
        return self.__marks[idx]

    def delete(self, timecontainer):
        if timecontainer in self.__marks:
            self.__marks.remove(timecontainer)

    def clear(self):
        self.__marks.clear()
        self.__images.clear()

    def get_xy_size(self, columns = 0):
        framecount = len(self.__marks)
        if columns == 0:
            columns = int(np.ceil(np.sqrt(framecount)))
        rows = 0 if columns == 0 else int(np.ceil(framecount/columns))
        return Xy(columns, rows)

    def get_images(self):
        result = []
        for mark in self.__marks:
            result.append(self.__images[mark])
        return result

    def __getitem__(self, index):
        return self.__marks[index]


class ThumbnailerLogic:

    def __init__(self, player):
        self.player = player
        self.datamodel = DataModel()
        self.is_playing = False
        self.is_paused = True
        self.fileio = FileIo()

    def load_media(self, mediaurl):
        self.datamodel.set_media_url(mediaurl)
        self.player.load_media(mediaurl)

        metadata = self.fileio.read_yaml(mediaurl)

        if metadata is not None:
            for key in ["Mediaurl", "Marks"] :
                if key not in metadata.keys():
                    return
            self.datamodel.full_media_url = metadata["Mediaurl"]
            marks = metadata["Marks"]
            for mark in marks:
                self.__mark_position_at_time(TimeContainer(mark))


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

    def set_current_time(self, timecontainer):
        self.player.set_current_time(timecontainer)

    def mark_position(self):
        time = self.player.get_current_time()
        self.__mark_position_at_time(time)

    def __mark_position_at_time(self, time):
        image = self.player.get_screenshot(time)
        self.datamodel.add_mark(time, image)

    def get_model(self):
        return self.datamodel

    def delete_mark(self, timecontainer):
        self.datamodel.delete(timecontainer)

    def clear_marks(self):
        self.datamodel.clear()

    def jump_to(self, timecontainer):
        self.player.set_current_time(timecontainer)

    def export_data(self):
        url = self.datamodel.full_media_url

        marks = [m.milliseconds for m in self.datamodel]
        data = {"Mediaurl": url, "Marks": marks }
        self.fileio.write_yaml(url, data)
       #marklist = [m.milliseconds for m in self.__marks]

       #{"Mediaurl": self.full_media_url, "Marks": marklist}


    def get_preview_image(self):
        images = self.datamodel.get_images()
        if len(images) < 1:
            return None

        geometry = np.shape(images[0])
        blank_image = np.zeros(geometry, np.uint8)
        xy = self.datamodel.get_xy_size()
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

    def export_jpg_image(self):
        img = self.get_preview_image()
        filename = self.datamodel.full_media_url + ".jpg"
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

