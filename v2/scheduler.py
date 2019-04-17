import os
import ansible_runner

from dciclient.v1.api.context import build_signature_context
from dciclient.v1.api import remoteci
from dciclient.v1.api import topic

topic = os.getenv('TOPIC')
remoteci_id = os.getenv("DCI_CLIENT_ID").split("/")[1]
context = build_signature_context()
topic_id = topic.list(context, where="name:%s" % topic).json()["topics"][0]["id"]
components_ids = context.session.post(
    "%s/jobs/schedule" % context.dci_cs_api,
    json={"topic_id": topic_id, "dry_run": True},
).json()["components_ids"]
ansible_runner.run(
    private_data_dir="/opt/dci-rhel-agent",
    playbook="agent.yml",
    extravars={
        "remoteci_id": remoteci_id,
        "local_repo": "/var/www/html",
        "components_ids": components_ids,
    },
)
