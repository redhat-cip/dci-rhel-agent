FROM registry.access.redhat.com/ubi9/ubi

LABEL name="dci-rhel-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum upgrade -y && \
  yum -y install https://packages.distributed-ci.io/dci-release.el9.noarch.rpm && \
  yum -y install yum-utils && \
  yum-config-manager --add-repo https://beaker-project.org/yum/harness/RedHatEnterpriseLinux8 && \
  yum-config-manager --add-repo https://packages.distributed-ci.io/repos/current/el/8/x86_64 && \
  yum-config-manager --setopt=beaker-project.org_yum_harness_RedHatEnterpriseLinux8.gpgcheck=0 --save && \
  yum -y install sshpass gcc python3 python3-devel python3-pip python3-lxml \
                 rsync restraint-client python3-netaddr patch openssh-clients \
                 dci-downloader dnf ansible-role-dci-rhel-cki-0.0.3 ansible-role-dci-rhel-certification && \
  yum clean all

RUN pip3 install -U pip && \
    pip3 install createrepo-c && \
    pip3 install ansible && \
    pip3 install ansible-runner && \
    #Install dumb-init package to handle "PID 1 problem" and reap zombie processes
    pip3 install 'dumb-init==1.2.2' && \
    pip3 install xmltodict && \
    pip3 install productmd


# Installing dci-ansible manually to work around Ansible dependency since Ansible
# is installed via pip here
RUN dnf download dci-ansible
RUN rpm -ivh --nodeps dci-ansible*.rpm

ENV LC_ALL="C.UTF-8"

ADD dci-rhel-agent /usr/share/dci-rhel-agent/

WORKDIR /usr/share/dci-rhel-agent
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["python3", "entrypoint.py"]
