# -*- encoding: utf-8 -*-

class Image(object):
    def __init__(self, _id):
        super(Image, self).__init__()

        self._id = _id
        self._tags = set()
    
    @property
    def id(self):
        return self._id
    
    @property
    def tags(self):
        return self._tags
    
    @tags.setter
    def tags(self, tags):
        self._tags = set(tags)
    
    def __str__(self):
        return "<Image %s [%r]>" % (self.id, self.tags)
    
    __repr__ = __str__
