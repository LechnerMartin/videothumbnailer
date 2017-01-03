import numpy as np

from videothumbnailer.datamodel.datatypes import Xy, Chapter, TimeContainer as TC


class DataModel:
    def __init__(self):
        self.__marks = []
        self.__chapters = {}
        self.__add_default_chapter()
        self.__images = {}
        self.full_media_url = ""

    def __add_default_chapter(self):
        self.add_chapter(Chapter(TC(0),"Default", ""))

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

    def get_marks(self):
        return self.__marks

    def get_marks_for_chapter(self, chapter):
        starttime = TC(0) if chapter is None else chapter.timestamp
        nextchapter = self.get_next_chapter(starttime)
        if nextchapter is not None:
            endtime = nextchapter.timestamp
            return [x  for x in self.__marks if x >= starttime and x < endtime]
        else:
            return [x  for x in self.__marks if x >= starttime]

    def add_chapter(self, chapter):
        self.__chapters[chapter.timestamp] = chapter

    def get_chapter(self, timestamp):
        if timestamp in self.__chapters.keys():
            return self.__chapters[timestamp]
        return None

    def get_chapter_for_timestamp(self, timestamp):
        keys = list(self.__chapters.keys())
        keys.sort(reverse=True)
        for key in keys:
            if key <= timestamp:
                return self.__chapters[key]
        return None


    def get_previous_chapter(self, timestamp):
        keys = list(self.__chapters.keys())
        keys.sort(reverse=True)
        for key in keys:
            if key < timestamp:
                return self.__chapters[key]
        return None

    def get_next_chapter(self, timestamp):
        keys = list(self.__chapters.keys())
        keys.sort()
        for key in keys:
            if key > timestamp:
                return self.__chapters[key]
        return None


    def get_chapters(self):
        clist = list(self.__chapters.values())
        clist.sort()
        return clist

    def delete_chapter(self, timestamp):
        if timestamp in self.__chapters.keys():
            del self.__chapters[timestamp]

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
            img = self.__images[mark]
            if img is not None:
                result.append(img)
        return result


    def __getitem__(self, index):
        return self.__marks[index]