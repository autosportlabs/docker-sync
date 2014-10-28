# -*- encoding: utf-8 -*-

import Manager
from lib import ContainerDefinition, Container, Image
import os

from nose.tools import eq_

class TestManager:
    EXAMPLE_DIR = os.path.abspath(os.path.join(__file__, "../../example"))

    def test_containerIsOutOfSync(self):
        container_def = ContainerDefinition.parseFile(os.path.join(self.EXAMPLE_DIR, "00-private-registry.yaml"))
        
        img_info = Image.fromJson({
            "id": "2e2d7133e4a578bd861e85e7195412201f765d050af78c7906841ea62eb6f7dd",
            "parent": "c79dab5561020bda9ce1b1cbe76283fc95f824cfb26a8a21a384993ed7f392bd",
            "created": "2014-10-21T08:50:44.448455269Z",
            "container": "b756100785c797b9f43d36f249b0d5688d88a1ca68df56d915cb436c4bfc7286",
            "config": {
                "OnBuild": [],
                "NetworkDisabled": False,
                "Entrypoint": None,
                "WorkingDir": "",
                "Volumes": None,
                "Image": "c79dab5561020bda9ce1b1cbe76283fc95f824cfb26a8a21a384993ed7f392bd",
                "Cmd": [
                    "/bin/sh",
                    "-c",
                    "exec docker-registry"
                ],
                "AttachStdin": False,
                "Cpuset": "",
                "CpuShares": 0,
                "MemorySwap": 0,
                "Memory": 0,
                "User": "",
                "Domainname": "",
                "Hostname": "965c252e48c3",
                "AttachStdout": False,
                "AttachStderr": False,
                "PortSpecs": None,
                "ExposedPorts": {
                    "5000/tcp": {}
                },
                "Tty": False,
                "OpenStdin": False,
                "StdinOnce": False,
                "Env": [
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "DOCKER_REGISTRY_CONFIG=/docker-registry/config/config_sample.yml",
                    "SETTINGS_FLAVOR=dev"
                ]
            },
        })

        container_info = Container.fromJson("private-registry", {
            "HostConfig": {
                "NetworkMode": "",
                "VolumesFrom": None,
                "DnsSearch": None,
                "Binds": [
                    "/tmp:/var/lib/docker/registry",
                ],
                "ContainerIDFile": "",
                "LxcConf": None,
                "Privileged": False,
                "PortBindings": {
                    "5000/tcp": [
                        {
                            "HostPort": "11003",
                            "HostIp": "0.0.0.0"
                        }
                    ]
                },
                "Links": None,
                "PublishAllPorts": False,
                "Dns": None
            },
            "VolumesRW": {
                "/var/lib/docker/registry": True,
            },
            "Volumes": {
                "/var/lib/docker/registry": "/tmp",
            },
            "NetworkSettings": {
                "Ports": {
                    "5000/tcp": [
                        {
                            "HostPort": "11003",
                            "HostIp": "0.0.0.0"
                        }
                    ]
                },
                "PortMapping": None,
                "Bridge": "docker0",
                "Gateway": "172.17.42.1",
                "IPPrefixLen": 16,
                "IPAddress": "172.17.0.31"
            },
            "Image": "2e2d7133e4a578bd861e85e7195412201f765d050af78c7906841ea62eb6f7dd",
            "State": {
                "FinishedAt": "0001-01-01T00:00:00Z",
                "StartedAt": "2014-10-28T16:38:31.491949274Z",
                "ExitCode": 0,
                "Pid": 18785,
                "Paused": False,
                "Running": True
            },
            "Config": {
                "OnBuild": None,
                "NetworkDisabled": False,
                "Entrypoint": None,
                "WorkingDir": "",
                "Volumes": {
                    "/var/lib/docker/registry": {},
                },
                "Image": "registry:0.8.1",
                "Cmd": [
                    "/bin/sh",
                    "-c",
                    "exec docker-registry"
                ],
                "AttachStdin": False,
                "Cpuset": "",
                "CpuShares": 0,
                "MemorySwap": 0,
                "Memory": 0,
                "User": "",
                "Domainname": "",
                "Hostname": "private-registry",
                "AttachStdout": False,
                "AttachStderr": False,
                "PortSpecs": None,
                "ExposedPorts": {
                    "5000/tcp": {}
                },
                "Tty": False,
                "OpenStdin": False,
                "StdinOnce": False,
                "Env": [
                    "SETTINGS_FLAVOR=local",
                    "STORAGE_PATH=/var/lib/docker/registry",
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "DOCKER_REGISTRY_CONFIG=/docker-registry/config/config_sample.yml"
                ]
            },
            "Args": [
                "-c",
                "exec docker-registry"
            ],
            "Path": "/bin/sh",
            "Created": "2014-10-28T16:38:31.20825271Z",
            "ID": "758a155a0374fa7e163e4fc71e96cd1bd7de37674dd5f552b9183789366e91f7",
            "ResolvConfPath": "/etc/resolv.conf",
            "HostnamePath": "/var/lib/docker/containers/758a155a0374fa7e163e4fc71e96cd1bd7de37674dd5f552b9183789366e91f7/hostname",
            "HostsPath": "/var/lib/docker/containers/758a155a0374fa7e163e4fc71e96cd1bd7de37674dd5f552b9183789366e91f7/hosts",
            "Name": "/private-registry",
            "Driver": "devicemapper",
            "ExecDriver": "native-0.2",
            "MountLabel": "",
            "ProcessLabel": ""
        })

        eq_(Manager.containerIsOutOfSync(container_def, container_info, img_info), False)

    def test_containerIsOutOfSync_hosts(self):
        container_def = ContainerDefinition.parseFile(os.path.join(self.EXAMPLE_DIR, "00-hosts.yaml"))
        
        ## blalor/docker-hosts:latest
        img_info = Image.fromJson({
            "Size": 0,
            "os": "linux",
            "architecture": "amd64",
            "id": "98e7ca605530c6ee637e175f08e692149a4d019b384e421e661bd35601b25975",
            "parent": "15e3a43eb69d67df5a6ae1f3b3e87407f3b82157bf54fe8a5dc997cf2ce6528a",
            "created": "2014-07-30T01:02:04.516066768Z",
            "container": "5d7384258a7ac29d8eabe30b6b1d83dfe4a8925440f33982b439731906a087f2",
            "docker_version": "1.1.1",
            "author": "Brian Lalor <blalor@bravo5.org>",
            "config": {
                "OnBuild": [],
                "NetworkDisabled": False,
                "Entrypoint": [
                    "/usr/local/bin/docker-hosts"
                ],
                "WorkingDir": "",
                "Volumes": None,
                "Image": "15e3a43eb69d67df5a6ae1f3b3e87407f3b82157bf54fe8a5dc997cf2ce6528a",
                "Cmd": None,
                "AttachStdin": False,
                "Cpuset": "",
                "CpuShares": 0,
                "MemorySwap": 0,
                "Memory": 0,
                "User": "",
                "Domainname": "",
                "Hostname": "5ca9d941ba62",
                "AttachStdout": False,
                "AttachStderr": False,
                "PortSpecs": None,
                "ExposedPorts": None,
                "Tty": False,
                "OpenStdin": False,
                "StdinOnce": False,
                "Env": [
                    "HOME=/",
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ]
            }
        })

        container_info = Container.fromJson("hosts", {
            "HostConfig": {
                "NetworkMode": "",
                "VolumesFrom": None,
                "DnsSearch": None,
                "Binds": [
                    "/var/run/docker.sock:/var/run/docker.sock:rw",
                    "/var/lib/docker/hosts:/srv/hosts:rw"
                ],
                "ContainerIDFile": "",
                "LxcConf": None,
                "Privileged": False,
                "PortBindings": None,
                "Links": None,
                "PublishAllPorts": False,
                "Dns": None
            },
            "VolumesRW": {
                "/var/run/docker.sock": True,
                "/srv/hosts": True
            },
            "Volumes": {
                "/var/run/docker.sock": "/var/run/docker.sock",
                "/srv/hosts": "/var/lib/docker/hosts"
            },
            "NetworkSettings": {
                "Ports": {},
                "PortMapping": None,
                "Bridge": "docker0",
                "Gateway": "172.17.42.1",
                "IPPrefixLen": 16,
                "IPAddress": "172.17.0.17"
            },
            "Image": "98e7ca605530c6ee637e175f08e692149a4d019b384e421e661bd35601b25975",
            "State": {
                "FinishedAt": "0001-01-01T00:00:00Z",
                "StartedAt": "2014-10-28T18:22:51.492441086Z",
                "ExitCode": 0,
                "Pid": 27669,
                "Paused": False,
                "Running": True
            },
            "Config": {
                "OnBuild": None,
                "NetworkDisabled": False,
                "Entrypoint": [
                    "/usr/local/bin/docker-hosts"
                ],
                "WorkingDir": "",
                "Volumes": {
                    "/var/run/docker.sock": {},
                    "/srv/hosts": {}
                },
                "Image": "blalor/docker-hosts:latest",
                "Cmd": [
                    "--domain-name=dev.docker",
                    "/srv/hosts"
                ],
                "AttachStdin": False,
                "Cpuset": "",
                "CpuShares": 0,
                "MemorySwap": 0,
                "Memory": 0,
                "User": "",
                "Domainname": "",
                "Hostname": "04bf6ca07d2c",
                "AttachStdout": False,
                "AttachStderr": False,
                "PortSpecs": None,
                "ExposedPorts": None,
                "Tty": False,
                "OpenStdin": False,
                "StdinOnce": False,
                "Env": [
                    "HOME=/",
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ]
            },
            "Args": [
                "--domain-name=dev.docker",
                "/srv/hosts"
            ],
            "Path": "/usr/local/bin/docker-hosts",
            "Created": "2014-10-28T18:22:51.142918682Z",
            "ID": "04bf6ca07d2c610235f57b041e224c19b6fab51d400a599ee0f1b1c53e12201f",
            "ResolvConfPath": "/etc/resolv.conf",
            "HostnamePath": "/var/lib/docker/containers/04bf6ca07d2c610235f57b041e224c19b6fab51d400a599ee0f1b1c53e12201f/hostname",
            "HostsPath": "/var/lib/docker/containers/04bf6ca07d2c610235f57b041e224c19b6fab51d400a599ee0f1b1c53e12201f/hosts",
            "Name": "/hosts",
            "Driver": "devicemapper",
            "ExecDriver": "native-0.2",
            "MountLabel": "",
            "ProcessLabel": ""
        })

        eq_(Manager.containerIsOutOfSync(container_def, container_info, img_info), False)
