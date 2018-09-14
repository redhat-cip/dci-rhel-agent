## Install Requirements
Install required packages

    sudo cat > /etc/yum.repos.d/hwcert.repo <<EOF
    [cdn.stage.redhat.com_content_dist_rhel_server_7_7.5_x86_64_extras_os_]
    name=added from: http://cdn.stage.redhat.com/content/dist/rhel/server/7/7.5/x86_64/extras/os/
    baseurl=http://cdn.stage.redhat.com/content/dist/rhel/server/7/7.5/x86_64/extras/os/
    enabled=1
    gpgcheck=0

    [download.fedoraproject.org_pub_epel_7_x86_64]
    name=added from: http://download.fedoraproject.org/pub/epel/7/x86_64
    baseurl=http://download.fedoraproject.org/pub/epel/7/x86_64
    enabled=1
    gpgcheck=0

    [hwcert-server.khw.lab.eng.bos.redhat.com_packages_devel_RHEL7_]
    name=added from: http://hwcert-server.khw.lab.eng.bos.redhat.com/packages/devel/RHEL7/
    baseurl=http://hwcert-server.khw.lab.eng.bos.redhat.com/packages/devel/RHEL7/
    enabled=1
    gpgcheck=0
    EOF

    sudo yum install -y standard-test-roles
    sudo yum install -y http://file.rdu.redhat.com/~jkinsman/rpms/redhat-certification-hardware-spicegate-0.1-20180720.el7.noarch.rpm

## Execute Playbook
    cd hwcert-sti
    ansible-playbook --tags classic tests.yml

