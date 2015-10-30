# Spec file for python-docker-sync.
#
# Copyright (c) 2015 Andrew Stiegmann (andrew.stiegmann@gmail.com)
#

Name:    python-docker-sync
Version: 1.2.4
Release: 1%{?dist}
Summary: Docker container sync and management utility
License: UNKNOWN
Group:   Applications/Internet
Url:     https://github.com/autosportlabs/docker-sync
Source:  https://github.com/autosportlabs/docker-sync/archive/v%{version}.zip

BuildRequires:     python2-devel
Requires:          python2
Requires:          python-docker-py >= 0.6.0
Requires:          PyYAML >= 3.10
Requires:          python-semantic_version >= 2.3.1

%{?python_provide: %python_provide python-%{srcname}}

BuildRoot: %{_tmppath}/%{name}-%{version}-build
BuildArch: noarch


%description
A utility written to sync and spin up the various docker containers
referenced by a directory provided on the command line.


%prep
%setup -qn docker-sync-%{version}


%build
# Nothing to do


%install
mkdir -p %{buildroot}%{python2_sitelib}/docker_sync/lib
install -m0644 docker_sync/*.py %{buildroot}%{python2_sitelib}/docker_sync/
install -m0644 docker_sync/lib/*.py %{buildroot}%{python2_sitelib}/docker_sync/lib

mkdir -p %{buildroot}%{_bindir}
install -m0755 scripts/docker-sync %{buildroot}%{_bindir}/docker-sync


%files
%{_bindir}/docker-sync
%{python2_sitelib}/docker_sync


%changelog
* Thu Oct 29 2015 Stieg <andrew.stiegmann@gmail.com> - 1.2.4-1.el7.centos
- Initial creation of the RHEL 7 spec file
