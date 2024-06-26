FROM centos:7

LABEL name="dci-rhel-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum upgrade -y && \
  yum -y install epel-release https://packages.distributed-ci.io/dci-release.el7.noarch.rpm && \
  yum-config-manager --add-repo https://beaker-project.org/yum/beaker-harness-CentOS.repo && \
  yum-config-manager --add-repo https://releases.ansible.com/ansible-runner/rpm/epel-7-x86_64/ && \
  yum-config-manager --save --setopt=releases.ansible.com_ansible-runner_rpm_epel-7-x86_64_.gpgkey=https://releases.ansible.com/keys/RPM-GPG-KEY-ansible-release.pub && \
  yum -y install gcc ansible python python2-devel python2-pip python-lxml \
                 dci-ansible ansible-role-dci-rhel-certification rsync python2-ansible-runner \
                 ansible-role-dci-rhel-cki-0.0.3 git restraint-client python-netaddr patch \
                 python2-productmd createrepo_c dnf-plugins-core dci-downloader dnf && \
  yum clean all

RUN ansible-galaxy collection install 'containers.podman:<1.10.3' && \
    ansible-galaxy collection install ansible.posix && \
    ansible-galaxy collection install community.general && \
    ansible-galaxy collection install community.libvirt && \
    ansible-galaxy collection install ansible.utils:2.10.3

ADD dci-rhel-agent /usr/share/dci-rhel-agent/

# Install dumb-init package to handle PID 1 problem and reap any zombie processes
RUN pip install 'dumb-init==1.2.2' && \
    pip install xmltodict

# Ansible-runner bug: https://github.com/ansible/ansible-runner/issues/219
RUN cp /usr/share/dci/callback/dci.py /usr/lib/python2.7/site-packages/ansible_runner/callbacks

WORKDIR /usr/share/dci-rhel-agent
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python", "entrypoint.py"]
