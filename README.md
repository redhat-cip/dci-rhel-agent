
# DCI RHEL Agent
`dci-rhel-agent` provides Red Hat Enterprise Linux (RHEL) in Red Hat Distributed CI service.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How to run your own set of tests](#how-to-run-your-own-set-of-tests)
- [Create your DCI account on distributed-ci.io](#create-your-dci-account-on-distributed-ciio)
- [License](#license)
- [Contact](#contact)

## Requirements
### Systems requirements

The simplest working setup must be composed of at least 2 systems:

- The first one is **DCI Jumpbox**. This system acts as a `controller node` and will run mandatory services such as DHCP server, local DNS resolver and Beaker.

- The second one is the **target** (also known as a **lab server**). This system will be deployed with **RHEL from DCI**  and execute all the tests on top of it. This system is installed and wiped at each `dci-rhel-agent` job.

Please note that you can have only one **DCI Jumpbox** per lab, but it makes sense to have multiple **targets** (for instance: systems with different hardware profiles).

#### Jumpbox requirements

The Jumpbox can be a physical server or a virtual machine.
In any case, it must:

* Be running the latest stable RHEL release (**7.6 or higher**) and registered via RHSM.
* Have at least 160GB of free space available in `/var`
* Have access to Internet
* Be able to connect the following Web urls:
  * DCI API, https://api.distributed-ci.io
  * DCI Packages, https://packages.distributed-ci.io
  * DCI Repository, https://repo.distributed-ci.io
  * EPEL, https://dl.fedoraproject.org/pub/epel/
* Have a stable internal IP
* Be able to reach all lab servers using (mandadory, but not limited to):
  * SSH
  * IPMI
  * Serial-Over-LAN or other remote consoles (details & software to be provided by the partner)
* Be reachable by the lab servers using:
  * DHCP
  * PXE
  * HTTP/HTTPS

#### Lab server requirements

The lab server can be a physical server or a virtual machine. It will be **installed** through DCI workflow with each job.
As the files on this system are NOT persistent between each `dci-rhel-agent` job, every customization has to be automated from the DCI Jumpbox.

### Lab network requirements
* The lab network must allow network booting protocols such as DHCP/PXE.
* The lab network should be fully isolated, to prevent conflicts with other networks.
* The lab network bandwidth can be impaired since the `dci-rhel-agent` will download RHEL snapshots (=~ 4GB each) once in a while.

#### Optional

* We strongly advise the partners to provide Red Hat DCI's team an access to their jumpbox. This way, Red Hat engineers can help with initial setup and troubleshooting.

## Installation

The `dci-rhel-agent` is packaged and available as a RPM files.
However,`dci-release` and `epel-release` must be installed first:

```bash
# yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
# yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
# yum -y install dci-rhel-agent
```

Next, install [Beaker](https://beaker-project.org/). Red Hat DCI maintains a [dedicated Ansible role](https://docs.distributed-ci.io/ansible-playbook-dci-beaker/) to help with this task.

```bash
# subscription-manager repos --enable=rhel-7-server-extras-rpms
# subscription-manager repos --enable=rhel-7-server-optional-rpms
# su - dci-rhel-agent
$ git clone https://github.com/redhat-cip/ansible-playbook-dci-beaker
$ cd ansible-playbook-dci-beaker/
$ ansible-galaxy install -r requirements.yml -p roles/
$ vi group_vars/all
[...]
$ ansible-playbook -i inventory playbook.yml
```

If the **target** is a virtual machine, read this [notice](https://github.com/redhat-cip/ansible-playbook-dci-beaker#note-about-virtual-machines).

When you install `dci-rhel-agent` on a fresh system (or if you need to update cached Beaker Harness packages), execute the `beaker-repo-update` command.
For more details, read the official [documentation](https://beaker-project.org/docs/admin-guide/man/beaker-repo-update.html).

## Configuration

There are two configuration files for `dci-rhel-agent`: `/etc/dci-rhel-agent/dcirc.sh` and `/etc/dci-rhel-agent/settings.yml`.

  * `/etc/dci-rhel-agent/dcirc.sh`

This file has the credential associated to the lab (also kwnown as a `RemoteCI` in the [DCI web dashboard](https://www.distributed-ci.io). The partner team administrator has to create a Remote CI in the DCI web dashboard, download the relative `remotecirc.sh` file and rename it locally on the Jumpbox to `/etc/dci-rhel-agent/dcirc.sh`.

This file should NOT be edited:

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

This YAML file includes the configuration for a `dci-rhel-agent` Job.
The possible values are:

| Variable | Required | Type | Description |
|----------|----------|------|-------------|
| topic | True | String | Name of the topic. |
| local_repo | True | Path | Path to directory where components will be stored; Must be exposed by httpd. |
| local_repo_ip | True | IP | DCI Jumpbox lab static network IP. |
| dci_rhel_agent_cert | True | True/False | Enable or disable the certification tests suite. |

Example:

```console
topic: RHEL-7
local_repo_ip: 172.23.100.100
local_repo: /var/www/html
dci_rhel_agent_cert: false
```

### Advanced settings
#### How to use a specific DCI component (a specific RHEL build) ?

By default the agent will use the latest component (RHEL build) available. If you need to test an old component, then you need to specify its ID in the agent configuration (`/etc/dci-rhel-agent/settings.yml`).

First, get the topic ID:

```console
$ dcictl topic-list --where name:RHEL-7
+--------------------------------------+--------+--------+-------------------------------------+----------------+---------------+--------------------------------------+
|                  id                  |  name  | state  |           component_types           | export_control | next_topic_id |              product_id              |
+--------------------------------------+--------+--------+-------------------------------------+----------------+---------------+--------------------------------------+
| 9e170c05-6bbf-46f7-9a0e-a64a66decc44 | RHEL-7 | active | [u'Compose', u'hwcert', u'extraos'] |      True      |      None     | 7adbc8c4-8c9e-4366-aca3-158dfce036c9 |
+--------------------------------------+--------+--------+-------------------------------------+----------------+---------------+--------------------------------------+
```

Then you can list the components associated to that topic and get the IDs (for each component_types):

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

Finally update the `settings.yml` file via the `dci_components` variable:

```
dci_components:
  - 9d30b332-d6d4-4a05-b54f-b26b38f1f71c
  - a40bc44b-df2f-406a-96e5-e0dfe7b36bda
  - 427f6e45-5c49-4c3a-a92b-232d985761f0
```

#### How to target a specific system in Beaker ?
If you have registred several systems in Beaker, you might want to configure where the DCI job will be executed. You can use ONE of the following options:

##### Option A: Using FQDN
This will match a single server by checking the hostname.

```
hostRequires:
  fqdn: my.host.example.com
```

##### Or option B: Using hardware requirements
This will return the first server available that matches the hardware requirement.

```
hostRequires:
  network: Extreme Gigabit Ethernet
  video: VD 0190
```

The various elements along with their attributes (and their possible values) are described in the RELAX NG schema [beaker-job.rng](https://beaker-project.org/docs/_downloads/beaker-job.rng).

#### How to skip Red Hat Certification tests ?
Some users might want to skip the certification tests suite. This can be done via `settings.yml` file by adding `dci_rhel_agent_cert: false`.


#### How to add tags to a job ?
If you want to associate tags to jobs you can edit the file `/etc/dci-rhel-agent/settings.yml` and add your tags in the `dci_tags` list.
By default, the tag "debug" is associated with every jobs. It should be kept 'as is' until the integration of the agent is done.
The debug tag prevents jobs results to be compiled in DCI trends.

## Usage
To start a single job `dci-rhel-agent`, please use `systemctl start dci-rhel-agent`.

For troubleshooting purposes, launch `dci-rhel-agent` foreground:

```bash
# su - dci-rhel-agent
$ cd /usr/share/dci-rhel-agent
$ source /etc/dci-rhel-agent/dcirc.sh
$ /usr/bin/ansible-playbook -vv /usr/share/dci-rhel-agent/dci-rhel-agent.yml -e @/etc/dci-rhel-agent/settings.yml -i /etc/dci-rhel-agent/hosts
```

## How to run your own set of tests ?
By default, `dci-rhel-agent` provides an empty Ansible playbook located at `/etc/dci-rhel-agent/hooks/user-tests.yml`.
It can be modified to include any task needed to run on the lab server that was provisionned for the job.

This file will not be replaced when the `dci-rhel-agent` RPM will be updated.

Please note, that it is possible at this point to use DCI Ansible bindings (see `/usr/share/dci/modules/`) in tasks.
In the following example, the task uploads Junit files (your tests results) into DCI Web dashboard.

```
- name: Copy tests results from lab server to jumpbox it-self
  fetch:
    src: '{{ item }}'
    dest: '{{ item }}'
    flat: yes
  with_items:
    - /tmp/result-1.xml
    - /tmp/result-2.xml

- name: Upload files from the jumpbox to DCI
  dci_file:
    path: '{{ item }}'
    name: '{{ item }}'
    job_id: '{{ hostvars.localhost.job_id }}'
    mime: "application/junit"
  delegate_to: localhost
  with_items:
    - /tmp/result-1.xml
    - /tmp/result-2.xml
```

## Create your DCI account on distributed-ci.io
Every user needs to create his personnal account by connecting to `https://www.distributed-ci.io` using a Red Hat SSO account.

The account will be created in the DCI database at the first connection. For now, there is no reliable way to know your team automatically.
Please contact the DCI team when this step has been reached, to be assigned in the correct organisation.

## License
Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact
Email: Distributed-CI Team  <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
