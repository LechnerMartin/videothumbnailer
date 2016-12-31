import datetime


class Chapter:
    def __init__(self, timestamp, title = "Chapter", description = ""):
        self.timestamp = timestamp
        self.title = title
        self.description = description

    def __eq__(self, other):
        if other != None:
            return (self.timestamp == other.timestamp) and\
                   (self.title == other.title) and \
                   (self.description == other.description)

        return False

    def __str__(self):
        return self.__repr__()

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __le__(self, other):
        return self.timestamp <= other.timestamp


    def __repr__(self):
        return str(self.__dict__)

    def __hash__(self):
        return self.timestamp.__hash__()


class Xy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x: {}, y: {}".format(self.x, self.y)

    def __eq__(self, other):
        if other != None:
            return (self.x == other.x) and (self.y == other.y)
        return False


class TimeContainer:

    def __init__(self, milliseconds):
        if milliseconds < 0:
            milliseconds = 0
        self.milliseconds = milliseconds
        try:
            self.__datetime = datetime.datetime.utcfromtimestamp(milliseconds/1000.0)
        except ValueError as ex:
            raise ValueError(str(ex) + " " + str(milliseconds))

    def strftime(self, formatstring):
        return self.__datetime.strftime(formatstring)

    def __str__(self):
        return self.__datetime.strftime("%H:%M:%S")

    def __repr__(self):
        return str(self.milliseconds)

    def __eq__(self, other):
        return self.milliseconds == other.milliseconds

    def __lt__(self, other):
        return self.milliseconds < other.milliseconds

    def __le__(self, other):
        return self.milliseconds <= other.milliseconds


    def __hash__(self):
        return hash(self.milliseconds)