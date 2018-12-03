# DCI RHEL Agent

This is the README of the DCI RHEL agent. It will allow one to schedule a job,
run the appropriate installation steps, run the specified tests and finally
return the tests results back to the DCI API. So both Partners and Red Hat
engineers can troubleshoot together.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)

## Requirements
### Setup Requirements

#### Assumptions
* Partner/Customer will use RHEL 7.6 or above.
* Partner/Customer has a valid configuration to install RHEL using DHCP/PXE/Kickstart.
* Partner/Customer has minimal hardware lab to be installed and wiped through DCI workflow.

#### Jumpbox

Jumpbox can be a physical server or a virtual machine.
In any case, it must:

* Be running the latest stable RHEL release and registered via RHSM.
* Have at least 160GB of free space available in `/var`
* (Ideally) access to Internet
* Be able to connect following Web urls:
  * DCI API, https://api.distributed-ci.io
  * DCI Packages, https://packages.distributed-ci.io
  * DCI Repository, https://repo.distributed-ci.io
  * EPEL, https://dl.fedoraproject.org/pub/epel/
* Have a stable internal IP
* Be able to reach the lab servers using (mandadory, but not limited to):
  * SSH
  * IPMI
  * Serial-Over-LAN or other remote console (details & software to be provided by the partner)
* Be reachable by the lab servers using:
  * DHCP
  * PXE
  * HTTP/HTTPS

##### Bandwidth requirement

DCI needs to download RHEL new snapshots regularly (=~ 4GB each).

##### Remote access

We strongly advise the partner to give access to the jumpbox to Red Hat team.
This way, Red Hat engineers will be able to help to do the initial setup and troubleshoot potential issues.

##### Additional remarks

Please note that the Jumpbox acts as a `controller node`, therefore it is NOT wiped/deployed after each `dci-rhel-agent` run (unlike hardware lab servers).

`dci-hrel-agent` use [Beaker](https://beaker-project.org) service to deploy RHEL automatically.

### Distributed-CI account

Every users need to create their own account in DCI by connecting to
`https://www.distributed-ci.io` using @redhat.com SSO account.

User account will be created in DCI database at the first connection.

**Please [contact](#contact) us back when you reach this step, to be assigned in the correct organisation.**

### RemoteCI credentials

A RemoteCI in DCI terms is a platform and its jumpbox.

One simply specifies a label, and a resource will be created with an ID and an
API_TOKEN that will let one authenticate to run jobs.

Only the admins of a team can create a RemoteCI. If you are not an admin of
your team, please contact her to ensure the RemoteCI is adequately created.

Once the remoteci is ready, one can download its authentication file on the
Download rc file column in the RemoteCI section in the UI.

The file is called `remotecirc.sh`, please rename it to `dcirc.sh` for the
next step.

## Installation

The agent comes in form of a RPM called `dci-rhel-agent`. In order to install
it one needs to install the `dci-release` and `epel-release` packages.

```bash
#> yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
#> yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
#> yum -y install dci-rhel-agent
```

## Configuration

There are two main configuration files: `/etc/dci-rhel-agent/dcirc.sh` and
`/etc/dci-rhel-agent/settings.yml`.


  * `/etc/dci-rhel-agent/dcirc.sh`

This file contents your lab credential (also kwnown as RemoteCI in DCI web interface). As
explained in [RemoteCI credential](#remoteci-credentials), an admin of the
team should have created a Remote CI, downloaded the relative `remotecirc.sh` file and renamed it locally on the Jumpbox to `/etc/dci-rhel-agent/dcirc.sh`.

The file content should looks like:

```bash
#!/usr/bin/env bash
DCI_CS_URL="https://api.distributed-ci.io/"
DCI_CLIENT_ID=remoteci/<remoteci_id>
DCI_API_SECRET=>remoteci_api_secret>
export DCI_CS_URL
export DCI_CLIENT_ID
export DCI_API_SECRET
```

* `/etc/dci-rhel-agent/settings.yml`
```
| Variable | Required | Type | Description |
|----------|----------|------|-------------|
| topic | True | String | Name of the topic the agent should run |
| local_repo | True | Path | Path to directory where components will be stored |
| local_repo_ip | True | IP | TO WRITE |
```

### Red Hat Certification: How to skip its execution

Some users might want to skip the certification tests suite. This can be done via `settings.yml` file by adding `dci_rhel_agent_cert: false`.

## Usage

To start `dci-rhel-agent`, please use `systemctl start dci-rhel-agent`.


## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team  <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
