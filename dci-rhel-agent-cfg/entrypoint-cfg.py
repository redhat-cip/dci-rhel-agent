#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entrypoint for dci-rhel-agent-cfg.
"""
import ansible_runner
import os
import signal
import sys
import shutil

def sigterm_handler(signal, frame):
    # This does NOT work with ansible_runner.run_async().
    print('Handle podman stop here !')
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

def update_jumpbox_config():
  r = ansible_runner.run(
      private_data_dir="/usr/share/dci-rhel-agent-cfg/",
      inventory="/etc/dci-rhel-agent/hosts",
      verbosity=1,
      playbook="dci-update-cfg.yml",
      quiet=False
  )
  if r.rc != 0:
    print ("Error ! DCI jumpbox configuration update has failed. {}: {}".format(r.status, r.rc))
    sys.exit(1)

def main():
  update_jumpbox_config()

if __name__ == '__main__':
    main()
