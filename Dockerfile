FROM centos:7

LABEL name="dci-rhel-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum upgrade -y && \
  yum -y install epel-release https://packages.distributed-ci.io/dci-release.el7.noarch.rpm && \
  yum-config-manager --add-repo https://beaker-project.org/yum/beaker-server-RedHatEnterpriseLinux.repo && \
  yum-config-manager --add-repo https://beaker-project.org/yum/beaker-harness-CentOS.repo && \
  yum -y install gcc ansible python python2-devel python2-pip beaker-client beaker-lab-controller \
                 ansible-role-dci-import-keys ansible-role-dci-retrieve-component \
                 dci-ansible ansible-role-dci-rhel-certification rsync python2-ansible-runner \
                 ansible-role-dci-rhel-cki git restraint-client beaker-common && \
  yum clean all

ADD dci-rhel-agent /usr/share/dci-rhel-agent/

WORKDIR /usr/share/dci-rhel-agent

CMD ["python", "entrypoint.py"]
