#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrypoint for dci-rhel-agent.
Example for settings.yml:

topic: RHEL-7.6
local_repo_ip: 192.168.60.1
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
import subprocess
from lxml import etree

from os import environ
from dciclient.v1.api.context import build_signature_context
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic

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

def get_system_arch(fqdn):
  try:
    machine_details = subprocess.check_output(["bkr", "system-details", fqdn])
    tree = etree.fromstring(machine_details)
    systemArch = tree.find('{https://fedorahosted.org/beaker/rdfschema/inventory#}System')\
                     .find('{https://fedorahosted.org/beaker/rdfschema/inventory#}supportsArch')\
                     .find('{https://fedorahosted.org/beaker/rdfschema/inventory#}Arch')\
                     .find('{http://www.w3.org/2000/01/rdf-schema#}label').text
    return systemArch
  except:
    print("Unexpected Error: Could not determine supported architecture of \
           machine to be provisioned: %s.  Ensure supported architecture \
           is specified in Beaker." % fqdn)
    return ""

def main():
  if environ.get('DCI_CLIENT_ID') is not None:
    remoteci_id = os.getenv("DCI_CLIENT_ID").split("/")[1]
  else:
    print ("Error ! Environmental variable DCI_CLIENT_ID not set.")
    sys.exit(1)

  # Path is static in the container
  local_repo = '/var/www/html'
  extravars = load_settings()
  extravars['local_repo'] = local_repo

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
      inventory="/etc/dci-rhel-agent/hosts",
      verbosity=1,
      playbook="dci-import.yml",
      extravars=extravars,
      quiet=False
  )
  if r.rc != 0:
    print ("Error ! Distro(s) import in Beaker has failed. {}: {}".format(r.status, r.rc))
    sys.exit(1)

  if 'systems' in extravars.keys():
    fqdn = extravars['systems']
  else:
    print ('Error ! No hosts found in settings. You should configure download-only mode or add systems[].')
    sys.exit(1)

  runner_threads = []
  for x in fqdn:
      print ("Starting job for %s." % x)
      extravars['system_arch'] = get_system_arch(x)
      if extravars['system_arch']:
        print ("Supported architecture is %s." % extravars['system_arch'])
      else:
        #If we could not determine system arch of SUT, skip it and move on to the next SUT
        continue

      extravars['fqdn']=x
      thread,_ = ansible_runner.run_async(
          private_data_dir="/usr/share/dci-rhel-agent/",
          inventory="/etc/dci-rhel-agent/hosts",
          verbosity=1,
          playbook="dci-rhel-agent.yml",
          extravars=extravars,
          quiet=False
      )
      runner_threads.append(thread)

  for rt in runner_threads:
    rt.join()
  print("All jobs terminated.")

if __name__ == '__main__':
    main()
