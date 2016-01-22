# -*- encoding: utf-8 -*-

class Image(object):
    @classmethod
    def fromJson(cls, json):
        """creates Image instance from a Docker image JSON dict"""

        img = Image(json["Id"])
        config = json.get("Config", {})
        img.entrypoint = config.get("Entrypoint", None)
        img.command = config.get("Cmd", None)

        for env in config.get("Env", []):
            k, v = env.split("=", 1)
            img.env[k] = v

        for k in ("PATH", "HOME"):
            if k in img.env:
                del img.env[k]

        return img

    def __init__(self, _id):
        super(Image, self).__init__()

        self._id = _id
        self._tags = set()
        self.entrypoint = None
        self.command = None
        self.env = {}

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
