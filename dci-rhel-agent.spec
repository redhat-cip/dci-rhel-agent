Name:             dci-rhel-agent
Version:          0.3.0
Release:          1.VERS%{?dist}
Summary:          The RHEL's DCI agent
License:          ASL 2.0
URL:              https://github.com/redhat-cip/dci-rhel-agent
BuildArch:        noarch
Source0:          dci-rhel-agent-%{version}.tar.gz

BuildRequires:    systemd
BuildRequires:    /usr/bin/pathfix.py
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires:    python2-devel
BuildRequires:    PyYAML
%else
BuildRequires:    python3-devel
BuildRequires:    python3-pyyaml
%endif

%{?systemd_requires}

Requires:         podman
Requires:         make
Requires:         dci-downloader
%if 0%{?rhel} && 0%{?rhel} < 8
Requires:         PyYAML
%else
Requires:         python3-pyyaml
%endif

%description
The RHEL's DCI agent

%prep
%setup -qc

%build

%install
install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 dcirc.sh.dist %{buildroot}%{_sysconfdir}/dci-rhel-agent/dcirc.sh.dist
install -p -D -m 644 inventory %{buildroot}%{_sysconfdir}/dci-rhel-agent/inventory
install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-rhel-agent/settings.yml
install -p -D -m 644 hooks/user-tests.yml %{buildroot}%{_sysconfdir}/dci-rhel-agent/hooks/user-tests.yml
install -p -D -m 644 hooks/pre-run.yml %{buildroot}%{_sysconfdir}/dci-rhel-agent/hooks/pre-run.yml
install -p -D -m 755 dci-rhel-agent-ctl %{buildroot}%{_bindir}/dci-rhel-agent-ctl
mkdir %{buildroot}%{_sysconfdir}/dci-rhel-agent/secrets
mkdir %{buildroot}%{_sysconfdir}/dci-rhel-agent/hooks/roles
cp -r hooks/roles/ansible-role-dci-rhel-os-tests/ %{buildroot}%{_sysconfdir}/dci-rhel-agent/hooks/roles/
rm -rf %{buildroot}%{_sysconfdir}/dci-rhel-agent/hooks/roles/ansible-role-dci-rhel-os-tests/molecule

%if 0%{?rhel} && 0%{?rhel} < 8
pathfix.py -pni "%{__python2}" %{buildroot}%{_bindir}/dci-rhel-agent-ctl
%else
pathfix.py -pni "%{__python3}" %{buildroot}%{_bindir}/dci-rhel-agent-ctl
%endif

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun

%files
%{_unitdir}/*
%{_bindir}/dci-rhel-agent-ctl
%{_sysconfdir}/dci-rhel-agent/dcirc.sh.dist
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/settings.yml
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/inventory
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/hooks/user-tests.yml
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/hooks/pre-run.yml
%dir  %{_sysconfdir}/dci-rhel-agent/secrets
%dir  %{_sysconfdir}/dci-rhel-agent/hooks/roles
%{_sysconfdir}/dci-rhel-agent/hooks/roles/ansible-role-dci-rhel-os-tests/meta/*
%{_sysconfdir}/dci-rhel-agent/hooks/roles/ansible-role-dci-rhel-os-tests/tasks/*

%changelog
* Mon Dec 06 2021 Guillaume Vincent <guillaume@oslab.fr> 0.3.0-1
- Add os-tests role
* Tue Jul 28 2020 Michael Burke <miburke@redhat.com> 0.2.0-2
- Add support for Ansible roles in hooks directory
* Wed Apr 1 2020 Guillaume Vincent <gvincent@redhat.com> - 0.2.0-1
- Add hooks folder support
* Wed Dec 11 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-8
- Add suport for external Beaker service
- Remove Makefile
* Tue Oct 29 2019 Michael Burke <miburke@redhat.com> - 0.1.2-7
- Updates for PPC arch
* Wed Oct 09 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-6
- Introduce dci-rhel-agent-ctl
* Tue Aug 13 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-5
- Use dci-downloader instead of built-in downloader
- Add support for RHEL Compose (multi-arch, variant)
* Thu Jul 11 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-4
- Allow users to provide a custom XML to bkr job-submit
* Thu Apr 25 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-3
- Make dci-rhel-agent a container
* Wed Apr 17 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-2
- Isolate logs is tmp dir
- Make documentation more helpful
- Move static Bkr xml to Ansible template
- Add custom hooks for user-tests at post-run
* Wed Sep 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.2-1
- Put Certification tests in different ansible role
* Wed Sep 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.1-1
- Add certification tests
- Ability to download multiple components
* Thu Apr 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.0-1
- Initial release
