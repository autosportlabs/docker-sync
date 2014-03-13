#!/usr/bin/env python
# -*- encoding: utf-8 -*-

## I'm beginning to think container links are just plain evil.  the dependency
## tracking is a pain in the ass.  So instead of trying to trace dependencies,
## all containers will be "linked" via explicit port mappings, via the host.

import logging
logging.basicConfig(level=logging.WARN)

import yaml
import glob
import subprocess
import re
import types
import time

# http://docs.python-requests.org/en/v1.2.3/
import requests

## cached objects: http://stackoverflow.com/questions/13054250/python-object-cache


class ImageTag(object):
    """image tag representation"""
    
    @classmethod
    def parse(cls, tag_str):
        """ parses image tags """
        
        ## <none>:<none>
        ## ubuntu => http://index.docker.io/v1/repositories/ubuntu/tags/latest
        ## ubuntu:12.04
        ## ubuntu:latest
        ## some/repo
        ## some/repo:aTag
        ## remote.registry:port/some/repo
        ## remote.registry:port/some/repo:aTag
        
        if tag_str == "<none>:<none>":
            return None


        registry = None
        repo_path = None
        repo_tag = None
                
        if tag_str.count("/") in (0, 1):
            repo_path = tag_str.split(":")
            
            if len(repo_path) == 2:
                repo_path, repo_tag = repo_path
            else:
                repo_path = repo_path[0]
        else:
            match = re.match(
                r"""(?P<registry>[a-z][a-z0-9.-]+(:\d+)?)/(?P<repo_path>[^:]+)(:(?P<repo_tag>.+))?""",
                tag_str
            )
            
            registry = match.group("registry")
            repo_path = match.group("repo_path")
            repo_tag = match.group("repo_tag")
            
        if repo_path:
            return ImageTag(repo_path, repo_tag, registry)
    
    def __init__(self, repository, tag=None, registry=None):
        super(ImageTag, self).__init__()
        
        assert repository
        self.repository = str(repository)
        
        self.tag = str(tag) if tag else "latest"
        self.registry = str(registry) if registry else None
    
    def __hash__(self):
        return hash((self.registry, self.repository, self.tag))
    
    def __str__(self):
        retVal = self.repository
        
        if self.tag is not None:
            retVal = ":".join((retVal, self.tag))
        
        if self.registry is not None:
            retVal = "/".join((self.registry, retVal))
        
        return retVal
    
    __repr__ = __str__
    
    def __cmp__(self, other):
        return cmp(repr(self), repr(other))
    

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
        self.env = None
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
        container.hostname = yml["hostname"]
        
        container.env = yml["env"]
        if container.env is not None:
            for key in container.env:
                ## coerce all values to strings
                container.env[key] = str(container.env[key])
        
        container.volumes = yml["volumes"]
        if container.volumes is not None:
            for v in container.volumes:
                if "ReadWrite" not in container.volumes[v]:
                    container.volumes[v]["ReadWrite"] = True

        container.ports = yml["ports"]
        if container.ports is not None:
            for p in container.ports:
                if "HostIp" not in container.ports[p]:
                    container.ports[p]["HostIp"] = "0.0.0.0"
        
        return container


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


class Docker(object):
    """interfaces with the local Docker daemon"""
    
    API_VERSION = "1.8"
    
    def __init__(self, http_port):
        super(Docker, self).__init__()
        
        self.logger = logging.getLogger("Docker")
        self.logger.setLevel(logging.DEBUG)
        
        self.base_url = "http://127.0.0.1:%d/v%s" % (http_port, Docker.API_VERSION)

        self.images = {}
        self.containers = {}

    def __get(self, path):
        retVal = None
        url = self.base_url + path

        self.logger.debug(url)

        start = time.time()
        resp = requests.get(url)
        duration = time.time() - start

        self.logger.debug("%s %d %.2f", url, resp.status_code, duration)
        
        if resp.status_code == requests.codes.ok:
            retVal = resp.json()
        elif resp.status_code != requests.codes.not_found:
            resp.raise_for_status()

        return retVal
    
    def getImages(self):
        """ returns a dict of image_tag => Image instance """
        
        self.images = {}
        
        for img in self.__get("/images/json?all=1"):
            tags = [ ImageTag.parse(t) for t in img["RepoTags"] ]

            image = Image(img["Id"])
            image.tags = tags
            
            for t in image.tags:
                if t:
                    self.images[t] = image
            
        return self.images
    
    def getImage(self, name):
        """ returns an Image for the given name, or None if not found """
        
        retVal = None
        
        img_data = self.__get("/images/%s/json" % name)
        
        if img_data:
            retVal = Image(img_data["id"])
            retVal.tags = [ name if isinstance(name, ImageTag) else ImageTag.parse(name) ]
        
        return retVal
    
    def getContainers(self):
        """ returns a dict of container name => Container """

        ## find all containers
        self.containers = {}
        
        for cont in self.__get("/containers/json?all=1"):
            ## get names without leading "/"
            names = [ n[1:] for n in cont["Names"] ]
            
            ## canonical name has no slashes
            canonical_name = [ n for n in names if "/" not in n ][0]
            
            cont_detail = self.__get("/containers/%s/json" % canonical_name)
            
            container = Container(canonical_name, cont_detail["ID"], Image(cont_detail["Image"]))
            
            container.hostname = cont_detail["Config"]["Hostname"]
            container.running = cont_detail["State"]["Running"]
            
            env_str = cont_detail["Config"]["Env"]
            if env_str:
                container.env = dict([ e.split("=", 1) for e in env_str])
                
                ## remove stuff generated by Docker
                for key in ("PATH", "HOME"):
                    if key in container.env:
                        del container.env[key]
                
                if not container.env:
                    container.env = None
            
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
                    
                    host_path, container_path = bind_info.split(":", 1)
                    
                    container.volumes[container_path] = {
                        "HostPath": host_path,
                        "ReadWrite": read_write,
                    }
            
            container.command.append(cont_detail["Path"])
            container.command.extend(cont_detail["Args"])
            
            self.containers[container.name] = container
            # pprint(("Container", container.__dict__))
        
        return self.containers
    
    def removeContainer(self, name):
        self.logger.info("stopping %s", name)
        
        subprocess.check_call([ "docker", "stop", name ])
        
        ## rm -v to remove volumes; we should always explicitly map a volume to
        ## the host, so this should be a non-issue.
        self.logger.info("removing %s", name)
        
        subprocess.check_call([ "docker", "rm", "-v", name ])
    
    def startContainer(self, container):
        # docker run -d -v … -e … -p … $image $cmd
        cmd = [ "docker", "run", "-d", "-name", container.name ]
        
        if container.hostname:
            cmd.extend([ "-h", container.hostname ])
        
        if container.volumes is not None:
            for vol_name in container.volumes:
                vol_def = container.volumes[vol_name]
                
                cmd.extend([
                    "-v",
                    "%s:%s%s" % (vol_def["HostPath"], vol_name, "" if vol_def["ReadWrite"] else ":ro"),
                ])
        
        if container.env is not None:
            for key in container.env:
                cmd.extend([ "-e", "%s=%s" % (key, container.env[key] )])

        if container.ports is not None:
            for port_spec in container.ports:
                port_def = container.ports[port_spec]
                
                cmd.extend([
                    "-p",
                    "%s:%s:%s" % (port_def["HostIp"], port_def["HostPort"], port_spec)
                ])
        
        cmd.append(str(container.image_tag))
        
        if container.command:
            cmd.extend(container.command)
        
        subprocess.check_call(cmd)
    
    def getImageIdFromRegistry(self, image_tag):
        ## http://localhost:5000/v1/repositories/apps/mongodb/tags/latest
        ## actually returns a list of every layer with that tag.  assuming you'd
        ## grab the first, but that seems weird.
        
        regUrl = "http://%s/v1/repositories/%s/tags" % (
            image_tag.registry if image_tag.registry else "index.docker.io",
            image_tag.repository,
        )
        
        attempts = 0
        success = False
        while not success and attempts < 3:
            attempts += 1
            
            self.logger.debug(regUrl)
            
            try:
                start = time.time()
                resp = requests.get(regUrl)
                duration = time.time() - start
                
                self.logger.debug("%s %d %.2f", regUrl, resp.status_code, duration)
                
                success = True
            except requests.exceptions.ConnectionError, e:
                self.logger.warn("connection error; sleeping 5", exc_info=True)

                time.sleep(5)
        
        if not success:
            self.logger.error("giving up")
            raise e
        
        ## if public registry (index.docker.io):
        ##      [ {"name":"tag", "layer": "<id>"}, …]
        ## else
        ##      { "tag": "<id>", … }
        ## I'm probably looking in the wrong place, but I don't think I can
        ## query the registry without authenticating to the index, and that's
        ## just a pain in the ass.
        layers = resp.json()
        
        if type(layers) == types.ListType:
            layers = dict(map(lambda x: (x["name"], x["layer"]), layers))

        return layers[image_tag.tag]


    def pullImage(self, image_tag):
        # @todo don't need to pull all the images; use self.getImage()
        local_images = self.getImages()
        
        registry_img_id = self.getImageIdFromRegistry(image_tag)
        must_pull = True
        
        if image_tag in local_images and local_images[image_tag].id == registry_img_id:
            self.logger.info("%s is up to date", image_tag)
            
            must_pull = False
        
        if must_pull:
            self.logger.info("pulling %s", image_tag)
            
            subprocess.check_call([ "docker", "pull", str(image_tag) ])
        
        return self.getImage(image_tag)


DOCKER = Docker(4231)

def main(pull=True):
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    
    container_defs = []
    
    for conf in sorted(glob.glob("/etc/docker.d/containers/*.yaml")):
        container_defs.append(ContainerDefinition.parseFile(conf))
            
    ## map of container name -> Container
    containers = DOCKER.getContainers()

    ## work through in sorted order so we can cheat and make private registries
    ## come first
    ## delete out-of-sync and unmanaged containers
    for container_def in container_defs:
        logger.info(container_def.name)
        
        if pull:
            image_def = DOCKER.pullImage(container_def.image_tag)
        else:
            image_def = DOCKER.getImage(container_def.image_tag)

        out_of_sync = False
        
        container_info = containers.get(container_def.name, None)

        if container_info is None:
            out_of_sync = True
        else:
            if container_info.image.id != image_def.id:
                logger.info("image id does not match")
                logger.debug("container_info.image.id %s != image_def.id %s", container_info.image.id, image_def.id)
                
                out_of_sync = True
                
            if container_def.hostname is not None and container_info.hostname != container_def.hostname:
                logger.info("hostname is different")
                logger.debug("container_info.hostname %s != container_def.hostname %s", container_info.hostname, container_def.hostname)
                
                out_of_sync = True
                
            if container_info.env != container_def.env:
                logger.info("env is different")
                logger.debug("container_info.env %s != container_def.env %s", container_info.env, container_def.env)
                
                out_of_sync = True
                
            if container_info.ports != container_def.ports:
                logger.info("ports are different")
                logger.debug("container_info.ports %s != container_def.ports %s", container_info.ports, container_def.ports)
                
                out_of_sync = True
                
            if container_info.volumes != container_def.volumes:
                logger.info("volumes are different")
                logger.debug("container_info.volumes %s != container_def.volumes %s", container_info.volumes, container_def.volumes)
                
                out_of_sync = True
            
            if not container_info.running:
                logger.info("container not running")
                out_of_sync = True
            
        if out_of_sync:
            if container_info:
                logger.info("removing %s", container_def.name)
                DOCKER.removeContainer(container_def.name)
            
            logger.info("creating %s", container_def.name)
            DOCKER.startContainer(container_def)
    
    ## delete unmanaged containers
    defined_container_names = [ c.name for c in container_defs ]
    for cont_name in DOCKER.getContainers():
        if cont_name not in defined_container_names:
            logger.warn("unmanaged container; removing %s", cont_name)
            
            DOCKER.removeContainer(cont_name)
    
    ## @todo remove unused images
    
if __name__ == "__main__":
    import getopt
    import sys
    
    def usage():
        print "Usage: %s -h | --help" % sys.argv[0]
        print "       %s -n | --no-pull" % sys.argv[0]
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn", ["help", "no-pull"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    
    pull = True
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-n", "--no-pull"):
            pull = False
        else:
            assert False, "unhandled option"

    main(pull)
