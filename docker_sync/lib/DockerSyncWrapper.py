# -*- encoding: utf-8 -*-

import logging
import os
import time
import types

# http://docs.python-requests.org/en/v1.2.3/
import requests

import semantic_version as semver

import docker as DockerPy

from ImageTag import ImageTag
from Image import Image
from Container import Container

class DockerSyncWrapper(object):
    """interfaces with the local Docker daemon"""

    API_VERSION = "1.8"

    def __init__(self, docker_host=None):
        super(DockerSyncWrapper, self).__init__()

        self.logger = logging.getLogger("Docker")
        self.logger.setLevel(logging.DEBUG)

        self.client = DockerPy.Client(
            base_url=docker_host if docker_host else os.environ.get("DOCKER_HOST", None),
            version=DockerSyncWrapper.API_VERSION,
        )

        self.images = {}
        self.containers = {}

    def getImages(self):
        """ returns a dict of image_tag => Image instance """

        self.images = {}

        for img in self.client.images(all=True):
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

        img_data = self.client.inspect_image(name)

        if img_data:
            retVal = Image.fromJson(img_data)
            retVal.tags = [ name if isinstance(name, ImageTag) else ImageTag.parse(name) ]

        return retVal

    def getContainers(self):
        """ returns a dict of container name => Container """

        ## find all containers
        self.containers = {}

        for cont in self.client.containers(all=True):
            ## get names without leading "/"
            names = [ n[1:] for n in cont["Names"] ]

            ## canonical name has no slashes
            canonical_name = [ n for n in names if "/" not in n ][0]

            container = Container.fromJson(canonical_name, self.client.inspect_container(canonical_name))
            self.containers[container.name] = container

        return self.containers

    def removeContainer(self, name, remove_delay=None):
        self.logger.info("stopping %s", name)

        self.client.stop(name)

        ## http://blog.hashbangbash.com/2014/11/docker-devicemapper-fix-for-device-or-resource-busy-ebusy/
        ## https://github.com/docker/docker/issues/8176
        ## https://github.com/docker/docker/issues/5684
        ## attempted workaround is to sleep between stop and remove
        if remove_delay is not None:
            self.logger.info("delaying %ds before removing" % remove_delay)
            time.sleep(remove_delay)

        ## rm -v to remove volumes; we should always explicitly map a volume to
        ## the host, so this should be a non-issue.
        self.logger.info("removing %s", name)

        self.client.remove_container(name, v=True)

    def startContainer(self, container):
        create_container_params = {
            "name":        container.name,
            "detach":      True,
            "command":     container.command,  ## can be None
            "hostname":    container.hostname, ## can be None
            "environment": container.env,      ## can be None
            # "ports":       None,
            # "volumes":     None,
            # "environment": None,
        }

        start_container_params = {
            # "port_bindings": {},
            # "binds": {},
        }

        if container.volumes is not None:
            create_container_params["volumes"] = []
            start_container_params["binds"] = {}

            for vol_name in container.volumes:
                vol_def = container.volumes[vol_name]

                create_container_params["volumes"].append(vol_name)

                ## https://github.com/dotcloud/docker-py/issues/175
                if semver.Version(DockerPy.__version__) < semver.Version("0.3.2"):
                    start_container_params["binds"][vol_def["HostPath"]] = "%s%s" % (
                        vol_name,
                        ":rw" if vol_def["ReadWrite"] else ":ro",
                    )
                else:
                    start_container_params["binds"][vol_def["HostPath"]] = {
                        "bind": vol_name,
                        "ro": not vol_def["ReadWrite"],
                    }


        if container.ports is not None:
            create_container_params["ports"] = []
            start_container_params["port_bindings"] = {}

            for port_spec in container.ports:
                port_def = container.ports[port_spec]

                create_container_params["ports"].append(tuple(port_spec.split("/")))
                start_container_params["port_bindings"][port_spec] = (
                    port_def["HostIp"],
                    port_def["HostPort"],
                )

        resp = self.client.create_container(str(container.image_tag), **create_container_params)
        container_id = resp["Id"]

        self.logger.info("created container for %s with id %s", container.name, container_id)

        if resp.get("Warnings", None):
            for warning in resp["Warnings"]:
                self.logger.warn(warning)

        self.client.start(container_id, **start_container_params)
        self.logger.info("started container %s", container.name)

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

            self.logger.debug("querying registry: " + regUrl)

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

    def pullImage(self, image_tag, insecure_registry=False):
        # @todo don't need to pull all the images; use self.getImage()
        local_images = self.getImages()

        registry_img_id = self.getImageIdFromRegistry(image_tag)
        must_pull = True

        if image_tag in local_images and local_images[image_tag].id == registry_img_id:
            self.logger.info("%s is up to date", image_tag)

            must_pull = False

        if must_pull:
            self.logger.info("pulling %s", image_tag)

            repoUrl = image_tag.repository

            if image_tag.registry is not None:
                repoUrl = "/".join((image_tag.registry, repoUrl))

            self.client.pull(repoUrl, tag=image_tag.tag, insecure_registry=insecure_registry)

        return self.getImage(str(image_tag))
