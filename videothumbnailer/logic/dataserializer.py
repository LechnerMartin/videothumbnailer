from videothumbnailer.datamodel.datamodel import DataModel
from videothumbnailer.datamodel.datatypes import Chapter, TimeContainer as TC

class DataSerializer:

    def serialize(self, model):
        marks = [m.milliseconds for m in model]
        chapters = [self.__chapter_to_dict(chap) for chap in model.get_chapters()  ]
        data = {"Marks": marks, "Chapters" : chapters }
        return data
      #marklist = [m.milliseconds for m in self.__marks]
       #{"Mediaurl": self.full_media_url, "Marks": marklist}


    def __chapter_to_dict(self, chap):
        dict  = {}
        dict["Timestamp"] = chap.timestamp.milliseconds
        dict["Title"] = chap.title
        dict["Description"] = chap.description
        return dict


    def deserialize(self, data):
        model = DataModel()
        if data is None:
            return model

        model.full_media_url = data.get("Mediaurl", "")
        marks = data.get("Marks", [])
        chapters = data.get("Chapters", [])
        for mark in marks:
            model.add_mark(TC(mark), None)
        for chapdata in chapters:
            time = chapdata.get("Timestamp", 0)
            title = chapdata.get("Title", "")
            description = chapdata.get("Description", "")
            model.add_chapter(Chapter(TC(time), title, description))
        return model