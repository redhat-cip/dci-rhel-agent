# Deploying a virtual environment of the dci-rhel-agent

## Introduction

This playbook will provide a way to deploy a full virtualized environment of the
`dci-rhel-agent` with one jumpbox and one SUT.

## Installation of the requirements

```
sudo yum -y install ansible libvirt git wget
git clone https://github.com/redhat-cip/dci-rhel-agent/
cd dci-rhel-agent/virtual-setup/
ansible-galaxy collection install -r requirements.yml
```

Download Centos 7 qemu base image in the right location

```
sudo wget https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud-2009.qcow2  -P /var/lib/libvirt/images
```

Ensure that you can login locally without password:

```
ssh localhost
```

## Running the virtual setup

```
ansible-playbook site.yml -e "dci_client_id=dci_clientid dci_api_secret=dci_api_secret"
```

You can also put all these configurations in a file and run the playbook

```
ansible-playbook site.yml -e @~/.virtual_setup_vars.yml
```

## Run manually the agent

# Get the jumpbox ip address

```
$ sudo virsh domifaddr jumpbox
 Name       MAC address          Protocol     Address
-------------------------------------------------------------------------------
 vnet0      52:54:00:22:5b:50    ipv4         192.168.122.24/24
```

# Run the agent

```
$ ssh -i ~/.ssh/id_rsa_rhel_ci dci@192.168.122.24
[dci@jumpbox ~]$ sudo dci-rhel-agent-ctl --skip-download --start
```

## Destroy the virtual setup

```
cd virtual-setup/
ansible-playbook site.yml -e "dci_client_id=dci_clientid dci_api_secret=dci_api_secret hook_action=cleanup"
```
