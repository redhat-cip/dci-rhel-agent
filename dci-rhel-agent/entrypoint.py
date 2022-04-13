#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrypoint for dci-rhel-agent.
Example for settings.yml:
local_repo: /var/www/html
local_repo_ip: 192.168.1.1
topics:
  - topic: RHEL-7.9
    archs:
      - x86_64
      - ppc64le
    variants:
      - Server
    dci_rhel_agent_cert: false
    dci_rhel_agent_cki: false
    systems:
      - fqdn: labvm-1.novalocal
        kernel_options: "rd.iscsi.ibft=1"
        ks_meta: "ignoredisk=--only-use=sda"
        sol_command: "ipmitool -I lanplus -U root -P calvin -H labvm-1.novalocal sol activate"
        watchdog_timeout: 3600
      - labvm-2.novalocal

  - topic: RHEL-8.5
    archs:
      - ppc64le
    variants:
      - BaseOS
      - AppStream
    dci_rhel-agent_cert: false
    dci_rhel-agent_cki: false
    systems:
      - SUT3
      - SUT4
"""
import ansible_runner
import signal
import sys
import yaml

from os import environ

number_of_failed_jobs = 0

def sigterm_handler(signal, frame):
    # This does NOT work with ansible_runner.run_async().
    print('Handle podman stop here !')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

def cleanup_boot_files():
    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/inventory",
        verbosity=1,
        playbook="dci-cleanup.yml",
        quiet=False
    )
    if r.rc != 0:
        print("Warning: Unable to remove boot files copied to tftproot by agent.")

def load_settings():
    with open('/etc/dci-rhel-agent/settings.yml', 'r') as settings:
        try:
            return(yaml.load(settings, Loader=yaml.SafeLoader))
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)

def provision_and_test(extravars, cmdline):
    # Path is static in the container
    # local_repo = '/var/www/html'
    # extravars['local_repo'] = local_repo

    if 'topic' in extravars.keys():
        print ("Topic is %s" % extravars['topic'])
    else:
        print ("Error ! No topic found in settings.")
        sys.exit(1)

    # Provision and install SUT
    if 'systems' not in extravars.keys():
        print ('No hosts found in settings. Please add systems to provision and/or test to your settings file.')
        sys.exit(1)

    # Setup conserver if a sol_command exist
    if [system for system in extravars['systems'] if type(system) is dict and 'sol_command' in system.keys()]:
        systems = {'systems' : [system for system in extravars['systems'] if type(system) is dict and 'sol_command' in system.keys()]}
        r = ansible_runner.run(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/inventory",
            verbosity=1,
            playbook="conserver.yml",
            extravars=systems,
            quiet=False
        )
        if r.rc != 0:
            print ("Conserver playbook failed. {}: {}".format(r.status, r.rc))
            sys.exit(1)

    threads_runners = {}
    for system in extravars['systems']:
        if type(system) is dict and 'fqdn' in system :
            extravars['fqdn'] = system['fqdn']
            if 'kernel_options' in system:
                extravars['kernel_options'] = system['kernel_options']
            else:
                extravars.pop('kernel_options', None)
            if 'ks_meta' in system:
                extravars['ks_meta'] = system['ks_meta']
            else:
                extravars.pop('ks_meta', None)
            if 'sol_command' in system:
                extravars['sol_command'] = system['sol_command']
            else:
                extravars.pop('sol_command', None)
            if 'sut_password' in system:
                extravars['sut_password'] = system['sut_password']
            else:
                extravars.pop('sut_password', None)
            if 'reboot_watchdog_timeout' in system:
                extravars['reboot_watchdog_timeout'] = system['reboot_watchdog_timeout']
            else:
                extravars.pop('reboot_watchdog_timeout', None)
            if 'install_watchdog_timeout' in system:
                extravars['install_watchdog_timeout'] = system['install_watchdog_timeout']
            else:
                extravars.pop('install_watchdog_timeout', None)
            if 'install_wait_time' in system:
                extravars['install_wait_time'] = system['install_wait_time']
            else:
                extravars.pop('install_wait_time', None)
        else:
            extravars['fqdn'] = system
            #Remove any install options set for previous SUTs in this topic if they exist
            extravars.pop('kernel_options', None)
            extravars.pop('ks_meta', None)
            extravars.pop('sol_command', None)
            extravars.pop('reboot_watchdog_timeout', None)
            extravars.pop('install_watchdog_timeout', None)
            extravars.pop('install_wait_time', None)
        print ("Starting job for %s." % extravars['fqdn'])
        thread, runner = ansible_runner.run_async(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/inventory",
            verbosity=int(environ.get('VERBOSITY')),
            playbook="dci-rhel-agent.yml",
            extravars=extravars,
            quiet=False,
            cmdline=cmdline
        )
        threads_runners[(thread, runner)] = extravars['fqdn']

    # wait for all jobs
    for t, _ in threads_runners:
        t.join()
    print("All jobs terminated.")

    global number_of_failed_jobs
    # check if some jobs failed
    for t, r in threads_runners:
        fqdn = threads_runners[(t, r)]
        if r.rc != 0:
            print("Job for %s failed, rc: %s, status: %s " % (fqdn, r.rc, r.status))
            number_of_failed_jobs += 1


def main():
    if environ.get('DCI_CLIENT_ID') is None:
        print ("Environment variable DCI_CLIENT_ID not set.")
        sys.exit(1)

    cmdline = ""
    tests_only = True if environ.get('TESTS_ONLY') == 'True' else False
    if tests_only:
        cmdline += ' --skip-tags "sut,beaker"'
    skip_download = True if environ.get('SKIP_DOWNLOAD') == 'True' else False
    if skip_download:
        cmdline += ' --skip-tags "download"'

    # Read the settings file
    sets = load_settings()

    ext_bkr = True if environ.get('EXT_BKR') == 'True' else False
    if not ext_bkr:
        # Run the update playbook once before jobs.
        # todo gvincent: move this in the main playbook
        r = ansible_runner.run(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/inventory",
            verbosity=1,
            playbook="dci-update.yml",
            extravars=sets,
            quiet=False,
            cmdline=cmdline
        )
        if r.rc != 0:
            print ("Update playbook failed. {}: {}".format(r.status, r.rc))
            sys.exit(1)

    # Check if the settings contain multiple topics and process accordingly
    if 'topics' in sets:
        # Break up settings file into individual jobs by topic
        jobs = sets['topics']
        # Loop over each job and provision system(s)
        for idx, current_job in enumerate(jobs):
            print ("Beginning provision/test jobs for topic %s" % current_job['topic'])
            current_job['local_repo'] = sets['local_repo']
            current_job['local_repo_ip'] = sets['local_repo_ip']
            current_job['ext_bkr'] = ext_bkr
            current_job['beaker_lab'] = sets['beaker_lab']
            provision_and_test(current_job, cmdline)
            cleanup_boot_files()
    else:
        print ('Incompatible settings file.  Topics not found. Please update settings file format.')
        sys.exit(1)
    sys.exit(number_of_failed_jobs)


if __name__ == '__main__':
    main()
