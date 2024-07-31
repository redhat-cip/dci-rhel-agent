#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrypoint for dci-rhel-agent.
Example for settings.yml:
local_repo: /opt/dci
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

def load_settings():
    with open('/etc/dci-rhel-agent/settings.yml', 'r') as settings:
        try:
            return(yaml.load(settings, Loader=yaml.SafeLoader))
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)

def provision_and_test(extravars, cmdline):
    # Path is static in the container
    # local_repo = '/opt/dci'
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

    # Convert list of <str|dict> into dict of dicts
    _systems = dict()
    for system in extravars['systems']:
        if type(system) is dict and 'fqdn' in system:
            _systems[system['fqdn']] = system
        else:
            _systems[system] = dict(fqdn=system)
    extravars['systems'] = _systems

    if not [system for system in extravars['systems'].values() if 'sol_command' in system.keys()]:
        cmdline += ' --skip-tags "conserver"'

    print ("Starting job for %s." % extravars['topic'])
    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/inventory",
        verbosity=int(environ.get('VERBOSITY')),
        playbook="dci-rhel-agent.yml",
        extravars=extravars,
        envvars={'ANSIBLE_CALLBACK_PLUGINS': "/usr/share/dci/callback"},
        quiet=False,
        cmdline=cmdline
    )

    global number_of_failed_jobs
    # check if some jobs failed
    if r.rc != 0:
        print("Job for %s failed, rc: %s, status: %s " % (extravars['topic'], r.rc, r.status))
        number_of_failed_jobs += 1


def main():
    if environ.get('DCI_CLIENT_ID') is None:
        print ("Environment variable DCI_CLIENT_ID not set.")
        sys.exit(1)

    cmdline = ""
    tests_only = True if environ.get('TESTS_ONLY') == 'True' else False
    if tests_only:
        cmdline += ' --skip-tags "beaker"'
    skip_download = True if environ.get('SKIP_DOWNLOAD') == 'True' else False
    if skip_download:
        cmdline += ' --skip-tags "download"'

    # Read the settings file
    sets = load_settings()

    # Check if the settings contain multiple topics and process accordingly
    if 'topics' in sets:
        # Break up settings file into individual jobs by topic
        jobs = sets['topics']
        # Loop over each job and provision system(s)
        for idx, current_job in enumerate(jobs):
            print ("Beginning provision/test jobs for topic %s" % current_job['topic'])
            current_job['local_repo'] = sets['local_repo']
            if 'jumpbox' in sets:
                current_job['jumpbox'] = sets['jumpbox']
            if 'domain' in sets:
                current_job['domain'] = sets['domain']
            provision_and_test(current_job, cmdline)
    else:
        print ('Incompatible settings file.  Topics not found. Please update settings file format.')
        sys.exit(1)
    sys.exit(number_of_failed_jobs)


if __name__ == '__main__':
    main()
