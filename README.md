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

- Be running the latest stable RHEL release (**8.7 or higher**) and registered via RHSM.
- Have at least 160GB of free space available in `/opt`
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
However,`dci-release` and `epel-release` must be installed first.

```bash
dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
dnf -y install https://packages.distributed-ci.io/dci-release.el8.noarch.rpm
dnf -y install dci-rhel-agent
ssh-keygen -t rsa -N "" -f /etc/dci-rhel-agent/secrets/id_rsa
ssh-copy-id -i /etc/dci-rhel-agent/secrets/id_rsa.pub root@localhost
```

The ssh-keygen and ssh-copy-id commands setup authentication so that the containers have permission to run commands on the jumphost.

## Configuration

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

| Variable                               | Required | Type           | Description                                                                                                                         |
| -------------------------------------- | -------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| topic                                  | True     | String         | Name of the topic.                                                                                                                  |
| dci_tags                               | False    | List           | List of tags to set on the job                                                                                                      |
| dci_name                               | False    | String         | Name of the job                                                                                                                     |
| dci_configuration                      | False    | String         | String representing the configuration of the job                                                                                    |
| dci_comment                            | False    | String         | Comment to associate with the job                                                                                                   |
| dci_url                                | False    | URL            | URL to associate with the job                                                                                                       |
| jumpbox                                | False    | String         | Hostname of DCI jumpbox. This is the name of the jumpbox on the SUT network.  The default is dci-jumpbox.                           |
| domain                                 | False    | String         | Domain of DCI jumpbox. This is the name of the domain on the SUT network.  The default is dci.local.                                |
| local_repo                             | True     | String         | Path to store DCI artefacts (Local RHEL mirror that will be exposed to SUT by `httpd`). Default is `/opt/dci`.                      |
| libvirt_images_dir                     | False    | String         | Path to store libvirt images for virtual hosts. Default is `/opt/libvirt/images`.                      |
| dci_rhel_agent_cert                    | True     | True/False     | Enable or disable the HW certification tests suite.                                                                                 |
| dci_rhel_agent_cki                     | True     | True/False     | Enable or disable the CKI tests suite.                                                                                              |
| disable_root_login_pw                  | False    | True/False     | When set to true, disables password based logins for root user setup by Beaker.  Key based logins only (setup by agent).
| machine_network_cidr                   | True     | String         | The private network to use for your Systems Under Test,  This is managed by dci.  The default is 10.60.0.0/24.                      |
| systems                                | False    | List of Dict   | List of all systems that will be deployed using RHEL from DCI.                                                                      |
| systems[].fqdn                         | True     | String         | Fully qualified Domain name of System under Test.                                                                                   |
| systems[].efi                          | False    | True/False     | Use efi netboot images instead of pxelinux.0                                                                                        |
| systems[].alternate_efi_boot_commands  | False    | True/False     | Use alternate linux and initrd commands instead if linuxefi and initrdefi                                                           |
| systems[].petitboot                    | False    | True/False     | Use alternate bootloader with ppc                                                                                                   |
| systems[].ks_meta                      | False    | String         | Metadata to pass to anaconda kickstart templating                                                                                   |
| systems[].ks_append                    | False    | String         | Appends custom commands to default kickstart used to provision test system
| systems[].kernel_options               | False    | String         | Arguments to pass to the install kernel                                                                                             |
| systems[].sol_command                  | False    | String         | Command to use for serial console over lan                                                                                          |
| beaker_xml                             | False    | String         | Path to a custom XML file to use with Beaker job.                                                                                   |
| variants                               | False    | List of string | List of RHEL 8.x variant to enable (AppStream, BaseOS, CRB, HighAvailability, NFV, RT, ResilientStorage, SAP, SAPHANA and unified). |
| archs                                  | False    | List of string | CPU arch to enable (aarch64, ppc64le, s390x and x86_64).                                                                            |
| with_debug                             | False    | True/False     | Use RPM with debug symbols.                                                                                                         |
| beaker_lab.beaker_dir                  | True     | String         | Path to store the beaker data files. Default is '/opt/beaker'                                                                       |
| beaker_lab.build_bridge                | False    | True/False     | Whether or not to setup the bridge network, defaults to True.                                                                       |
| beaker_lab.bridge_interface            | False    | String         | Network interface where all your SUT's will be connected.  Example provided in settings.                                            |
| beaker_lab.dns_server                  | False    | IP             | IP address of DNS server to specify in beaker.conf (dnsmasq config)                                                                 |
| beaker_lab.ntp_server                  | False    | IP             | IP address of NTP server to specify in beaker.conf (dnsmasq config)                                                                 |
| beaker_lab.dhcp_start                  | False    | IP             | Starting IP address range to assign to DCI test systems via DHCP.                                                                   |
| beaker_lab.dhcp_end                    | False    | IP             | Ending IP address range to assigne to DCI test systems via DHCP.                                                                    |
| beaker_lab.router                      | False    | IP             | Gateway address                                                                                                                     |
| system_inventory                       | False    | various        | List of all DCI tests systems and corresponding Beaker information                                                                  |

Example:

```console
local_repo: /opt/dci
jumpbox: dci-jumpbox
domain: dci.local
machine_network_cidr: 10.60.0.0/24
machine_network_ip: "{{ machine_network_cidr | nthhost(190) }}"
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
      - fqdn: sut1.{{ domain }}
        efi: true
        alternate_efi_boot_commands: true
      - fqdn: sut3.{{ domain }}
        petitboot: true
  - topic: RHEL-7.8
    dci_rhel_agent_cert: false
    dci_rhel_agent_cki: false
    disable_root_login_pw: true
    variants:
      - Server
    archs:
      - x86_64
    with_debug: false
    systems:
      - fqdn: sut1.{{ domain }}
        kernel_options: "rd.iscsi.ibft=1"
        ks_meta: "ignoredisk=--only-use=sda no autopart
        ks_append: |
          part /boot --recommended
          part /home --size=20480
          part / --grow
        sol_command: "ipmitool -I lanplus -U root -P calvin -H my.x86_64.system2.local sol activate"
        sut_password: sut_pw
        reboot_watchdog_timeout: 14400
        install_watchdog_timeout: 28800
        install_wait_time: 180
      - fqdn: sut2.{{ domain }}
      - fqdn: sut3.{{ domain }}

beaker_lab:
  beaker_dir: /opt/beaker
  dns_server: "{{ machine_network_ip }}"
  router: "{{ machine_network_ip }}"
  dhcp_start: "{{ machine_network_cidr | ipaddr('20') | ipaddr('address') }}"
  dhcp_end: "{{ machine_network_cidr | ipaddr('100') | ipaddr('address') }}"

  # By default we will build a bridge for the virtual systems in this example
  # settings Uncomment and set the bridge_interface to your physical network
  # interface which will have your Systems Under Test's.  If you set your
  # network up outside of this you can set build_bridge to false.
  build_bridge: true
  #  bridge_interface: eno2
  #

  system_inventory:
    sut1:
      ip_address: 10.60.0.51
      mac: "52:54:00:EF:C0:2C"
      arch: x86_64
      power_address: "{{ jumpbox }}.{{ domain }}"
      power_user: admin
      power_password: password
      power_id: 6230
      power_type: ipmitool_lanplus
      virt:
        mode: efi
        disks:
          main: 150
        memory: "16384"
        vcpu: "4"

    sut2:
      ip_address: 10.60.0.52
      mac: "52:54:00:EF:C0:2D"
      arch: x86_64
      power_address: "{{ jumpbox }}.{{ domain }}"
      power_user: admin
      power_password: password
      power_id: 6231
      power_type: ipmitool_lanplus
      virt:
        mode: legacy
        disks:
          main: 150
        memory: "16384"
        vcpu: "4"

    sut3:
      ip_address: 10.60.0.53
      mac: aa:cc:bb:dd:ee:ff
      arch: ppc64le
      power_address: sut3.power.address
      power_user: p_user3
      power_password: p_pass3
      #power_id:
      power_type: apc_snmp
```

## Setup of Containerized beaker and example virtual systems

The dci-rhel-agent-setup program will read your `/etc/dci-rhel-agent/settings.yml` file and setup the beaker containers and two virtual systems.  This will give you a fully working environment capable of downloading RHEL components from DCI and installing them on the virtual systems.

Setting the `port.name` under `beaker_lab.network_config` to the network interface that hosts your systems under test will allow you to test bare metal systems.  You will need to add entries for every test system under the `beaker_lab` section of the `settings.yml` file.  This includes mandatory fields like ip address, mac address, ipmi settings for power cycling.  There are also some optional settings.  Please see the table above for a complete list.

Since the virtual setup is self contained it can uncover issues with the main installation before adding in external hosts.  External hosts present their own issues.

Edit the inventory, by default it creates two Systems Under Test
make sure `libvirt_images_dir`, `local_repo` and `beaker_lab.beaker_dir` points to a location with enough disk space

```bash
dci-rhel-agent-setup
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

### Upgrading from Version 0.5.0

If you have changed the `/etc/dci-rhel-agent/inventory` file you will need to change the `beaker_server` entry to jumpbox.

The following settings in `/etc/dci-rhel-agent/settings.yml` have changed:

`local_repo_ip` has been replaced with `machine_network_ip`.

Both `beaker_lab.jumpbox_fqdn` and `beaker_lab.labcontroller_fqdn` have been dropped.

The dnsmasq configuration for the Test Network is now stored in `/etc/dnsmasq.d`  The playbooks will create the new config automatically but you will need to remove the entries in `/etc/NetworkManager/dnsmasq.d`

### Further settings

#### How to target a specific system in Beaker ?

##### Single system

If you have registred several systems in Beaker, you might want to configure where the DCI job will be executed.
You can use the `systems` option in `settings.yml` to match a single server by checking the hostname.

```
systems:
  - fqdn: labvm.dci.local
```

##### Multiple systems

If you want to execute the DCI job on multiple servers, add all FQDN in the `systems` configuration.

```
systems:
  - fqdn: labvm.dci.local
  - fqdn: labvm-2.dci.local
  - fqdn: labvm-3.dci.local
```

If you use the default settings and allow dci-rhel-agent-setup to configure the test network then all dns should work.
If you setup your network yourself make sure all FQDN must resolve locally on the DCI jumpbox. If you don't have proper DNS records, please update `/etc/hosts` then reload `dnsmasq` service. Also, the supported architecture of the systems must be entered in Beaker in order for the agent to properly provision a system with the correct architecture.

All provision jobs in the same topic will run concurrently, but each topic will run consecutively. Running two instances of the agent simultaneously with different settings files is possible.  If you do this a best practice is to separate the settings by topic.  ie: `settings-rhel8.yml` and `settings-rhel9.yml` and run them with `--config settings-rhel8.yml` for example.

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

#### How to use an external Beaker service ?

It is possible to configure the `dci-rhel-agent` to use an external Beaker service (therefore not to use the Beaker service that runs in a container on the `dci-jumpbox`).  This is as simple as updating the beaker client config on the jumpbox to use this external beaker (`/etc/beaker/client.conf`).  Please see Beaker's documentation for further details.

#### How to customize the system deployment ?

If you want you can customize the system deployment by adding some kernel option or kickstart metadata.

For example:

```
    systems:
      - fqdn: x86_64_2.dci.local
        kernel_options: "rd.iscsi.ibft=1"
        ks_meta: "ignoredisk=--only-use=sda"
      - fqdn: x86_64_3.dci.local
      - fqdn: x86_64_4.dci.local
```

#### How to enable conserver ?

The beaker-watchdog daemon on the Beaker lab controller can monitor the console logs from conserver for every running recipe. For that you will need to add the SOL (serial over lan) command and the kernel option in the setting file :

For example:

```
    systems:
      - fqdn: x86_64_2.dci.local
        kernel_options: "console=ttyS1,115200n8"
        sol_command: "ipmitool -I lanplus -U root -P calvin -H console_2.dci.local sol activate"
      - fqdn: x86_64_3.dci.local
      - fqdn: x86_64_4.dci.local
```

#### How to extend the Beaker watchdog timeout for a system deployment?

If deployment of systems is timing out due to Beaker's watchdog timeout expiring, the timeout for a test system can be set to a user-specified amount in the settings file. There is a watchdog which monitors the time from reboot to system installation start (`reboot_watchdog_timeout`), and a watchdog which monitors the time from installation start (`install_watchdog_timeout`). Either or both can be modified from the settings file.  The amount of time the agent waits for the installation to start is defaulted to 12.5 minutes (25 retries, 30 seconds apart).  This wait time can be adjusted in the settings file (specified in minutes) to allow for more time as is sometimes needed when provisioning large VMs for example.

For example, the following will cause the agent to wait 3 hours for the installation to start, set the reboot watchdog timeout to 4 hours and the install watchdog timeout to 8 hours (after installation begins) for any deployment jobs on the my.x86_64.system.local test machine:

```

    systems:
      - fqdn: x86_64_2.dci.local
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

To use any existing Ansible roles in your tests, copy the role directory to /etc/dci-rhel-agent/hooks/roles. The role can then be imported into your hooks file.

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

The test network is separate from your public network and should not need to be updated.

### My DCI job is failing, what should I do?

The status of each job executed through DCI is captured on our web UI (distributed-ci.io). When a failure occurs, a good first step is to find the job in the DCI UI by logging in, clicking on the "Jobs" link on the left side of the page, and then filtering the jobs by your team. The most recent job will be at the top of the list. Clicking on the topic name with take you to a log of the output of each Ansible task that was executed during the job. By clicking on each task, you can see a more verbose output which can help to troubleshoot where your job failed and why.
The DCI team is reachable via distributed-ci@redhat.com. When contacting DCI regarding a failing job it is helpful to have as much information as possible to help the team troubleshoot. A link to the failing job, anything new that has changed in your lab, and whether or not this job has succeeded in the past are all helpful in assisting the DCI team to find the root cause.

### My job is hanging at the dci-downloader task.

There could be .lock files in your local_repo (usually /opt/dci unless overridden in settings) which are not being cleared. Check in your local_repo/<topic_name> and manually delete any .lock files if present.

### I have a new test system I would like to add to my DCI Beaker Lab.

Adding new SUT to your DCI Beaker Lab can all be handled in your settings file. Each settings file contains a "beaker_lab" section which describes various network configs for your SUT, along with a list of all SUTs and their relevant information. Add any new systems to this list, and run the dci-rhel-agent-setup as usual. The agent will see that there are SUTs in your settings file which are not integrated into your DCI Beaker lab and will make the appropriate changes to add them to the SUTs network, and include them in Beaker. New systems can be added to your topics..systems section to be used with the agent now. See the RHEL agent documentation above for settings file structure.

### Can I use virtual machines as test systems in my DCI lab?

Yes. A common setup is to use the libvirt/qemu/kvm stack for VM test machines. The default settings creates two virtual machines.

### Does the agent download an entire RHEL compose every time a new nightly or milestone compose is available?

No. Due to the large size of RHEL composes, our dci-downloader tool called by the RHEL agent downloads only the files which have changed since your lab's last download of the topic. So your first run of the agent will include a lengthy download, but subsequent runs will be much faster.

### I would like to continue to use the same RHEL compose for testing in our Beaker lab for a while.

The RHEL agent provides an option which can be supplied when it is started to skip the download of composes. By supplying the `--skip-download` flag to your start call of the agent, the downloader will be bypassed and you can continue to run with the most recently downloaded RHEL compose until you are ready to move on. At that point, omitting the skip-download flag will allow your agent to download the latest available composes for each topic specified in your settings file.

### My EFI system does not recognize the default "linuxefi" and "initrdefi" commands supplied in the grub.cfg by the RHEL agent.

The linuxefi and initrdefi commands are supplied by default in the `grub.cfg` constructed by the agent for EFI systems.  These can be swapped with the linux and initrd commands by supplying a boolean in the system inventory for that system:

    alternate_efi_boot_commands: true

### My system times out waiting before install starts

There is a known bug, BZ 1785663.  This can be worked around by adding `rd.net.timeout.carrier=10` to that systems `kernel_options`

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
