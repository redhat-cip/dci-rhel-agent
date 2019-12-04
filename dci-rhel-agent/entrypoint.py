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
    download_only: false
    systems:
      - labvm-1.novalocal
      - labvm-2.novalocal

  - topic: RHEL-8.1
    archs:
      - ppc64le
    variants:
      - BaseOS
      - AppStream
    dci_rhel-agent_cert: false
    download_only: false
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

def configure_beaker_server():
    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/inventory",
        verbosity=1,
        playbook="dci-config-update.yml",
        quiet=False
    )
    if r.rc != 0:
        print("Unable to properly configure DCI jumpbox, exiting...")
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

    # This function is kept for backward compatibility.
    if 'download_only' in extravars.keys():
        if extravars['download_only'] == True:
            print ('The dci-rhel-agent is configured in download-only mode.')
            sys.exit(0)

    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/inventory",
        verbosity=1,
        playbook="dci-import.yml",
        extravars=extravars,
        quiet=False
    )
    if r.rc != 0:
        print ("Distro(s) import in Beaker has failed. {}: {}".format(r.status, r.rc))
        sys.exit(1)

    if 'systems' not in extravars.keys():
        print ('No hosts found in settings. You should configure download-only mode or add systems[].')
        sys.exit(1)
    fqdns = extravars['systems']

    threads_runners = {}
    for fqdn in fqdns:
        print ("Starting job for %s." % fqdn)
        extravars['fqdn'] = fqdn
        thread, runner = ansible_runner.run_async(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/inventory",
            verbosity=1,
            playbook="dci-rhel-agent.yml",
            extravars=extravars,
            quiet=False
        )
        threads_runners[(thread, runner)] = fqdn

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
    # Read the settings file
    sets = load_settings()
    # Ensure Beaker server is configured correctly before provisioning SUTs
    configure_beaker_server()
    # Check if the settings contain multiple topics and process accordingly
    if 'topics' in sets:
        # Break up settings file into individual jobs by topic
        jobs = sets['topics']
        # Loop over each job and provision system(s)
        for idx, current_job in enumerate(jobs):
            print ("Beginning provision/test jobs for topic %s" % current_job['topic'])
            current_job['local_repo'] = sets['local_repo']
            current_job['local_repo_ip'] = sets['local_repo_ip']
            provision_and_test(current_job)
            #Clean up all boot files copied for this topic
            cleanup_boot_files()
    else:
        # Legacy settings file format (single topic/job)
        # preserved for compatibility
        provision_and_test(sets)
        #Clean up all boot files copied for this topic
        cleanup_boot_files()
    sys.exit(number_of_failed_jobs)


if __name__ == '__main__':
    main()
