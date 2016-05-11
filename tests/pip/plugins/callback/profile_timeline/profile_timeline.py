# https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/callback/profile_tasks.rst
#
# (C) 2016  Matt Young <halcyondude@gmail.com>
# (C) 2016, Joel, http://github.com/jjshoe 
# (C) 2015, Tom Paine, <github@aioue.net>
# (C) 2014, Jharrod LaFon, @JharrodLaFon
# (C) 2012-2013, Michael DeHaan, <michael.dehaan@gmail.com>
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# File is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# See <http://www.gnu.org/licenses/> for a copy of the
# GNU General Public License

# Provides per-task timing, ongoing playbook elapsed time and
# ordered list of top 15 longest running tasks at end

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: profile_timeline
version_added: "2.0"
short_description: task profiling and timing callback plugin

description:
   - Provides per-task timing, ongoing playbook elapsed time, time line with all tasks sequentially
     and top 15 longest running tasks
'''

import time
import collections
import os

from ansible.plugins.callback import CallbackBase

# define start time
t0 = tn = time.time()

# width for default printing
default_width = 79


def filled(msg, fchar="*"):
    return msg.ljust(default_width - 3, fchar) + fchar*3


def seconds_to_hms(seconds_delta, show_subsec=False):
    m, s = divmod(seconds_delta, 60)
    h, m = divmod(m, 60)
    if show_subsec:
        msg = "%d:%d:%.3f" % (h, m, s)
    else:
        msg = "%d:%02d:%02d" % (h, m, s)
    return msg


def time_to_hms(secs_since_epoch):
    msg = time.strftime('%H:%M:%S', time.localtime(secs_since_epoch))
    return msg


def tasktime():
    global tn
    time_current = time.strftime('%A %d %B %Y  %H:%M:%S %z')
    time_elapsed = seconds_to_hms(time.time() - tn, True)
    time_total_elapsed = seconds_to_hms(time.time() - t0, True)
    tn = time.time()
    msg = '%s (%s)%s%s ' % (time_current, time_elapsed, ' ' * 7, time_total_elapsed)
    return filled(msg)


class CallbackModule(CallbackBase):
    """
    This callback module provides per-task timing, ongoing playbook elapsed time,
    a timeline summary, and an ordered list of longest running tasks.  

    The following optional environment variables modify behavior:
        PROFILE_TASKS_SORT_ORDER: set to 'ascending' for shortest -> longest
        PROFILE_TASKS_TASK_OUTPUT_LIMIT: default is 20.  set to 'all' for the complete set
        PROFILE_TASKS_TIMELINE_SUMMARY: if defined will display a complete timeline summary with durations and role name
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'profile_timeline'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        self.stats = collections.OrderedDict()
        self.current = None
        self.sort_order = os.getenv('PROFILE_TASKS_SORT_ORDER', True)
        self.task_output_limit = os.getenv('PROFILE_TASKS_TASK_OUTPUT_LIMIT', 20)
        self.enable_timeline = os.getenv('PROFILE_TASKS_TIMELINE_SUMMARY')

        if self.sort_order == 'ascending':
            self.sort_order = False;

        if self.task_output_limit == 'all':
            self.task_output_limit = None
        else:
            self.task_output_limit = int(self.task_output_limit) 

        # if defined at all (1, True, 'enabled', ...)
        if self.enable_timeline is not None:
            self.enable_timeline = True

        super(CallbackModule, self).__init__()

    def _log(self, msg, color=None, stderr=False, screen_only=False, log_only=False):
        self._display.display(msg, color=color, stderr=stderr, screen_only=screen_only, log_only=log_only)

    # TODO: validate async things work the way this assumes they do
    # TODO: add asserts / warning module calls
    def _mark_item_complete(self):
        self._log(tasktime())
        if self.current is None:
            self._log("ERROR: self.current is None:\n%s" % str(ts))
        else:
            ts = self.stats[self.current]
            if ts['complete']:
                self._log("ERROR: double complete:\n%s" % str(ts))
            else:
                ts['end_time'] = time.time()
                ts['elapsed_time'] = ts['end_time'] - ts['start_time']

    def _record_task(self, task):
        """
        Logs the start of each task
        """
        self._mark_item_complete()

        # Record the start time of the current task
        self.current = task._uuid
        self.stats[self.current] = {'start_time': time.time(),
                                    'end_time': None,
                                    'elapsed_time': None,
                                    'name': task.get_name(),
                                    'complete': False}

        if self._display.verbosity >= 2:
            self.stats[self.current]['path'] = task.get_path()

    @staticmethod
    def _construct_timeline_line(uuid, item):
            msg = "[{0} - {1}], {2}, {3:>6}, ({4}) {5:<70}".format(
                time_to_hms(item['start_time']),
                time_to_hms(item['end_time']),
                seconds_to_hms(item['elapsed_time']),
                '{0:.01f}'.format(item['elapsed_time']),
                uuid,
                item['name'])

            if 'path' in item:
                msg += ", {0}".format(item['path'])

            return msg

    # TODO: since OrderedDict is used, the first sort technically should not be necessary.
    # TODO: It's also probably faster to simply reverse the already sorted list in the unlikely event that ascending sort_order is being used
    def _print_reports(self):
        if self.enable_timeline:
            # sort tasks by start time (oldest --> newest)

            # TODO: pre-sort, and post sort should be the same.  verify
            timeline = sorted(
                self.stats.items(),
                key=lambda x: x[1]['start_time']
            )

            # Print  all timings
            for uuid, item in timeline:
                self._log(self._construct_timeline_line(uuid, item))

        results = self.stats.items()

        # Sort the tasks by the specified sort (ascending, descending (default))
        if self.sort_order != 'none':
            results = sorted(
                self.stats.iteritems(),
                key=lambda x: x[1]['start_time'],
                reverse=self.sort_order
            )

        # Display the number of tasks specified or the default of 20
        results = results[:self.task_output_limit]

        self._log("=================== NEW report format ===============")

        # Print  all timings
        for uuid, item in results:
            self._log(self._construct_timeline_line(uuid, item))

        self._log("=================== OLD report format ===============")

        # Print the timings
        for uuid, result in results:
            msg = ''
            msg = "{0:-<70}{1:->9}".format('{0} '.format(result['name']), ' {0:.02f}s'.format(result['start_time']))
            if 'path' in result:
                msg += "\n{0:-<79}".format('{0} '.format(result['path']))
            self._display.display(msg)

    # Begin Hooks
    def v2_playbook_on_task_start(self, task, is_conditional):
        self._record_task(task)

    def v2_playbook_on_handler_task_start(self, task):
        self._record_task(task)

    def playbook_on_setup(self):
        self._log(tasktime())

    def playbook_on_stats(self, stats):
        self._log(tasktime())
        self._log(filled("", fchar="="))

        self._mark_item_complete()
        self._print_reports()

