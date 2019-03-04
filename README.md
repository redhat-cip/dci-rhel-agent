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
* Partner/Customer will use RHEL 7.6 or higher.
* Partner/Customer has a valid configuration to install RHEL using DHCP/PXE/Kickstart.
* Partner/Customer has a physical or virtual lab to be installed and wiped through DCI workflow.

#### Jumpbox

Jumpbox can be a physical server or a virtual machine.
In any case, it must:

* Be running the latest stable RHEL release and registered via RHSM.
* Have at least 160GB of free space available in `/var`
* Access to Internet
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

`dci-rhel-agent` use [Beaker](https://beaker-project.org) service to deploy RHEL automatically.

### Distributed-CI account

Every user needs to create his account in DCI by connecting to
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

| Variable | Required | Type | Description |
|----------|----------|------|-------------|
| topic | True | String | Name of the topic the agent should run |
| local_repo | True | Path | Path to directory where components will be stored |
| local_repo_ip | True | IP | TO WRITE |

### Test specific components

By default the agent will use the latest component (build) available.
If you need to test an old component then you need to specify its ID in the
agent configuration (/etc/dci-rhel-agent/settings.yml).

First, get the topic ID

```console
$ dcictl topic-list --where name:RHEL-7
+--------------------------------------+--------+--------+-------------------------------------+----------------+---------------+--------------------------------------+
|                  id                  |  name  | state  |           component_types           | export_control | next_topic_id |              product_id              |
+--------------------------------------+--------+--------+-------------------------------------+----------------+---------------+--------------------------------------+
| 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | RHEL-7 | active | [u'Compose', u'hwcert', u'extraos'] |      True      |      None     | 7adbc8c4-8c9e-4366-aca3-158dfce036c9 |
+--------------------------------------+--------+--------+-------------------------------------+----------------+---------------+--------------------------------------+
```

Then you can list the components associated to that topic and get the IDs (for each component_types).
```console
$ dcictl component-list --topic-id 9e170c05-6bbf-46f7-9a0e-a64a66decc44 --where type:Compose
+--------------------------------------+-----------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+---------+--------------------------------------------------------------------------+
|                  id                  |          name         | state  | canonical_project_name | export_control | message | title |               topic_id               |   type  |                                   url                                    |
+--------------------------------------+-----------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+---------+--------------------------------------------------------------------------+
| cb35c4bc-d4b0-4d3f-9c89-9f5c1969854d | RHEL-7.6-20180906.n.0 | active | RHEL-7.6-20180906.n.0  |      True      |   None  |  None | 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | Compose | http://download-node-02.eng.bos.redhat.com/nightly/RHEL-7.6-20180906.n.0 |
| 1ea259ad-cca4-4c96-aada-78b9909212bb | RHEL-7.6-20180905.n.0 | active | RHEL-7.6-20180905.n.0  |      True      |   None  |  None | 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | Compose | http://download-node-02.eng.bos.redhat.com/nightly/RHEL-7.6-20180905.n.0 |
| 9d30b332-d6d4-4a05-b54f-b26b38f1f71c | RHEL-7.6-20180904.n.0 | active | RHEL-7.6-20180904.n.0  |      True      |   None  |  None | 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | Compose | http://download-node-02.eng.bos.redhat.com/nightly/RHEL-7.6-20180904.n.0 |
+--------------------------------------+-----------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+---------+--------------------------------------------------------------------------+
$ dcictl component-list --topic-id 9e170c05-6bbf-46f7-9a0e-a64a66decc44 --where type:extraos
+--------------------------------------+--------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+---------+------+
|                  id                  |        name        | state  | canonical_project_name | export_control | message | title |               topic_id               |   type  | url  |
+--------------------------------------+--------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+---------+------+
| a40bc44b-df2f-406a-96e5-e0dfe7b36bda | extraos-1525269455 | active |          None          |      True      |   None  |  None | 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | extraos | None |
+--------------------------------------+--------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+---------+------+
$ dcictl component-list --topic-id 9e170c05-6bbf-46f7-9a0e-a64a66decc44 --where type:hwcert
+--------------------------------------+-------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+--------+------+
|                  id                  |        name       | state  | canonical_project_name | export_control | message | title |               topic_id               |  type  | url  |
+--------------------------------------+-------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+--------+------+
| 427f6e45-5c49-4c3a-a92b-232d985761f0 | hwcert-1536148774 | active |          None          |      True      |   None  |  None | 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | hwcert | None |
+--------------------------------------+-------------------+--------+------------------------+----------------+---------+-------+--------------------------------------+--------+------+
```

Finally update the `settings.yml` file via the dci_components variable.

```
dci_components:
  - 9d30b332-d6d4-4a05-b54f-b26b38f1f71c
  - a40bc44b-df2f-406a-96e5-e0dfe7b36bda
  - 427f6e45-5c49-4c3a-a92b-232d985761f0
```

### Target a specific server registred in Beaker

If you need to assign the job to a specific server which is registered in Beaker, you can use ONE of the following options.

#### Using FQDN

This will match a single server by checking the hostname.

```
hostRequires:
  fqdn: my.host.example.com
```

#### Using hardware requirements

This will return the first server available that match the hardware requirement.

```
hostRequires:
  network: Extreme Gigabit Ethernet
  video: VD 0190
```

The various elements along with their attributes and the values they can take are described in the RELAX NG schema described in the file [beaker-job.rng](https://beaker-project.org/docs/_downloads/beaker-job.rng).

### Red Hat Certification: How to skip its execution

Some users might want to skip the certification tests suite. This can be done via `settings.yml` file by adding `dci_rhel_agent_cert: false`.

## Usage

To start `dci-rhel-agent`, please use `systemctl start dci-rhel-agent`.


## Use tags

If you want to associate tags to jobs you can edit the file `/etc/dci-rhel-agent/settings.yml` and add your tags in the `dci_tags` list.
By default the tag "debug" is associated with all jobs, you should keep it like this until the integration of the agent is done.
The debug tag will prevent jobs to be count in the statistics.


## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team  <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
