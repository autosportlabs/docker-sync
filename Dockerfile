FROM blalor/centos
# MAINTAINER Brian Lalor <brian@autosportlabs.com>

RUN yum install -y python-pip
ADD . /src
RUN pip install /src

ENTRYPOINT [ "docker-sync" ]
# CMD [ "/etc/docker/containers.d" ]
CMD [ "/src/example" ]
