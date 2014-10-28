# -*- encoding: utf-8 -*-

from Image import Image

from nose.tools import eq_

class TestImage:
    def test_fromJson(self):
        img = Image.fromJson({
            "id": "2e2d7133e4a578bd861e85e7195412201f765d050af78c7906841ea62eb6f7dd",
            "parent": "c79dab5561020bda9ce1b1cbe76283fc95f824cfb26a8a21a384993ed7f392bd",
            "created": "2014-10-21T08:50:44.448455269Z",
            "container": "b756100785c797b9f43d36f249b0d5688d88a1ca68df56d915cb436c4bfc7286",
            "config": {
                "Hostname": "965c252e48c3",
                "User": "",
                "Memory": 0,
                "MemorySwap": 0,
                "AttachStdin": False,
                "AttachStdout": False,
                "AttachStderr": False,
                "PortSpecs": None,
                "Tty": False,
                "OpenStdin": False,
                "StdinOnce": False,
                "Env": [
                    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "DOCKER_REGISTRY_CONFIG=/docker-registry/config/config_sample.yml",
                    "SETTINGS_FLAVOR=dev",
                    "HOME=/"
                ],
                "Entrypoint": None,
                "Cmd": [ "/bin/sh", "-c", "exec", "docker-registry" ],

                "Image": "c79dab5561020bda9ce1b1cbe76283fc95f824cfb26a8a21a384993ed7f392bd",
                "Volumes": None,

                "WorkingDir": "",
            },
        })

        eq_(img.id, "2e2d7133e4a578bd861e85e7195412201f765d050af78c7906841ea62eb6f7dd")
        eq_(img.entrypoint, None)
        eq_(img.command, [ "/bin/sh", "-c", "exec", "docker-registry" ])
        eq_(img.env, {
            "DOCKER_REGISTRY_CONFIG": "/docker-registry/config/config_sample.yml",
            "SETTINGS_FLAVOR": "dev",
        })
