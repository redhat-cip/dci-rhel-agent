FROM centos:7

LABEL name="dci-rhel-agent-cfg"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum upgrade -y && \
  yum -y install epel-release https://packages.distributed-ci.io/dci-release.el7.noarch.rpm && \
  yum -y install gcc ansible dci-ansible python python2-devel python2-pip && \
  yum clean all

ADD dci-rhel-agent-cfg /usr/share/dci-rhel-agent-cfg/
RUN pip install -r /usr/share/dci-rhel-agent-cfg/requirements.txt && pip freeze

# Ansible-runner bug: https://github.com/ansible/ansible-runner/issues/219
RUN cp /usr/share/dci/callback/dci.py /usr/lib/python2.7/site-packages/ansible_runner/callbacks

WORKDIR /usr/share/dci-rhel-agent-cfg

CMD ["python", "entrypoint-cfg.py"]
