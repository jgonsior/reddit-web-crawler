__author__ = 'julius'


class Post:
    """ Facebook Post """

    def __init__(self):
        self.id = None
        self.fb_id = None
        self.content = None
        self.author = None
        self.nLikes = None
        self.nComments = 0
        self.timeOfPublication = None
        self.original_features = None
        self.features = None
        self.representativeFor = 0
        self.daysSinceBegin = None
        self.distances = {}