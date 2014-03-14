# -*- encoding: utf-8 -*-

import yaml

from Image import Image

class Container(object):
    def __init__(self, name, id, image):
        assert isinstance(image, Image)
        
        super(Container, self).__init__()

        self._name = name
        self._id = id
        self.image = image
        
        self.hostname = None
        self.command = []
        self.env = None
        self.ports = None
        self.volumes = None
        self.running = None
    
    @property
    def name(self):
        return self._name
    
    @property
    def id(self):
        return self._id
    
    def toYaml(self):
        return yaml.safe_dump({
            "name":     self.name,
            "image":    self.image.tags,
            "command":  self.command,
            "hostname": self.hostname,
            "env":      self.env,
            "ports":    self.ports,
            "volumes":  self.volumes,
        }, default_flow_style=False, indent="    ")
