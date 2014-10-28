#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="docker-sync",
    version="1.1.0",
    description="Configuration management for Docker containers",
    long_description=open("README.md").read(),
    author="Brian Lalor",
    author_email="brian@autosportlabs.com",
    url="http://github.com/autosportlabs/docker-sync",
    packages=find_packages(),
    setup_requires=[
        "nose >= 1.3.4, < 1.4.0",
    ],
    tests_require=[
        "HTTPretty >= 0.8.3, < 0.9.0"
    ],
    install_requires=[
        "PyYAML >= 3.10, < 4.0",
        "argparse >= 1.1",
        "docker-py >= 0.3.0, < 0.4.0",
        "setuptools",
        "semantic_version >= 2.3.1, < 2.4.0"
    ],
    entry_points={
        "console_scripts": [
            "docker-sync = docker_sync.cli:sync",
        ],
    },
)
