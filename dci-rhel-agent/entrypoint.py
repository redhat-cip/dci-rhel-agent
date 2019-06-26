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

from os import environ
from dciclient.v1.api.context import build_signature_context
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic as dci_topic


def sigterm_handler(signal, frame):
    # This does NOT work with ansible_runner.run_async().
    print("Handle podman stop here !")
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)


def load_settings():
    with open("/etc/dci-rhel-agent/settings.yml", "r") as settings:
        try:
            return yaml.load(settings, Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)


def check_parameters(extravars):
    stop = False
    error_messages = []
    if environ.get("DCI_CLIENT_ID") is None:
        stop = True
        error_messages.append("DCI_CLIENT_ID environmental variable is not set.")

    if "topic" not in extravars.keys():
        stop = True
        error_messages.append("topic is defined in /etc/dci-rhel-agent/settings.yml.")

    if "systems" not in extravars.keys():
        if "download_only" not in extravars.keys() or not extravars["download_only"]:
            stop = True
            error_messages.append(
                "systems is not defined /etc/dci-rhel-agent/settings.yml."
            )

    if stop:
        print("Please ensure:")
        for message in error_messages:
            print(" * %s" % message)
        sys.exit(1)


def main():
    # Path is static in the container
    local_repo = "/var/www/html"
    extravars = load_settings()
    extravars["local_repo"] = local_repo
    check_parameters(extravars)

    topic_name = extravars["topic"]
    print("Topic is %s" % topic_name)
    context = build_signature_context()
    t = dci_topic.list(context, where="name:%s" % topic_name)
    if t.status_code != 200:
        print(
            "Error ! HTTP error code=%s, message=%s, while getting topics"
            % (t.status_code, t.text)
        )
        sys.exit(1)

    topics = t.json()["topics"]
    if len(topics) == 0:
        print(
            "Topic %s is no available. Ensure topic name is correct and you have the permission to download it"
            % topic_name
        )
    topic = topics[0]

    components = context.session.post(
        "%s/jobs/schedule" % context.dci_cs_api,
        json={"topic_id": topic["id"], "dry_run": True},
    ).json()["components"]

    remoteci_id = os.getenv("DCI_CLIENT_ID").split("/")[1]
    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent",
        playbook="dci-downloader.yml",
        extravars={
            "remoteci_id": remoteci_id,
            "local_repo": local_repo,
            "components": components,
            "topic_id": topic["id"],
            "product": topic["product_id"],
            "topic": topic_name,
        },
    )
    if r.rc != 0:
        print("Error ! Download components has failed. {}: {}".format(r.status, r.rc))
        sys.exit(1)

    if "download_only" in extravars.keys():
        if extravars["download_only"] == True:
            print("The dci-rhel-agent is configured in download-only mode.")
            sys.exit(0)

    r = ansible_runner.run(
        private_data_dir="/usr/share/dci-rhel-agent/",
        inventory="/etc/dci-rhel-agent/hosts",
        verbosity=1,
        playbook="dci-import.yml",
        extravars=extravars,
        quiet=False,
    )
    if r.rc != 0:
        print(
            "Error ! Distro(s) import in Beaker has failed. {}: {}".format(
                r.status, r.rc
            )
        )
        sys.exit(1)

    runner_threads = []
    for x in extravars["systems"]:
        print("Starting job for %s." % x)
        extravars["fqdn"] = x
        thread, _ = ansible_runner.run_async(
            private_data_dir="/usr/share/dci-rhel-agent/",
            inventory="/etc/dci-rhel-agent/hosts",
            verbosity=1,
            playbook="dci-rhel-agent.yml",
            extravars=extravars,
            quiet=False,
        )
        runner_threads.append(thread)

    for rt in runner_threads:
        rt.join()
    print("All jobs terminated.")


if __name__ == "__main__":
    main()
