import os
import ansible_runner

from dciclient.v1.api.context import build_signature_context
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic

# topic = os.getenv('TOPIC')
# remoteci_id = os.getenv("DCI_CLIENT_ID").split("/")[1]
# context = build_signature_context()
# topic_id = topic.list(context, where="name:%s" % topic).json()["topics"][0]["id"]
# # RHEL-7
# topic_id="e6ff2abf-b109-4dd5-b06a-39f8846ad252"
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

# Run DCI jobs in //

ansible_runner.run_async(
    private_data_dir="/usr/share/dci-rhel-agent",
    playbook="dci-rhel-agent.yml",
    extravars={
        "topic": "RHEL-7",
        "local_repo": "/var/www/html",
        "local_repo_ip": "192.168.60.1",
        "dci_rhel_agent_cert":"false",
        "hostRequires.fqdn": "labvm.novalocal",
    }
)

ansible_runner.run_async(
    private_data_dir="/usr/share/dci-rhel-agent",
    playbook="dci-rhel-agent.yml",
    extravars={
        "topic": "RHEL-7",
        "local_repo": "/var/www/html",
        "local_repo_ip": "192.168.60.1",
        "dci_rhel_agent_cert":"false",
        "hostRequires.fqdn": "labvm-2.novalocal",
    }
)