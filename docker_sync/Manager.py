#!/usr/bin/env python
# -*- encoding: utf-8 -*-

## I'm beginning to think container links are just plain evil.  the dependency
## tracking is a pain in the ass.  So instead of trying to trace dependencies,
## all containers will be "linked" via explicit port mappings, via the host.

import logging
logging.basicConfig(level=logging.WARN)

import os
import glob

## cached objects: http://stackoverflow.com/questions/13054250/python-object-cache

from lib import DockerSyncWrapper as Docker
from lib import ContainerDefinition

DOCKER = Docker()

LOGGER = logging.getLogger("main")

def containerIsOutOfSync(container_def, container_info, image_info):
    out_of_sync = False

    ## the effective command being executed is different from the configured
    ## command because the effective command includes the entrypoint.
    effective_command = image_info.entrypoint or []

    if container_def.command:
        effective_command += container_def.command
    else:
        effective_command += image_info.command or []
    
    ## include image's env vars when comparing container def's vars
    effective_env = dict(image_info.env.items() + container_def.env.items())

    if container_info.image.id != image_info.id:
        LOGGER.info("image id does not match")
        LOGGER.debug("container_info.image.id %s != image_info.id %s", container_info.image.id, image_info.id)
        
        out_of_sync = True
        
    if container_def.hostname is not None and container_info.hostname != container_def.hostname:
        LOGGER.info("hostname is different")
        LOGGER.debug("container_info.hostname %s != container_def.hostname %s", container_info.hostname, container_def.hostname)
        
        out_of_sync = True
        
    if container_info.command != effective_command:
        LOGGER.info("command is different")
        LOGGER.debug("container_info.command %s != effective_command %s", container_info.command, effective_command)
        
        out_of_sync = True
        
    if container_info.env != effective_env:
        LOGGER.info("env is different")
        LOGGER.debug("container_info.env %s != effective_env %s", container_info.env, effective_env)
        
        out_of_sync = True
        
    if container_info.ports != container_def.ports:
        LOGGER.info("ports are different")
        LOGGER.debug("container_info.ports %s != container_def.ports %s", container_info.ports, container_def.ports)
        
        out_of_sync = True
        
    if container_info.volumes != container_def.volumes:
        LOGGER.info("volumes are different")
        LOGGER.debug("container_info.volumes %s != container_def.volumes %s", container_info.volumes, container_def.volumes)
        
        out_of_sync = True
    
    if not container_info.running:
        LOGGER.info("container not running")
        out_of_sync = True
    
    return out_of_sync


def main(config_dir, pull=True):
    LOGGER.setLevel(logging.DEBUG)
    
    container_defs = []
    
    for conf in sorted(glob.glob(os.path.join(config_dir, "*.yaml"))):
        container_defs.append(ContainerDefinition.parseFile(conf))
            
    ## map of container name -> Container
    containers = DOCKER.getContainers()

    ## work through in sorted order so we can cheat and make private registries
    ## come first
    ## delete out-of-sync and unmanaged containers
    for container_def in container_defs:
        LOGGER.info(container_def.name)
        
        if pull:
            image_info = DOCKER.pullImage(container_def.image_tag)
        else:
            image_info = DOCKER.getImage(container_def.image_tag)
        
        container_info = containers.get(container_def.name, None)
        
        out_of_sync = True
        
        if container_info is not None:
            out_of_sync = containerIsOutOfSync(container_def, container_info, image_info)
            
        if out_of_sync:
            if container_info:
                LOGGER.info("removing %s", container_def.name)
                DOCKER.removeContainer(container_def.name)
            
            LOGGER.info("creating %s", container_def.name)
            DOCKER.startContainer(container_def)
    
    ## delete unmanaged containers
    defined_container_names = [ c.name for c in container_defs ]
    for cont_name in DOCKER.getContainers():
        if cont_name not in defined_container_names:
            LOGGER.warn("unmanaged container; removing %s", cont_name)
            
            DOCKER.removeContainer(cont_name)
