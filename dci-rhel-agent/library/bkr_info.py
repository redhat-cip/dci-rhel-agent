#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os

from sys import stderr
import xml.etree.ElementTree as etree
from ansible.module_utils.basic import AnsibleModule

from bkr.client import BeakerCommand
from bkr.client import conf
from bkr.common.hub import HubProxy
from bkr.common.pyconfig import PyConfigParser

class BeakerTargets(object):
    def __init__(self, params, logger=None):
        # params from AnsibleModule argument_spec below
        self.jid = params['job_id']
        self.system = params['system']

        # set up beaker connection
        self.hub = HubProxy(logger=logger, conf=conf)

    def get_recipe_status(self):
        """
        Returns the status of a Beaker job (jid)
        """

        status = "Queued"
        result = "None"
        myxml = self.hub.taskactions.to_xml(self.jid, False, True, True)
        myxml = myxml.encode('utf8')
        tree = etree.fromstring(myxml)
        elt = tree.find(".//recipe[@system='%s']" % (self.system))
        if elt:
            status = elt.get("status")
            result = elt.get("result")
        return (result, status)

def main():
    mod = AnsibleModule(argument_spec={
        'job_id': {'type': 'str'},
        'system': {'type': 'str'},
    })
    beaker = BeakerTargets(mod.params)
    try:
        result, status = beaker.get_recipe_status()
        mod.exit_json(status=status, result=result, changed=True)
    except Exception as ex:
        msg = ": For more details please check jobs on beaker"
        msg = str(ex) + msg
        mod.fail_json(msg=msg, changed=True)


# import module snippets
main()
