#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os

from sys import stderr
import xml.etree.ElementTree as etree
from ansible.module_utils.basic import AnsibleModule

from bkr.client import BeakerCommand
from bkr.common.hub import HubProxy
from bkr.common.pyconfig import PyConfigParser

# beaker client config finding code lifted from beaker-client
user_config_file = os.environ.get("BEAKER_CLIENT_CONF", None)
if not user_config_file:
    user_conf = os.path.expanduser('~/.beaker_client/config')
    old_conf = os.path.expanduser('~/.beaker')
    if os.path.exists(user_conf):
        user_config_file = user_conf
    elif os.path.exists(old_conf):
        user_config_file = old_conf
        sys.stderr.write(
            "%s is deprecated for config, please use %s instead\n" % (old_conf, user_conf))
    else:
        pass

system_config_file = None
if os.path.exists('/etc/beaker/client.conf'):
    system_config_file = '/etc/beaker/client.conf'

conf = PyConfigParser()
if system_config_file:
    conf.load_from_file(system_config_file)
if user_config_file:
    conf.load_from_file(user_config_file)

class BeakerTargets(object):
    def __init__(self, params, logger=None):
        # params from AnsibleModule argument_spec below
        self.jid = params['job_id']
        self.task = params['task']

        # set up beaker connection
        self.hub = HubProxy(logger=logger, conf=conf)

    def get_job_status(self):
        """
        Returns the status of a Beaker job (jid)
        """

        myxml = self.hub.taskactions.to_xml(self.jid, False, True, True)
        myxml = myxml.encode('utf8')
        tree = etree.fromstring(myxml)
        elt = tree.find(".//task[@name='%s']" % (self.task))
        status = elt.get("status")

        return status

def main():
    mod = AnsibleModule(argument_spec={
        'job_id': {'type': 'str'},
        'task': {'type': 'str'},
    })
    beaker = BeakerTargets(mod.params)
    try:
        results = beaker.get_job_status()
        mod.exit_json(status=results, changed=True)
    except Exception as ex:
        msg = ": For more details please check jobs on beaker"
        msg = str(ex) + msg
        mod.fail_json(msg=msg, changed=True)


# import module snippets
main()
