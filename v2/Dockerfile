FROM centos:7

LABEL name="DCI RHEL AGENT"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum -y install epel-release && \
    yum -y install gcc ansible python python2-devel python2-pip && \
    yum clean all

RUN yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
RUN yum -y install ansible-role-dci-import-keys ansible-role-dci-retrieve-component dci-ansible

RUN mkdir /opt/dci-rhel-agent/
WORKDIR /opt/dci-rhel-agent/
COPY requirements.txt /opt/dci-rhel-agent/requirements.txt
RUN pip install -r /opt/dci-rhel-agent/requirements.txt
RUN pip freeze

COPY agent.yml /opt/dci-rhel-agent/agent.yml
COPY ansible.cfg /opt/dci-rhel-agent/ansible.cfg
COPY scheduler.py /opt/dci-rhel-agent/scheduler.py

CMD ["python", "/opt/dci-rhel-agent/scheduler.py"]
