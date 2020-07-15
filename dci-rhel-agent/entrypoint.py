#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrypoint for dci-rhel-agent.
Example for settings.yml:
local_repo: /var/www/html
local_repo_ip: 192.168.1.1
topics:
  - topic: RHEL-7.6
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
      - labvm-2.novalocal

  - topic: RHEL-8.1
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

def provision_and_test(extravars):
    # # Path is static in the container
    # local_repo = '/var/www/html'
    # extravars['local_repo'] = local_repo

    if 'topic' in extravars.keys():
        print ("Topic is %s" % extravars['topic'])
    else:
        print ("Error ! No topic found in settings.")
        sys.exit(1)

    if 'systems' not in extravars.keys():
        print ('No hosts found in settings. Please add systems to provision to your settings file.')
        sys.exit(1)

    threads_runners = {}
    for system in extravars['systems']:
        if type(system) is dict and 'fqdn' in system :
            extravars['fqdn'] = system['fqdn']
            if 'kernel_options' in system:
                extravars['kernel_options'] = system['kernel_options']
            if 'ks_meta' in system:
                extravars['ks_meta'] = system['ks_meta']
        else:
            extravars['fqdn'] = system
        print ("Starting job for %s." % extravars['fqdn'])
        thread, runner = ansible_runner.run_async(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/inventory",
            verbosity=1,
            playbook="dci-rhel-agent.yml",
            extravars=extravars,
            quiet=False
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

def exit_if_duplicates(jobs):
    topics_name = []
    for job in jobs:
        topic_name = job['topic']
        if topic_name in topics_name:
            print("Error ! Topics list in your settings file contains duplicates.")
            print("Topic %s is present at least 2 times." % topic_name)
            print("Please edit your setting file.")
            sys.exit(1)
        topics_name.append(topic_name)


def main():
    if environ.get('DCI_CLIENT_ID') is None:
        print ("Environment variable DCI_CLIENT_ID not set.")
        sys.exit(1)
    # Read the settings file
    sets = load_settings()
    # Check if the settings contain multiple topics and process accordingly
    if 'topics' in sets:
        # Break up settings file into individual jobs by topic
        jobs = sets['topics']
        exit_if_duplicates(jobs)
        # Loop over each job and provision system(s)
        for idx, current_job in enumerate(jobs):
            print ("Beginning provision/test jobs for topic %s" % current_job['topic'])
            current_job['local_repo'] = sets['local_repo']
            current_job['local_repo_ip'] = sets['local_repo_ip']
            provision_and_test(current_job)
    else:
        print ('Incompatible settings file.  Topics not found. Please update settings file format.')
        sys.exit(1)
    sys.exit(number_of_failed_jobs)


if __name__ == '__main__':
    main()
