# DCI RHEL Agent

`dci-rhel-agent` provides Red Hat Enterprise Linux (RHEL) in Red Hat Distributed CI service.

## Requirements

The simplest working setup must be composed of at least 2 systems:

- The first one is **DCI jumpbox**. This system acts as a `controller node` and will run mandatory services such as DHCP server, local DNS resolver and Beaker.

- The second one is the **system under test** (SUT). Beaker will provision this system with **RHEL** and execute all the tests on top of it. This system is installed and wiped at each `dci-rhel-agent` job.

Please note that it's common to have multiple **SUTs** (for instance: systems with different hardware profiles).

### Jumpbox requirements

The jumpbox can be a physical server or a virtual machine.
In any case, it must:

- Be running the latest stable RHEL release (**7.9 or higher**) and registered via RHSM.
- Have at least 160GB of free space available in `/var`
- Have access to Internet
- Be able to connect the following Web urls:
  - DCI API, https://api.distributed-ci.io
  - DCI Packages, https://packages.distributed-ci.io
  - DCI Repository, https://repo.distributed-ci.io
  - EPEL, https://dl.fedoraproject.org/pub/epel/
  - QUAY.IO, https://quay.io
- Have a stable internal IP
- Be able to reach all SUTs using (mandadory, but not limited to):
  - SSH
  - IPMI
  - Serial-Over-LAN or other remote consoles (details & software to be provided by the partner)
- Be reachable by the SUTs using:
  - DHCP
  - PXE
  - HTTP/HTTPS

### SUT requirements

A SUT can be a physical server or a virtual machine. It will be **installed** through DCI workflow with each job.
As the files on this system are NOT persistent between each `dci-rhel-agent` job, every customization has to be automated from the DCI jumpbox.

### SUTs network

- SUTs network must allow network booting protocols such as DHCP/PXE.
- SUTs network should be fully isolated, to prevent conflicts with other networks.
- SUTs network bandwidth can be impaired since the `dci-rhel-agent` will download RHEL snapshots (=~ 4GB each) once in a while.

### Optional

We strongly advise the partners to provide Red Hat DCI's team an access to their jumpbox. This way, Red Hat engineers can help with initial setup and troubleshooting.

## Installation of DCI Rhel Agent

The `dci-rhel-agent` is packaged and available as a RPM files.
However,`dci-release` and `epel-release` must be installed first:

```bash
sudo yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
sudo yum -y install yum-utils
sudo yum-config-manager --save --setopt=epel.exclude=nodejs*,npm
sudo subscription-manager repos --enable=rhel-7-server-extras-rpms
sudo subscription-manager repos --enable=rhel-7-server-optional-rpms
sudo yum -y install dci-rhel-agent
sudo yum -y install ansible git
```

## Installation Of Beaker

You can install and run beaker externally to DCI but we provide containers that allow it to run from the jumphost.

```bash
git clone https://github.com/redhat-cip/ansible-playbook-dci-beaker
cd ansible-playbook-dci-beaker/
ansible-galaxy install -r requirements.yml -p roles/
# Edit the settings in group_vars/all
vi group_vars/all
ansible-playbook -i inventory playbook.yml
```

## Configuration

In order to ensure the agent is able to connect to all applicable hosts, please copy the ssh key located in `/etc/dci-rhel-agent/secrets/id_rsa` to the hosts running Beaker and dnsmasq. Normally, these will be on the same machine running the agent.

```console
ssh-copy-id -i /etc/dci-rhel-agent/secrets/id_rsa <user>@<host>
```

There are two configuration files for `dci-rhel-agent`: `/etc/dci-rhel-agent/dcirc.sh` and `/etc/dci-rhel-agent/settings.yml`.

- `/etc/dci-rhel-agent/dcirc.sh`

Note: The initial copy of `dcirc.sh` is shipped as `/etc/dci-rhel-agent/dcirc.sh.dist`. Copy this to `/etc/dci-rhel-agent/dcirc.sh` to get started.

This file has the credential associated to the jumpbox (also kwnown as a `Remoteci` in the [DCI web dashboard](https://www.distributed-ci.io). The partner team administrator has to create a Remote CI in the DCI web dashboard, copy the relative credential and paste it locally on the jumpbox to `/etc/dci-rhel-agent/dcirc.sh`.

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

- `/etc/dci-rhel-agent/inventory`
  This file should be edited once upon installation. The ansible_host (192.168.1.1 as delivered) should be updated to the IP of the machine running the DCI RHEL agent.
- `/etc/dci-rhel-agent/settings.yml`

This YAML file includes the configuration for one or more `dci-rhel-agent` Jobs.
The possible values are:

| Variable                      | Required | Type           | Description                                                                                                                         |
| ----------------------------- | -------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| topic                         | True     | String         | Name of the topic.                                                                                                                  |
| dci_tags                      | False    | List           | List of tags to set on the job                                                                                                      |
| dci_name                      | False    | String         | Name of the job                                                                                                                     |
| dci_configuration             | False    | String         | String representing the configuration of the job                                                                                    |
| dci_comment                   | False    | String         | Comment to associate with the job                                                                                                   |
| dci_url                       | False    | URL            | URL to associate with the job                                                                                                       |
| local_repo_ip                 | True     | IP             | DCI jumpbox static network IP.                                                                                                      |
| local_repo                    | True     | String         | Path to store DCI artefacts (Local RHEL mirror that will be exposed to SUT by `httpd`). Default is `/var/www/html`.                 |
| dci_rhel_agent_cert           | True     | True/False     | Enable or disable the HW certification tests suite.                                                                                 |
| dci_rhel_agent_cki            | True     | True/False     | Enable or disable the CKI tests suite.                                                                                              |
| systems                       | False    | List of string | List of all systems that will be deployed using RHEL from DCI.                                                                      |
| beaker_xml                    | False    | String         | Path to a custom XML file to use with Beaker job.                                                                                   |
| variants                      | False    | List of string | List of RHEL 8.x variant to enable (AppStream, BaseOS, CRB, HighAvailability, NFV, RT, ResilientStorage, SAP, SAPHANA and unified). |
| archs                         | False    | List of string | CPU arch to enable (aarch64, ppc64le, s390x and x86_64).                                                                            |
| with_debug                    | False    | True/False     | Use RPM with debug symbols.                                                                                                         |
| beaker_lab.external_dns       | False    | True/False     | Boolean representing whether an external DNS server is in use.                                                                      |
| beaker_lab.dns_server         | False    | IP             | IP address of DNS server to specify in beaker.conf (dnsmasq config)                                                                 |
| beaker_lab.ntp_server         | False    | IP             | IP address of NTP server to specify in beaker.conf (dnsmasq config)                                                                 |
| beaker_lab.domain             | False    | String         | Domain to append to hosts                                                                                                           |
| beaker_lab.dhcp_start         | False    | IP             | Starting IP address range to assign to DCI test systems via DHCP.                                                                   |
| beaker_lab.dhcp_end           | False    | IP             | Ending IP address range to assigne to DCI test systems via DHCP.                                                                    |
| beaker_lab.jumpbox_fqdn       | False    | FQDN           | FQDN of DCI jumpbox.                                                                                                                |
| beaker_lab.labcontroller_fqdn | False    | FQDN           | Public interface FQDN of Beaker lab controller.                                                                                     |
| beaker_lab.router             | False    | IP             | Gateway address                                                                                                                     |
| system_inventory              | False    | various        | List of all DCI tests systems and corresponding Beaker information                                                                  |

Example:

```console
local_repo_ip: 192.168.1.1
local_repo: /opt/beaker/dci
topics:
  - topic: RHEL-8.1
    dci_rhel_agent_cert: false
    dci_rhel_agent_cki: false
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
    variants:
      - Server
    archs:
      - x86_64
    with_debug: false
    systems:
      - fqdn: my.x86_64.system2.local
        kernel_options: "rd.iscsi.ibft=1"
        ks_meta: "ignoredisk=--only-use=sda"
        sol_command: "ipmitool -I lanplus -U root -P calvin -H my.x86_64.system2.local sol activate"
        sut_password: sut_pw
        reboot_watchdog_timeout: 14400
        install_watchdog_timeout: 28800
        install_wait_time: 180
      - my.x86_64.system3.local
      - my.x86_64.system4.local
beaker_lab:
  dhcp_start: 192.168.1.20
  dhcp_end: 192.168.1.30
  dhcp_netmask: 255.255.255.0
  external_dns: True
  dns_server: 192.168.1.1
  ntp_server : 192.168.1.1
  domain: sample.domain.com

  jumpbox_fqdn: dci-jumpbox
  labcontroller_fqdn: dell-pet410-wdci-01.khw2.lab.eng.bos.redhat.com

  system_inventory:
    test.x86.sut1:
      ip_address: 192.168.1.20
      mac: aa:bb:cc:dd:ee:ff
      arch: x86_64
      power_address: sut1.power.address
      power_user: p_user1
      power_password: p_pass1
      # Power ID depends on which power type is selected.  Typically this field identifies
      # a particular plug, socket, port, or virtual guest name. Defaults to fqdn when not
      # specified here
      #power_id:
      power_type: ipmilan
    test.x86.sut2
      ip_address: 192.168.1.21
      mac: ff:ee:dd:cc:bb:aa
      arch: x86_64
      power_address: sut2.power.address
      power_user: p_user2
      power_password: p_pass2
      #power_id:
      power_type: wti
    test.ppc.sut3
      ip_address: 192.168.1.23
      mac: aa:cc:bb:dd:ee:ff
      arch: ppc64le
      power_address: sut4.power.address
      power_user: p_user4
      power_password: p_pass4
      #power_id:
      power_type: apc_snmp
    test.ppc.sut4
      ip_address: 192.168.1.24
      mac: aa:cc:bb:dd:ee:ff
      arch: ppc64le
      power_address: sut5.power.address
      power_user: p_user5
      power_password: p_pass5
      #power_id:
      power_type: apc_snmp
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

Please note that all FQDN must resolve locally on the DCI jumpbox. If you don't have proper DNS records, please update `/etc/hosts` then reload `dnsmasq` service. Also, the supported architecture of the systems must be entered in Beaker in order for the agent to properly provision a system with the correct architecture.

Please also note that the RHEL agent does not currently support concurrent provisioning of different topics. All provision jobs in the same topic will run concurrently, but each topic will run consecutively. Running two instances of the agent simultaneously will cause installation issues on the systems under test. This feature will be added in the near future and this readme will be updated to reflect the support.

#### Red Hat HW Certification tests

The DCI RHEL agent offers a suite of tests from the Red Hat HW certification tests. These tests can be enabled via `settings.yml` file by adding `dci_rhel_agent_cert: true`. The tests will be run after the test system is provisioned. Test results will be uploaded to DCI and are available to both the partner and Red Hat. By enabling these tests a partner is able to catch any errors they may need to address before participating in the official HW certification process through Red Hat and get a head start on any formal HW certification plans that a partner may have. This test suite will be updated regularly and is a subset of the full test suite which would be required for official certification, which depends on the type of hardware to be certified. The DCI cert test suite contains a set of tests applicable to all hardware. Currently, the suite of tests includes:

Non-interactive tests:

- memory
- core
- cpuscaling
- fv_core
- fv_memory
- fv_cpu_pinning
- hw_profiler
- sw_profiler

Storage tests:

- STORAGE
- SATA
- SATA_SSD
- SAS

In addition to these tests, the info, self-check, and sosreport tests are mandatory and will execute every test run.

Further information the tests noted can be found at: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_hardware_certification/7.18/html-single/test_suite_user_guide/index#sect-User_Guide-Appendixes-Hardware_Test_Procedures

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

For example:

```
beaker_server ansible_host=X.X.X.X ansible_ssh_user=my_user ansible_ssh_private_key_file=/etc/dci-rhel-agent/secrets/id_rsa
[beaker_sut]
```

The SSH private key files need to be located in the `/etc/dci-rhel-agent/secrets/` folder.

Please leave `[beaker_sut]` group empty.

#### How to customize the system deployment ?

If you want you can customize the system deployment by adding some kernel option or kickstart metadata.

For example:

```
    systems:
      - fqdn: my.x86_64.system2.local
        kernel_options: "rd.iscsi.ibft=1"
        ks_meta: "ignoredisk=--only-use=sda"
      - my.x86_64.system3.local
      - my.x86_64.system4.local
```

#### How to enable conserver ?

The beaker-watchdog daemon on the Beaker lab controller can monitor the console logs from conserver for every running recipe. For that you will need to add the SOL (serial over lan) command and the kernel option in the setting file :

For example:

```
    systems:
      - fqdn: my.x86_64.system2.local
        kernel_options: "console=ttyS1,115200n8"
        sol_command: "ipmitool -I lanplus -U root -P calvin -H my.x86_64.system2.local sol activate"
      - my.x86_64.system3.local
      - my.x86_64.system4.local
```

#### How to extend the Beaker watchdog timeout for a system deployment?

If deployment of systems is timing out due to Beaker's watchdog timeout expiring, the timeout for a test system can be set to a user-specified amount in the settings file. There is a watchdog which monitors the time from reboot to system installation start (`reboot_watchdog_timeout`), and a watchdog which monitors the time from installation start (`install_watchdog_timeout`). Either or both can be modified from the settings file.  The amount of time the agent waits for the installation to start is defaulted to 12.5 minutes (25 retries, 30 seconds apart).  This wait time can be adjusted in the settings file (specified in minutes) to allow for more time as is sometimes needed when provisioning large VMs for example.

For example, the following will cause the agent to wait 3 hours for the installation to start, set the reboot watchdog timeout to 4 hours and the install watchdog timeout to 8 hours (after installation begins) for any deployment jobs on the my.x86_64.system.local test machine:

```

    systems:
      - fqdn: my.x86_64.system.local
        reboot_watchdog_timeout: 14400
        install_watchdog_timeout: 28800
        install_wait_time: 180
```

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

## How to execute tasks before SUT deployment ?

By default, `dci-rhel-agent` provides an empty Ansible list of tasks located at `/etc/dci-rhel-agent/hooks/pre-run.yml`.
It can be modified to include any task needed to run **before** the system Under Test is provisionned for the job.

## How to run your own set of tests ?

By default, `dci-rhel-agent` provides 2 hooks files you can use to run your tests:
  - `/etc/dci-rhel-agent/hooks/tests.yml`
  - `/etc/dci-rhel-agent/hooks/user-tests.yml`

Those files are kept when the `dci-rhel-agent` RPM will be updated.

### tests.yml

You can include any tasks that will be run on the jumpbox

### user-tests.yml

You can include any tasks that will be run on each SUTs

To use any existing Ansible roles in your tests, copy the role directory to `/etc/dci-rhel-agent/hooks/roles`. The role can then be imported into your hooks file.

Please note, that it is possible at this point to use DCI Ansible bindings (see in the container `/usr/share/dci/modules/`) in tasks.
In the following example, the task uploads Junit files (your tests results) into DCI Web dashboard.

```
- name: Copy tests results from SUT to jumpbox it-self
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

### How to run tests only (no provisioning)?

If a user has a pre-provisioned system and would like to only run user-tests and enabled Red Hat tests, the agent can be started with the --tests-only command line option. An entry for the system and job needs to exist in the settings file so the agent can determine the appropriate Red Hat tests to run, if enabled (RHEL-7 vs. RHEL-8).

`dci-rhel-agent-ctl --start --tests-only`

## FAQ

### I need to move our jumpbox and give it a new IP. How do we update our RHEL agent install?

The new IP address should be updated in the following files:
/etc/hosts (if applicable)
/etc/dnsmasq.d/beaker.conf
/etc/beaker/labcontroller.conf
/etc/beaker/client.conf
/etc/dci-rhel-agent/inventory
/etc/dci-rhel-agent/settings.yml

### My DCI job is failing, what should I do?

The status of each job executed through DCI is captured on our web UI (distributed-ci.io). When a failure occurs, a good first step is to find the job in the DCI UI by logging in, clicking on the "Jobs" link on the left side of the page, and then filtering the jobs by your team. The most recent job will be at the top of the list. Clicking on the topic name with take you to a log of the output of each Ansible task that was executed during the job. By clicking on each task, you can see a more verbose output which can help to troubleshoot where your job failed and why.
The DCI team is reachable via distributed-ci@redhat.com. When contacting DCI regarding a failing job it is helpful to have as much information as possible to help the team troubleshoot. A link to the failing job, anything new that has changed in your lab, and whether or not this job has succeeded in the past are all helpful in assisting the DCI team to find the root cause.

### My job is hanging at the dci-downloader task.

There could be .lock files in your local_repo (usually `/var/www/html` unless overridden in settings) which are not being cleared. Check in your `local_repo/<topic_name>` and manually delete any .lock files if present.

### I have a new test system I would like to add to my DCI Beaker Lab.

Adding new SUT to your DCI Beaker Lab can all be handled in your settings file. Each settings file contains a "beaker_lab" section which describes various network configs for your SUT, along with a list of all SUTs and their relevant information. Add any new systems to this list, and run the agent as usual. The agent will see that there are SUTs in your settings file which are not integrated into your DCI Beaker lab and will make the appropriate changes to add them to the SUTs network, and include them in Beaker. New systems can be added and provisioned in a single run given they are configured appropriately in your settings file. See the RHEL agent documentation above for settings file structure.

### Can I use virtual machines as test systems in my DCI lab?

Yes. A common setup is to use the libvirt/qemu/kvm stack for VM test machines. A bridge network can be set up on the hypervisor to allow VMs to be seen and provisioned by the agent on the jumpbox.

### Does the agent download an entire RHEL compose every time a new nightly or milestone compose is available?

No. Due to the large size of RHEL composes, our dci-downloader tool called by the RHEL agent downloads only the files which have changed since your lab's last download of the topic. So your first run of the agent will include a lengthy download, but subsequent runs will be much faster.

### I would like to continue to use the same RHEL compose for testing in our Beaker lab for a while.

The RHEL agent provides an option which can be supplied when it is started to skip the download of composes. By supplying the `--skip-download` flag to your start call of the agent, the downloader will be bypassed and you can continue to run with the most recently downloaded RHEL compose until you are ready to move on. At that point, omitting the skip-download flag will allow your agent to download the latest available composes for each topic specified in your settings file.

### My EFI system does not recognize the default "linuxefi" and "initrdefi" commands supplied in the grub.cfg by the RHEL agent.

The linuxefi and initrdefi commands are supplied by default in the grub.cfg constructed by the agent for EFI systems.  These can be swapped with the linux and initrd commands by supplying a boolean in the system inventory for that system:

    alternate_efi_boot_commands: true

### My system times out waiting before install starts

There is a known bug, BZ 1785663.  This can be worked around by adding rd.net.timeout.carrier=10 to that systems kernel_options

    kernel_options: rd.net.timeout.carrier=10

## Create your DCI account on distributed-ci.io

Every user needs to create an account by connecting to `https://www.distributed-ci.io` using a Red Hat SSO account.

The account will be created in the DCI database at the first connection. For now, there is no reliable way to know your team automatically.
Please contact the DCI team when this step has been reached, to be assigned in the correct organization.

## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team <distributed-ci@redhat.com>
IRC: #distributed-ci on Freenode
