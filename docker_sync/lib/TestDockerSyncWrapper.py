# -*- encoding: utf-8 -*-

import httpretty
import json
import os
from nose.tools import eq_

from DockerSyncWrapper import DockerSyncWrapper
from ImageTag import ImageTag
from ContainerDefinition import ContainerDefinition

class TestDockerSyncWrapper():
    DOCKER_HOST_URL = "http://docker.local:5454"
    EXAMPLE_DIR = os.path.abspath(os.path.join(__file__, "../../../example"))
    
    @httpretty.activate
    def test_getImages(self):
        docker = DockerSyncWrapper(docker_host=self.DOCKER_HOST_URL)

        httpretty.register_uri(
            httpretty.GET,
            self.DOCKER_HOST_URL + "/v1.8/images/json",
            body=json.dumps([
                {
                   "RepoTags": [
                     "ubuntu:12.04",
                     "ubuntu:precise",
                     "ubuntu:latest"
                   ],
                   "Id": "8dbd9e392a964056420e5d58ca5cc376ef18e2de93b5cc90e868a1bbc8318c1c",
                   "Created": 1365714795,
                   "Size": 131506275,
                   "VirtualSize": 131506275
                },
                {
                   "RepoTags": [
                     "ubuntu:12.10",
                     "ubuntu:quantal"
                   ],
                   "ParentId": "27cf784147099545",
                   "Id": "b750fe79269d2ec9a3c593ef05b4332b1d1a02a62b4accb2c21d589ff2f5f2dc",
                   "Created": 1364102658,
                   "Size": 24653,
                   "VirtualSize": 180116135
                }
            ]),
            content_type="application/json",
        )
        
        images = docker.getImages()

        eq_(httpretty.last_request().querystring["all"], ["1"])
        
        assert ImageTag.parse("ubuntu:12.10") in images, "tag not found"
    
    @httpretty.activate
    def test_getImageIdFromRegistry(self):
        docker = DockerSyncWrapper(docker_host=self.DOCKER_HOST_URL)

        httpretty.register_uri(
            httpretty.GET,
            "http://index.docker.io/v1/repositories/some/repo/tags",
            body=json.dumps([
                { "layer": "84422536", "name": "latest" }
            ]),
            content_type="application/json",
        )
        
        img_id = docker.getImageIdFromRegistry(ImageTag("some/repo", tag="latest"))

        eq_("84422536", img_id)

    @httpretty.activate
    def test_getContainers(self):
        docker = DockerSyncWrapper(docker_host=self.DOCKER_HOST_URL)

        httpretty.register_uri(
            httpretty.GET,
            self.DOCKER_HOST_URL + "/v1.8/containers/json",
            body=json.dumps([
                {
                    "Command":"/bin/sh -c 'exec docker-registry'",
                    "Created":1413905954,
                    "Id":"68afa73fe4d5a4012566a24b5f0487fd25b154d66a593b4e67425199487099a5",
                    "Image":"registry:0.8.1",
                    "Names":["/pensive_euclid"],
                    "Ports":[
                        {"IP":"0.0.0.0","PrivatePort":5000,"PublicPort":49153,"Type":"tcp"}
                    ],
                    "Status":"",
                },
            ]),
            content_type="application/json",
        )
        
        httpretty.register_uri(
            httpretty.GET,
            self.DOCKER_HOST_URL + "/v1.8/containers/pensive_euclid/json",
            body=json.dumps(
                {
                    "ID": "68afa73fe4d5a4012566a24b5f0487fd25b154d66a593b4e67425199487099a5",
                    "Created": "2014-10-21T15:39:14.468411999Z",
                    "Path": "/bin/sh",
                    "Args": [ "-c", "exec docker-registry" ],
                    "Config": {
                        "Hostname": "68afa73fe4d5",
                        "Domainname": "",
                        "User": "",
                        "Memory": 0,
                        "MemorySwap": 0,
                        "CpuShares": 0,
                        "Cpuset": "",
                        "AttachStdin": False,
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
                        ],
                        "Cmd": [
                            "/bin/sh",
                            "-c",
                            "exec docker-registry"
                        ],
                        "Image": "registry:0.8.1",
                        "Volumes": None,
                        "WorkingDir": "",
                        "Entrypoint": None,
                        "NetworkDisabled": False,
                        "OnBuild": None
                    },
                    "State": {
                        "Running": False,
                        "Paused": False,
                        "Pid": 0,
                        "ExitCode": 0,
                        "StartedAt": "0001-01-01T00:00:00Z",
                        "FinishedAt": "0001-01-01T00:00:00Z"
                    },
                    "Image": "326f0493022a886302ca28625533f006517836fb9a0645a7b7da7a220b3e3cf4",
                    "NetworkSettings": {
                        "IPAddress": "172.17.0.3",
                        "IPPrefixLen": 16,
                        "Gateway": "172.17.42.1",
                        "Bridge": "docker0",
                        "PortMapping": None,
                        "Ports": {
                            "5000/tcp": [
                                {
                                    "HostIp": "0.0.0.0",
                                    "HostPort": "49153"
                                }
                            ]
                        }
                    },
                    "ResolvConfPath": "/etc/resolv.conf",
                    "HostnamePath": "/var/lib/docker/containers/68afa73fe4d5a4012566a24b5f0487fd25b154d66a593b4e67425199487099a5/hostname",
                    "HostsPath": "/var/lib/docker/containers/68afa73fe4d5a4012566a24b5f0487fd25b154d66a593b4e67425199487099a5/hosts",
                    "Name": "/pensive_euclid",
                    "Driver": "devicemapper",
                    "ExecDriver": "native-0.2",
                    "MountLabel": "",
                    "ProcessLabel": "",
                    "Volumes": {
                        "/tmp/registry": "/tmp/registry"
                    },
                    "VolumesRW": {
                        "/tmp/registry": True
                    },
                    "HostConfig": {
                        "Binds": [
                            "/tmp/registry:/tmp/registry"
                        ],
                        "ContainerIDFile": "",
                        "LxcConf": [],
                        "Privileged": False,
                        "PortBindings": {
                            "5000/tcp": [
                                {
                                    "HostIp": "0.0.0.0",
                                    "HostPort": "49153"
                                }
                            ]
                        },
                        "Links": None,
                        "PublishAllPorts": True,
                        "Dns": None,
                        "DnsSearch": None,
                        "VolumesFrom": None,
                        "NetworkMode": "bridge"
                    }
                }
            ),
            content_type="application/json",
        )
        
        containers = docker.getContainers()

        eq_(httpretty.HTTPretty.latest_requests[0].querystring["all"], ["1"])

        assert "pensive_euclid" in containers

    @httpretty.activate
    def test_startContainer(self):
        docker = DockerSyncWrapper(docker_host=self.DOCKER_HOST_URL)
        cdef = ContainerDefinition.parseFile(os.path.join(self.EXAMPLE_DIR, "30-elasticsearch.yaml"))
        
        container_id = "e90e34656806"
        
        httpretty.register_uri(
            httpretty.POST,
            self.DOCKER_HOST_URL + "/v1.8/containers/create",
            body=json.dumps(
                {
                    "Id": container_id,
                    "Warnings": [],
                }
            ),
            content_type="application/json",
            status=201,
        )
        
        httpretty.register_uri(
            httpretty.POST,
            "%s/v1.8/containers/%s/start" % (self.DOCKER_HOST_URL, container_id),
            content_type="text/plain",
            status=204,
        )

        docker.startContainer(cdef)
        
        # create_req = json.loads(httpretty.HTTPretty.latest_requests[0].body)
        start_req = json.loads(httpretty.HTTPretty.latest_requests[1].body)
        
        eq_(
            set([
                "/var/lib/docker_container_data/elasticsearch:/var/lib/elasticsearch:rw",
                "/var/lib/docker/hosts:/etc/hosts:ro",
            ]),
            set(start_req["Binds"]),
        )
