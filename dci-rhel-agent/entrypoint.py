#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrypoint for dci-rhel-agent.
Example for settings.yml ("hostRequires" is depreciated, "systems" (list) replaces it):

topic: RHEL-7
local_repo_ip: 192.168.60.1
local_repo: /var/www/html
dci_rhel_agent_cert: false
download_only: false
systems:
  - labvm-1.novalocal
  - labvm-2.novalocal

"""
import ansible_runner
import os
import signal
import sys
import yaml

from dciclient.v1.api.context import build_signature_context
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic

def sigterm_handler(signal, frame):
    # This does NOT work with ansible_runner.run_async().
    print('Handle podman stop here !')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

def main():
  with open('/etc/dci-rhel-agent/settings.yml', 'r') as settings:
    try:
      extravars = yaml.load(settings, Loader=yaml.SafeLoader)
    except yaml.YAMLError as exc:
      print(exc)
      sys.exit(1)

    if 'topic' in extravars.keys():
      print ("Topic is %s." % extravars['topic'])
    else:
      print ("Error ! No topic found in settings.")
      sys.exit(1)

    remoteci_id = os.getenv("DCI_CLIENT_ID").split("/")[1]
    local_repo = os.getenv("DCI_LOCAL_REPO")
    context = build_signature_context()
    topic_id = topic.list(context, where="name:%s" % extravars['topic']).json()["topics"][0]['id']
    components_ids = context.session.post(
        "%s/jobs/schedule" % context.dci_cs_api,
        json={"topic_id": topic_id, "dry_run": True},
    ).json()["components_ids"]

    ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent",
        playbook="dci-downloader.yml",
        extravars={
            "remoteci_id": remoteci_id,
            "local_repo": local_repo,
            "components_ids": components_ids,
        }
    )

    if 'download_only' in extravars.keys():
      if extravars['download_only'] == True:
        print ('The dci-rhel-agent is configured in download-only mode.')
        sys.exit(0)

    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/hosts",
        verbosity=1,
        playbook="dci-import.yml",
        extravars=extravars,
        quiet=False
    )
    if r.rc != 0:
      print ('Error ! Import distro in Beaker failed.')
      sys.exit(1)

    if 'systems' in extravars.keys():
      fqdn = extravars['systems']
    else:
      print ('No hosts found in settings !')
      sys.exit(1)

    for x in fqdn:
        print ("Starting job for %s." % x)
        extravars['fqdn']=x
        ansible_runner.run_async(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/hosts",
            verbosity=1,
            playbook="dci-rhel-agent.yml",
            extravars=extravars,
            quiet=False
        )

if __name__ == '__main__':
    main()