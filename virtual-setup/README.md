# Deploying a virtual environment of the dci-rhel-agent

## Introduction
This playbook will provide a way to deploy a full virtualized environment of the 
`dci-rhel-agent` with one jumpbox and one SUT.

## Installation of the requierements
```
cd virtual-setup/
ansible-galaxy install -r requirements.yml
```

Download Centos 7 qemu base image and put it in `/var/lib/libvirt/images/CentOS-7-x86_64-GenericCloud-2009.qcow2`

## Running the virtual setup

```
cd virtual-setup/
ansible-playbook site.yml -e "dci_client_id=dci_clientid dci_api_secret=dci_api_secret"
```

You can also put all these configurations in a file and run the playbook
```
ansible-playbook site.yml -e @~/.virtual_setup_vars.yml
```

## Destroy the virtual setup

``
cd virtual-setup/
ansible-playbook site.yml -e "hook_action=cleanup"
```