FROM registry.access.redhat.com/ubi7/ubi

LABEL name="dci-rhel-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

# ANSIBLE
RUN yum-config-manager --enable rhel-7-server-ansible-2-rpms
RUN yum -y --disableplugin=subscription-manager install ansible

# ANSIBLE-RUNNER
RUN yum-config-manager --add-repo http://download.hosts.prod.upshift.rdu2.redhat.com/nightly/rhel-7/updates/ansible-runner/latest-ansible-runner-1.2-RHEL-7/compose/Server/x86_64/os/
RUN yum -y --nogpg install ansible-runner

# DCI
RUN yum -y --disableplugin=subscription-manager install  https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
RUN yum -y install ansible-role-dci-import-keys dci-ansible ansible-role-dci-rhel-certification ansible-role-dci-rhel-cki

RUN yum clean all

ADD dci-rhel-agent /usr/share/dci-rhel-agent/
WORKDIR /usr/share/dci-rhel-agent
CMD ["python", "entrypoint.py"]