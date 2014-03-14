# -*- encoding: utf-8 -*-

import re

class ImageTag(object):
    """image tag representation"""
    
    @classmethod
    def parse(cls, tag_str):
        """ parses image tags """
        
        ## <none>:<none>
        ## ubuntu => http://index.docker.io/v1/repositories/ubuntu/tags/latest
        ## ubuntu:12.04
        ## ubuntu:latest
        ## some/repo
        ## some/repo:aTag
        ## remote.registry:port/some/repo
        ## remote.registry:port/some/repo:aTag
        
        if tag_str == "<none>:<none>":
            return None


        registry = None
        repo_path = None
        repo_tag = None
                
        if tag_str.count("/") in (0, 1):
            repo_path = tag_str.split(":")
            
            if len(repo_path) == 2:
                repo_path, repo_tag = repo_path
            else:
                repo_path = repo_path[0]
        else:
            match = re.match(
                r"""(?P<registry>[a-z][a-z0-9.-]+(:\d+)?)/(?P<repo_path>[^:]+)(:(?P<repo_tag>.+))?""",
                tag_str
            )
            
            registry = match.group("registry")
            repo_path = match.group("repo_path")
            repo_tag = match.group("repo_tag")
            
        if repo_path:
            return ImageTag(repo_path, repo_tag, registry)
    
    def __init__(self, repository, tag=None, registry=None):
        super(ImageTag, self).__init__()
        
        assert repository
        self.repository = str(repository)
        
        self.tag = str(tag) if tag else "latest"
        self.registry = str(registry) if registry else None
    
    def __hash__(self):
        return hash((self.registry, self.repository, self.tag))
    
    def __str__(self):
        retVal = self.repository
        
        if self.tag is not None:
            retVal = ":".join((retVal, self.tag))
        
        if self.registry is not None:
            retVal = "/".join((self.registry, retVal))
        
        return retVal
    
    __repr__ = __str__
    
    def __cmp__(self, other):
        return cmp(repr(self), repr(other))
