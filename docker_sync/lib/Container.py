# -*- encoding: utf-8 -*-

import yaml

from Image import Image

class Container(object):
    @classmethod
    def fromJson(cls, canonical_name, cont_detail):
        container = Container(canonical_name, cont_detail["Id"], Image(cont_detail["Image"]))

        container.hostname = cont_detail["Config"]["Hostname"]
        container.running = cont_detail["State"]["Running"]

        env_strs = cont_detail["Config"]["Env"]
        if env_strs:
            container.env = dict([ e.split("=", 1) for e in env_strs])

            ## remove stuff generated by Docker
            for key in ("PATH", "HOME"):
                if key in container.env:
                    del container.env[key]

        if cont_detail["HostConfig"]["PortBindings"]:
            for port_def in cont_detail["HostConfig"]["PortBindings"]:
                binding = cont_detail["HostConfig"]["PortBindings"][port_def]

                ## binding is none if port not mapped to host
                if binding:
                    if container.ports is None:
                        container.ports = {}

                    ## @todo uh, why is this a list?
                    binding = binding[0]

                    ## HostPort is a number in yaml but string in binding
                    container.ports[port_def] = {
                        "HostIp": binding["HostIp"],
                        "HostPort": int(binding["HostPort"]),
                    }

        ## { "/container/mount": { "HostPath": "/some/path", "ReadWrite": True}}
        if cont_detail["HostConfig"]["Binds"]:
            container.volumes = {}

            ## [ "/host/path:/container/path:ro" ] :ro is optional
            for bind_info in cont_detail["HostConfig"]["Binds"]:
                read_write = True

                if bind_info.endswith(":ro"):
                    read_write = False
                    bind_info = bind_info[:-3]
                elif bind_info.endswith(":rw"):
                    read_write = True
                    bind_info = bind_info[:-3]

                host_path, container_path = bind_info.split(":", 1)

                container.volumes[container_path] = {
                    "HostPath": host_path,
                    "ReadWrite": read_write,
                }

        container.command.append(cont_detail["Path"])
        container.command.extend(cont_detail["Args"])

        return container

    def __init__(self, name, id, image):
        assert isinstance(image, Image)

        super(Container, self).__init__()

        self._name = name
        self._id = id
        self.image = image

        self.hostname = None
        self.command = []
        self.env = {}
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
