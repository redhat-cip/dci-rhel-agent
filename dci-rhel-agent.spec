Name:             dci-rhel-agent
Version:          0.1.2
Release:          1.VERS%{?dist}
Summary:          The RHEL's DCI agent
License:          ASL 2.0
URL:              https://github.com/redhat-cip/dci-rhel-agent
BuildArch:        noarch
Source0:          dci-rhel-agent-%{version}.tar.gz

BuildRequires:    systemd
BuildRequires:    systemd-units

Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

Requires:         podman
Requires:         make
Requires:         dci-downloader

%description
The RHEL's DCI agent

%prep
%setup -qc

%build

%install
install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 dcirc.sh.dist %{buildroot}%{_sysconfdir}/dci-rhel-agent/dcirc.sh.dist
install -p -D -m 644 hosts %{buildroot}%{_sysconfdir}/dci-rhel-agent/hosts
install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-rhel-agent/settings.yml
install -p -D -m 644 hooks/user-tests.yml %{buildroot}%{_sysconfdir}/dci-rhel-agent/hooks/user-tests.yml
install -p -D -m 644 Makefile %{buildroot}%{_sysconfdir}/dci-rhel-agent/Makefile
install -p -D -m 755 dci-rhel-agent-ctl %{buildroot}%{_bindir}/dci-rhel-agent/dci-rhel-agent-ctl

%clean

%pre

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun

%files
%{_unitdir}/*
%{_sysconfdir}/dci-rhel-agent/Makefile
%{_bindir}/dci-rhel-agent/dci-rhel-agent-ctl
%{_sysconfdir}/dci-rhel-agent/dcirc.sh.dist
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/settings.yml
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/hosts
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/hooks/user-tests.yml

%changelog
* Tue Oct 09 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-6
- Introduce dci-rhel-agent-ctl
* Tue Aug 13 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-5
- Use dci-downloader instead of built-in downloader
- Add support for RHEL Compose (multi-arch, variant)
* Thu Jul 11 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-4
- Allow users to provide a custom XML to bkr job-submit
* Wed Apr 25 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-3
- Make dci-rhel-agent a container
* Wed Apr 17 2019 Thomas Vassilian <tvassili@redhat.com> - 0.1.2-2
- Isolate logs is tmp dir
- Make documentation more helpful
- Move static Bkr xml to Ansible template
- Add custom hooks for user-tests at post-run
* Tue Sep 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.2-1
- Put Certification tests in different ansible role
* Tue Sep 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.1-1
- Add certification tests
- Ability to download multiple components
* Tue Apr 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.0-1
- Initial release
