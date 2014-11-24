# docker-sync

Helper utility for configuration management tools like Chef and Puppet.

Given a directory of config files (see the `example` directory), docker-sync
will ensure that the running containers are kept in sync with the config files,
and will remove containers that no longer have a related config file.

It's a little bit opinionated: container links aren't supported (tho they could
be in the future); all containers are detached.  The image a container is
instantiated from is compared to its tag in its appropriate registry, and the
pull is only done if the registry tag is different than the local tag (a `docker
pull` is slow even when there are no changes).

In the future I may support [dogestry][dogestry] as an alternative (or companion
to) a traditional Docker registry.

## installation

    pip install docker-sync

Or from a clone:

    pip install -r requirements.txt
    pip install .

## example usage

    docker-sync ./example

or

    ./docker_sync/cli.py ./example

## options

You can add `--no-pull` to skip pulling images; very useful when you're
iterating on your configs.

## running tests

    python setup.py nosetests

[dogestry]: https://github.com/blake-education/dogestry
