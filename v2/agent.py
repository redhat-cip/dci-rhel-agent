import os

import requests

from scheduler import asap
from api import get, post


def get_components_ids(topic_id):
    return post(
        "/api/v1/jobs/schedule", {"dry_run": True, "topic_id": topic_id}
    ).json()["components_ids"]


def get_topic_id(topic):
    return get("/api/v1/topics", {"where": "name:%s" % topic}).json()["topics"][0]["id"]


components_ids = get_components_ids(get_topic_id("RHEL-7"))
print(components_ids)
