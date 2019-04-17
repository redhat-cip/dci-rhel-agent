import os

import requests
from dciauth.signature import Signature
from dciauth.request import AuthRequest


DCI_CLIENT_ID = os.getenv("DCI_CLIENT_ID")
DCI_API_SECRET = os.getenv("DCI_API_SECRET")
DCI_CS_URL = os.getenv("DCI_CS_URL")


def get(endpoint, params=None):
    auth_request = AuthRequest(endpoint=endpoint, params=params)
    client_type, client_id = DCI_CLIENT_ID.split("/")
    headers = Signature(request=auth_request).generate_headers(
        client_id=client_id, client_type=client_type, secret=DCI_API_SECRET
    )
    return requests.get("%s%s" % (DCI_CS_URL, endpoint), params=params, headers=headers)


def post(endpoint, payload):
    auth_request = AuthRequest(
        method="POST",
        endpoint=endpoint,
        payload=payload,
        headers={"content-type": "application/json"},
    )
    client_type, client_id = DCI_CLIENT_ID.split("/")
    headers = Signature(request=auth_request).generate_headers(
        client_id=client_id, client_type=client_type, secret=DCI_API_SECRET
    )
    return requests.post("%s%s" % (DCI_CS_URL, endpoint), json=payload, headers=headers)
