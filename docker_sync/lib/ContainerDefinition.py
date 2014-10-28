# -*- encoding: utf-8 -*-

import yaml

from ImageTag import ImageTag

class ContainerDefinition(object):
    def __init__(self, name, image_tag):
        ## containers always have at least one name.  the name with only a
        ## leading slash shall be the canonical name and all others shall be
        ## aliases.

        assert isinstance(image_tag, ImageTag)
        
        super(ContainerDefinition, self).__init__()

        self._name = name
        self.image_tag = image_tag
        
        self.id = None
        
        self.hostname = None
        self.command = []
        self.env = {}
        self.ports = None
        self.volumes = None
    
    @property
    def name(self):
        return self._name
    
    @classmethod
    def parseFile(cls, ymlFile):
        with open(ymlFile, "r") as ifp:
            yml = yaml.safe_load(ifp)
            
        img_tag = ImageTag.parse(yml["image"])

        container = cls(yml["name"], img_tag)
        container.hostname = yml.get("hostname", None)

        container.command = yml.get("command", None)
        if container.command:
            ## convert all arguments to strings
            container.command = [ str(a) for a in container.command ]
        
        container.env = yml.get("env", {})
        for key in container.env:
            ## coerce all values to strings
            container.env[key] = str(container.env[key])
        
        container.volumes = yml.get("volumes", None)
        if container.volumes is not None:
            for v in container.volumes:
                if "ReadWrite" not in container.volumes[v]:
                    container.volumes[v]["ReadWrite"] = True

        container.ports = yml.get("ports", None)
        if container.ports is not None:
            for p in container.ports:
                if "HostIp" not in container.ports[p]:
                    container.ports[p]["HostIp"] = "0.0.0.0"
        
        return container
