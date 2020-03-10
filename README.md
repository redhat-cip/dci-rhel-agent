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
  * QUAY.IO, https://quay.io
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
# subscription-manager repos --enable=rhel-7-server-extras-rpms
# subscription-manager repos --enable=rhel-7-server-optional-rpms
# yum -y install dci-rhel-agent
# yum -y install ansible
```

Next, install [Beaker](https://beaker-project.org/). Red Hat DCI maintains a [dedicated Ansible role](https://docs.distributed-ci.io/ansible-playbook-dci-beaker/) to help with this task.

```bash
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

Note: The initial copy of `dcirc.sh` is shipped as `/etc/dci-rhel-agent/dcirc.sh.dist`. Copy this to `/etc/rhel-agent/dcirc.sh` to get started.

This file has the credential associated to the lab (also kwnown as a `RemoteCI` in the [DCI web dashboard](https://www.distributed-ci.io). The partner team administrator has to create a Remote CI in the DCI web dashboard, copy the relative credential and paste it locally on the Jumpbox to `/etc/dci-rhel-agent/dcirc.sh`.

This file should be edited once:

```bash
#!/usr/bin/env bash
DCI_CS_URL="https://api.distributed-ci.io/"
DCI_CLIENT_ID=remoteci/<remoteci_id>
DCI_API_SECRET=>remoteci_api_secret>
export DCI_CLIENT_ID
export DCI_API_SECRET
export DCI_CS_URL
```

* `/etc/dci-rhel-agent/settings.yml`

This YAML file includes the configuration for one or more `dci-rhel-agent` Jobs.
The possible values are:

| Variable | Required | Type | Description |
|----------|----------|------|-------------|
| topic | True | String | Name of the topic. |
| local_repo_ip | True | IP | DCI Jumpbox lab static network IP. |
| local_repo | True | String | Path to store DCI artefacts (Local RHEL mirror that will be exposed to SUT by `httpd`). Default is `/var/www/html`. |
| dci_rhel_agent_cert | True | True/False | Enable or disable the certification tests suite. |
| dci_rhel_agent_cki  | True | True/False | Enable or disable the cki tests suite.           |
| download_only | False | True/False | If enable, dci-rhel-agnt will exit after downloading RHEL builds (no job will be executed). |
| systems | False | List of string | List of all systems that will be deployed using RHEL from DCI. |
| beaker_xml | False | String | Path to a custom XML file to use with Beaker job. |
| variants | False | List of string | List of RHEL 8.x variant to enable (AppStream, BaseOS, CRB, HighAvailability, NFV, RT, ResilientStorage, SAP, SAPHANA and unified). |
| archs | False | List of string | CPU arch to enable (aarch64, ppc64le, s390x and x86_64). |
| with_debug | False | True/False | Use RPM with debug symbols.  |
Example:

```console
local_repo_ip: 192.168.1.1
local_repo: /var/www/html
topics:
  - topic: RHEL-8.1
    dci_rhel_agent_cert: false
    dci_rhel_agent_cki: false
    download_only: false
    variants:
      - AppStream
      - BaseOS
    archs:
      - x86_64
      - ppc64le
    with_debug: false
    systems:
      - my.x86_64.system.local
      - my.ppc64le.system.local
  - topic: RHEL-7.8
    dci_rhel_agent_cert: false
    dci_rhel_agent_cki: false
    download_only: false
    variants:
      - Server
    archs:
      - x86_64
    with_debug: false
    systems:
      - my.x86_64.system2.local
      - my.x86_64.system3.local
      - my.x86_64.system4.local
```

## Starting the DCI RHEL Agent and Accessing Beaker

Now that you have configured the DCI RHEL Agent, you need to start the service:

```
systemctl start dci-rhel-agent
```

You may access Beaker at:

```
http://<hostname>/bkr
```

### Further settings
#### How to target a specific system in Beaker ?
##### Single system
If you have registred several systems in Beaker, you might want to configure where the DCI job will be executed.
You can use the `systems` option in `settings.yml` to match a single server by checking the hostname.

```
systems:
  - labvm.local
```

##### Multiple systems
If you want to execute the DCI job on multiple servers, add all FQDN in the `systems` configuration.

```
systems:
  - labvm.local
  - labvm-2.local
  - labvm-3.local
```

Please note that all FQDN must resolve locally on the DCI jumpbox. If you don't have proper DNS records, please update `/etc/hosts` then reload `dnsmasq` service.  Also, the supported architecture of the systems must be entered in Beaker in order for the agent to properly provision a system with the correct architecture.

Please also note that the RHEL agent does not currently support concurrent provisioning.  Running two instances of the agent simultaneously will cause installation issues on the systems under test.  This feature will be added in the near future and this readme will be updated to reflect the support.

#### How to skip Red Hat Certification tests ?
Some users might want to skip the certification tests suite. This can be done via `settings.yml` file by adding `dci_rhel_agent_cert: false`.

#### How to skip Red Hat CKI tests ?
Some users might want to skip the cki tests suite. This can be done via `settings.yml` file by adding `dci_rhel_agent_cki: false`.

#### How to add tags to a job ?
If you want to associate tags to jobs you can edit the file `settings.yml` and add your tags in the `dci_tags` list.
By default, the tag "debug" is associated with every jobs. It should be kept 'as is' until the integration of the agent is done.
The debug tag prevents jobs results to be compiled in DCI trends.

#### How to use a custom Beaker XML file in DCI jobs ?
If you want to use your own XML file during the `bkr-job-submit (1)` step, you can use the property `beaker_xml` in `settings.yml`:

```
beaker_xml: /etc/dci-rhel-agent/hooks/path/to/job.xml
```

Please note the XML file has to be in `/etc/dci-rhel-agent/hooks/` directory.

#### How to use an external Beaker service ?
It is possible to configure the `dci-rhel-agent` to use an external Beaker service (therefore not to use the Beaker service that runs on the `dci-jumpbox`).

In this case, you can adapt directly the Ansible inventory file (`/etc/dci-rhel-agent/inventory`) of the agent.
Change the connexion line for the host `beaker_server`.
By default, it is configured `ansible_connection=local`.

For example:

```
beaker_server ansible_host=X.X.X.X ansible_ssh_user=my_user ansible_ssh_private_key_file=/etc/dci-rhel-agent/secrets/id_rsa
[beaker_sut]
```

The SSH private key files need to be located in the `/etc/dci-rhel-agent/secrets/` folder.

Please leave `[beaker_sut]` group empty.

## Usage
To start a single DCI RHEL Agent job, run:

```
systemctl start dci-rhel-agent
```

To explicitly run a job and for troubleshooting purposes, launch `dci-rhel-agent` in the foreground:

```bash
# dci-rhel-agent-ctl --start
```

The return code is the number of failed jobs. This is also a good time to go get a coffee as this will take a little while. You may also wish to use screen on RHEL 7 and earlier or tmux on RHEL 8 in order to be able to detach your session and return to it later.

If you need advanced debug, you can spawn a new container with a shell:

```bash
# dci-rhel-agent-ctl --start --debug
[container]#
[container]# ./entrypoint.py
[container]# dcictl topic-list
```

## How to run your own set of tests ?
By default, `dci-rhel-agent` provides an empty Ansible list of tasks located at `/etc/dci-rhel-agent/hooks/user-tests.yml`.
It can be modified to include any task needed to run on top of the lab server that was provisionned for the job.

This file will not be replaced when the `dci-rhel-agent` RPM will be updated.

Please note, that it is possible at this point to use DCI Ansible bindings (see in the container `/usr/share/dci/modules/`) in tasks.
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
