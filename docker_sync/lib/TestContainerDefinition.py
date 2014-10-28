# -*- encoding: utf-8 -*-

from ContainerDefinition import ContainerDefinition
from ImageTag import ImageTag

from nose.tools import eq_
import os

class TestContainerDefinition:
    EXAMPLE_DIR = os.path.abspath(os.path.join(__file__, "../../../example"))
    
    def test_parseFile(self):
        cdef = ContainerDefinition.parseFile(os.path.join(self.EXAMPLE_DIR, "00-private-registry.yaml"))
        
        eq_(cdef.name, "private-registry")
        eq_(cdef.image_tag, ImageTag("registry", tag="0.8.1"))
        eq_(cdef.env["SETTINGS_FLAVOR"], "local")
        eq_(cdef.ports["5000/tcp"], { "HostIp": "0.0.0.0", "HostPort": 11003 })
        eq_(cdef.volumes["/var/lib/docker/registry"], { "HostPath": "/tmp", "ReadWrite": True })
