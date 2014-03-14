#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="docker-sync",
    version="0.0.0",
    description="Configuration management for Docker containers",
    author="Brian Lalor",
    author_email="brian@autosportlabs.com",
    url="http://github.com/autosportlabs/docker-sync",
    packages=find_packages(),
    install_requires=[
        "requests >= 1.2, < 2.0",
        "PyYAML >= 3.10, < 4.0",
        "argparse >= 1.1",
    ],
    entry_points={
        "console_scripts": [
            "docker_sync = docker_sync.cli:sync",
            "docker_sync_gen = docker_sync.cli:gen",
        ],
    },
)
