from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

import time

display = Display()

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()
        module_return = dict(status="New")
        while True:
            module_return = self._execute_module(module_name='bkr_info',
                                         module_args=module_args,
                                         task_vars=task_vars, tmp=tmp)
            print ("BKR_INFO:%s" % module_return)
            if (module_return["status"] in ["Completed", "Aborted"]):
                break
            time.sleep(10)

        return module_return
