#!/usr/bin/env python
# -*- encoding: utf-8 -*-

## I'm beginning to think container links are just plain evil.  the dependency
## tracking is a pain in the ass.  So instead of trying to trace dependencies,
## all containers will be "linked" via explicit port mappings, via the host.

import logging
logging.basicConfig(level=logging.WARN)

import glob

## cached objects: http://stackoverflow.com/questions/13054250/python-object-cache

from lib import Docker
from lib import ContainerDefinition

DOCKER = Docker(4243)

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
