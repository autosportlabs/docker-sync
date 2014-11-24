#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from distutils.core import setup

setup(
    name="docker-sync",
    version="1.2.0",
    description="Configuration management for Docker containers",
    long_description=open("README.md").read(),
    author="Brian Lalor",
    author_email="brian@autosportlabs.com",
    url="http://github.com/autosportlabs/docker-sync",
    packages=[ "docker_sync", "docker_sync.lib" ],
    scripts=[ "scripts/docker-sync" ],
)
