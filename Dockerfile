FROM registry.access.redhat.com/ubi7/ubi

LABEL name="dci-rhel-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8
RUN yum update  --disableplugin=subscription-manager -y
RUN yum upgrade --disableplugin=subscription-manager -y
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y --disableplugin=subscription-manager install  https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
RUN yum -y --nogpg install \
                 --disableplugin=subscription-manager \
                 --enablerepo=ubi-7 \
                 --enablerepo=ubi-7-rhah \
                 --enablerepo=ubi-7-server-devtools-rpms \
                 --enablerepo=ubi-7-server-extras-rpms \
                 --enablerepo=ubi-7-server-optional-rpms \
                 --enablerepo=ubi-server-rhscl-7-rpms \
                 --enablerepo=epel \
                 gcc ansible python python2-devel python2-pip \
                 ansible-role-dci-import-keys \
                 dci-ansible ansible-role-dci-rhel-certification rsync \
                 ansible-role-dci-rhel-cki git
RUN yum clean all

ADD dci-rhel-agent /usr/share/dci-rhel-agent/
RUN pip install -r /usr/share/dci-rhel-agent/requirements.txt && pip freeze

# Ansible-runner bug: https://github.com/ansible/ansible-runner/issues/219
RUN cp /usr/share/dci/callback/dci.py /usr/lib/python2.7/site-packages/ansible_runner/callbacks

WORKDIR /usr/share/dci-rhel-agent

CMD ["python", "entrypoint.py"]
