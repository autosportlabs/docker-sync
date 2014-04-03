#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="docker-sync",
    version="0.0.0",
    description="Configuration management for Docker containers",
    long_description=open("README.md").read(),
    author="Brian Lalor",
    author_email="brian@autosportlabs.com",
    url="http://github.com/autosportlabs/docker-sync",
    packages=find_packages(),
    install_requires=[
        "PyYAML >= 3.10, < 4.0",
        "argparse >= 1.1",
        "docker-py >= 0.3.0, < 0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "docker-sync = docker_sync.cli:sync",
        ],
    },
)
