FROM centos:7

LABEL name="dci-rhel-agent"
LABEL version="1.0.0"
LABEL maintainer="DCI Team <distributed-ci@redhat.com>"

ENV LANG en_US.UTF-8

RUN yum -y install epel-release
RUN yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
RUN yum-config-manager --add-repo https://beaker-project.org/yum/beaker-server-RedHatEnterpriseLinux.repo
RUN yum -y install gcc ansible python python2-devel python2-pip beaker-client beaker-lab-controller ansible-role-dci-import-keys ansible-role-dci-retrieve-component dci-ansible ansible-role-dci-rhel-certification
RUN yum clean all
RUN cp /bin/true /usr/bin/setfacl
ADD dci-rhel-agent /usr/share/dci-rhel-agent/

WORKDIR /usr/share/dci-rhel-agent

CMD ["/usr/bin/ansible-playbook", "-vv", "/usr/share/dci-rhel-agent/dci-rhel-agent.yml", "-e", "@/etc/dci-rhel-agent/settings.yml", "-i", "/etc/dci-rhel-agent/hosts"]