Name:             dci-rhel-agent
Version:          0.1.0
Release:          1.VERS%{?dist}
Summary:          The RHEL's DCI agent
License:          ASL 2.0
URL:              https://github.com/redhat-cip/dci-rhel-agent
BuildArch:        noarch
Source0:          dci-rhel-agent-%{version}.tar.gz

BuildRequires:    systemd
BuildRequires:    systemd-units
Requires:         dci-ansible
Requires:         python-lxml
Requires:         python-netaddr
Requires:         ansible-role-dci-import-keys
Requires:         ansible-role-dci-retrieve-component

Requires:         sudo

Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
The RHEL's DCI agent

%prep
%setup -qc

%build

%install
install -p -D -m 644 systemd/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -p -D -m 644 systemd/%{name}.timer %{buildroot}%{_unitdir}/%{name}.timer
install -p -D -m 644 systemd/dci-update.timer %{buildroot}%{_unitdir}/dci-update.timer
install -p -D -m 644 ansible.cfg %{buildroot}%{_datadir}/dci-rhel-agent/ansible.cfg
install -p -D -m 644 dci-rhel-agent.yml %{buildroot}%{_datadir}/dci-rhel-agent/dci-rhel-agent.yml
install -p -D -m 644 dcirc.sh %{buildroot}%{_sysconfdir}/dci-rhel-agent/dcirc.sh
install -p -D -m 644 hooks/clean.yml %{buildroot}%{_datadir}/dci-rhel-agent/hooks/clean.yml
install -p -D -m 644 hooks/import.yml %{buildroot}%{_datadir}/dci-rhel-agent/hooks/import.yml
install -p -D -m 644 hooks/install.yml %{buildroot}%{_datadir}/dci-rhel-agent/hooks/install.yml
install -p -D -m 755 hooks/wait.py %{buildroot}%{_datadir}/dci-rhel-agent/hooks/wait.py
install -p -D -m 644 dci/success.yml %{buildroot}%{_datadir}/dci-rhel-agent/dci/success.yml
install -p -D -m 644 dci/failure.yml %{buildroot}%{_datadir}/dci-rhel-agent/dci/failure.yml
install -p -D -m 644 dci/release.yml %{buildroot}%{_datadir}/dci-rhel-agent/dci/release.yml
install -p -D -m 644 job.xml %{buildroot}%{_sysconfdir}/dci-rhel-agent/job.xml
install -p -D -m 644 hosts %{buildroot}%{_sysconfdir}/dci-rhel-agent/hosts
install -p -D -m 644 dci/test.yml %{buildroot}%{_datadir}/dci-rhel-agent/dci/test.yml
install -p -D -m 644 settings.yml %{buildroot}%{_sysconfdir}/dci-rhel-agent/settings.yml
install -p -D -m 440 dci-rhel-agent.sudo %{buildroot}%{_sysconfdir}/sudoers.d/dci-rhel-agent
install -p -d -m 755 %{buildroot}/%{_sharedstatedir}/dci-rhel-agent

%clean

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
# NOTE(spredzy): Specify /bin/bash instead of /sbin/nologin
# because of https://github.com/ansible/ansible/issues/30620
getent passwd %{name} >/dev/null || \
    useradd -r -m -g %{name} -d %{_sharedstatedir}/%{name} -s /bin/bash \
            -c "DCI-Agent service" %{name}
exit 0

%post
%systemd_post %{name}.service
%systemd_post dci-update.service
%systemd_post %{name}.timer
%systemd_post dci-update.timer

%preun
%systemd_preun %{name}.service
%systemd_preun dci-update.service
%systemd_preun %{name}.timer
%systemd_preun dci-update.timer

%postun
%systemd_postun

%files
%{_unitdir}/*
%{_datadir}/dci-rhel-agent
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/dcirc.sh
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/settings.yml
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/job.xml
%config(noreplace) %{_sysconfdir}/dci-rhel-agent/hosts
%dir %{_sharedstatedir}/dci-rhel-agent
%attr(0755, %{name}, %{name}) %{_sharedstatedir}/dci-rhel-agent
/etc/sudoers.d/dci-rhel-agent

%changelog
* Tue Apr 19 2018 Cedric Lecomte <clecomte@redhat.com> - 0.1.0-1
- Initial release
