# Building the RPM

This spec file stages and builds the `python-docker-sync` rpm that is used by the ASL system.  The steps below show you how to build the RPM file.

## Steps
1. Boot up the vagrant image found in the puppet repo.
2. Install the `rpmdevtools` and `rpm-build` packages if not already installed.
3. As the non root user, run `rpmdev-setuptree`.  This builds the file structure you will need under the `~/rpmbuild` directory.
4. Copy the spec file into `~/rpmuild/SPECS`.
5. Use curl or wget to get the version of the source you are trying to build.  The URL for this source is in the `Source:` tag in the spec file.  Ensure this zip file ends up in the `SOURCES` directory.
6. Run `rpmbuild -ba ~/rpmbuild/SPECS/python-docker-sync.spec`.  This should build both the SRPM and RPM files.  Look in SRPM and RPM directories to find them.
