# -*- encoding: utf-8 -*-

from ImageTag import ImageTag

from nose.tools import eq_

class TestImageTag:
    def test_untagged(self):
        eq_(None, ImageTag.parse("<none>:<none>"))
    
    def test_official_repo_only(self):
        # http://index.docker.io/v1/repositories/ubuntu/tags/latest
        eq_(ImageTag(repository="ubuntu", tag="latest"), ImageTag.parse("ubuntu"))

    def test_official_repo_with_simple_tag(self):
        eq_(ImageTag(repository="ubuntu", tag="12.04"), ImageTag.parse("ubuntu:12.04"))

    def test_official_repo_with_latest(self):
        eq_(ImageTag(repository="ubuntu", tag="latest"), ImageTag.parse("ubuntu:latest"))

    def test_repo_with_path(self):
        eq_(ImageTag(repository="some/repo", tag="latest"), ImageTag.parse("some/repo"))

    def test_repo_with_path_and_tag(self):
        eq_(ImageTag(repository="some/repo", tag="aTag"), ImageTag.parse("some/repo:aTag"))

    def test_remote_registry(self):
        eq_(ImageTag(repository="some/repo", tag="latest", registry="remote.registry:5000"), ImageTag.parse("remote.registry:5000/some/repo"))

    def test_remote_registry_with_tag(self):
        eq_(ImageTag(repository="some/repo", tag="aTag", registry="remote.registry:5000"), ImageTag.parse("remote.registry:5000/some/repo:aTag"))
