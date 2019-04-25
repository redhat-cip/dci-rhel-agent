#!/usr/bin/env python

import time
import logging
from lxml import etree
import subprocess
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def get_task_status(task, job_id):
        xmlstr = subprocess.check_output(["bkr", "job-results", job_id])
        tree = etree.fromstring(xmlstr)
        elt = tree.find(".//task[@name='%s']" % (task))
        status = elt.get("status")
        logging.debug('Status for task %s: %s' % (task, status))
        return status

status = get_task_status('/distribution/install', sys.argv[1])
while status != "Completed":
        logging.debug('Waiting for 5s ...')
        time.sleep(5)
        status = get_task_status('/distribution/install', sys.argv[1])
        if status in ["Aborted", "Cancelled"]:
                exit(1)

exit(0)
