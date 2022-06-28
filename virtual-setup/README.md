# Deploying a virtual environment of the dci-rhel-agent

## Introduction

This playbook will provide a way to deploy a full virtualized environment of the
`dci-rhel-agent` with one SUT.

## Running the virtual setup

```
ansible-playbook site.yml -v
```

## Run manually the agent

# Run the agent

```
[dci@jumpbox ~]$ sudo dci-rhel-agent-ctl --start
```

## Destroy the virtual setup

```
cd virtual-setup/
ansible-playbook site.yml -e "hook_action=cleanup"
```
