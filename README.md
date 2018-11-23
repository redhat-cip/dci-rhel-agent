# DCI RHEL Agent

This is the README of the DCI RHEL agent. It will allow one to schedule a job,
run the appropriate installation steps, run the specified tests and finally
return the tests results back to the DCI API. So both Partners and Red Hat
engineers can troubleshoot together.

## Table of Contents

- [Requirements](#requirements)
  * [Distributed-CI account](#distributed-ci-account)
  * [RemoteCI credentials](#remoteci-credentials)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)

## Requirements

### Distributed-CI account

You need to create your user account in the system. Please connect to
https://www.distributed-ci.io with your redhat.com SSO account.

Your user account will be created in our database the first time you connect.

There is no reliable way to automatically know your team. So please
[contact](#contact) us back when you reach this step, we will manually move
your user in the correct organisation.

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

This is the file that allows one to authenticate against the DCI API. As
explained in [RemoteCI credential](#remoteci-credentials), an admin of the
team should have created a RemoteCI and one should have downloaded the
`remotecirc.sh` and renamed it. The file should look like:

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

| Variable | Required | Type | Description |
|----------|----------|------|-------------|
| topic | True | String | Name of the topic the agent should run |
| local_repo | True | Path | Path to directory where components will be stored |
| local_repo_ip | True | IP | TO WRITE |


### Red Hat Certification: How to skip its execution

Some users might want to skip the certification tests suite. This can be done via the settings file by adding `dci_rhel_agent_cert: false` to `settings.yml` file.


## Usage

To run the agent, one needs to run `systemctl start dci-rhel-agent`


## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team  <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
