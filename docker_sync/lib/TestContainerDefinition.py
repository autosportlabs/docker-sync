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
        eq_(cdef.image_tag, ImageTag("blalor/docker-local-registry", tag="latest"))
        eq_(cdef.env["AWS_BUCKET"], "some-bucket")
        eq_(cdef.ports["5000/tcp"], { "HostIp": "0.0.0.0", "HostPort": 11003 })
        eq_(cdef.volumes["/var/lib/docker/registry"], { "HostPath": "/tmp", "ReadWrite": True })
