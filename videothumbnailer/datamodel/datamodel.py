import numpy as np

from videothumbnailer.datamodel.datatypes import Xy


class DataModel:
    def __init__(self):
        self.__marks = []
        self.__chapters = {}
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
        if timecontainer not in self.__images.keys() or self.__images[timecontainer] is None:
            self.__images[timecontainer] = image

    def get_by_idx(self, idx):
        return self.__marks[idx]

    def add_chapter(self, chapter):
        self.__chapters[chapter.timestamp] = chapter

    def get_chapter(self, timestamp):
        if timestamp in self.__chapters.keys():
            return self.__chapters[timestamp]
        return None

    def get_chapters(self):
        return list(self.__chapters.values())

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