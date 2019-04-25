# -*- coding: utf-8 -*-
import os
import sys
import ansible_runner
import yaml

from dciclient.v1.api.context import build_signature_context
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic

# Example for settings.yml ("hostRequires" is depreciated, "systems" (list) replaces it):
# 
# topic: RHEL-7
# local_repo_ip: 192.168.60.1
# local_repo: /var/www/html
# dci_rhel_agent_cert: false
# systems:
#   - labvm.novalocal
#   - labvm-2.novalocal

extravars = yaml.load(open('/etc/dci-rhel-agent/settings.yml'), Loader=yaml.SafeLoader)

if 'topic' in extravars.keys():
  print ("Topic is %s." % extravars['topic'])
else:
  print ("No topic found in settings.")
  sys.exit(1)

# remoteci_id = os.getenv("DCI_CLIENT_ID").split("/")[1]
# context = build_signature_context()
# topic_id = topic.list(context, where="name:%s" % topic).json()["topics"][0]["id"]
# components_ids = context.session.post(
#     "%s/jobs/schedule" % context.dci_cs_api,
#     json={"topic_id": topic_id, "dry_run": True},
# ).json()["components_ids"]

# ansible_runner.run(
#     private_data_dir="/usr/share/dci-rhel-agent",
#     playbook="dci-downloader.yml",
#     extravars={
#         "remoteci_id": remoteci_id,
#         "local_repo": "/var/www/html",
#         "components_ids": components_ids,
#     }
# )

if 'systems' in extravars.keys():
  fqdn = extravars['systems']
else:
  # To do: If fqdn not set, get the list from "bkr system-list --free" or sys.exit(1)
  fqdn = ['labvm.novalocal', 'labvm-2.novalocal']

for x in fqdn:
    print ("Starting job for %s." % x)
    extravars['fqdn']=x
    ansible_runner.run_async(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/hosts",
        verbosity=1,
        playbook="dci-rhel-agent.yml",
        extravars=extravars
    )