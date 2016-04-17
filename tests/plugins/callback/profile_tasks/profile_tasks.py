# Adapted from:
# https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/callback/profile_tasks.rst
# (C) 2016  Matt Young <halcyondude@gmail.com>
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
module: profile_tasks
version_added: "2.0"
short_description: task profiling and timing callback plugin

description:
   - Provides per-task timing, ongoing playbook elapsed time, time line with all tasks sequentially
     and top 15 longest running tasks
'''

import time

from ansible.plugins.callback import CallbackBase

# define start time
t0 = tn = time.time()

def secondsToStr(t):
    # http://bytes.com/topic/python/answers/635958-handy-short-cut-formatting-elapsed-time-floating-point-seconds
    rediv = lambda ll, b: list(divmod(ll[0], b)) + ll[1:]
    return "%d:%02d:%02d.%03d" % tuple(reduce(rediv, [[t * 1000, ], 1000, 60, 60]))


def filled(msg, fchar="*"):
    if len(msg) == 0:
        width = 79
    else:
        msg = "%s " % msg
        width = 79 - len(msg)
    if width < 3:
        width = 3
    filler = fchar * width
    return "%s%s " % (msg, filler)


def timestamp(self):
    if self.current is not None:
        self.stats[self.current][1] = time.time() - self.stats[self.current][0]

def tasktime():
    global tn
    time_current = time.strftime('%A %d %B %Y  %H:%M:%S %z')
    time_elapsed = secondsToStr(time.time() - tn)
    time_total_elapsed = secondsToStr(time.time() - t0)
    tn = time.time()
    return filled('%s (%s)%s%s' % (time_current, time_elapsed, ' ' * 7, time_total_elapsed))

def seconds_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

class CallbackModule(CallbackBase):
    """
    This callback module provides per-task timing, ongoing playbook elapsed time
    and ordered list of top 15 longest running tasks at end.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'profile_tasks'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        self.stats = {}
        self.current = None

        super(CallbackModule, self).__init__()

    def _log(self, msg):
        # TODO: make this better, handle varargs
        # note: display(self, msg, color=None, stderr=False, screen_only=False, log_only=False)
        self._display.display(msg)

    def _record_task(self, name):
        """
        Logs the start of each task
        """
        self._log(tasktime())
        timestamp(self)

        # Record the start time of the current task
        # note: self.stats[taskname] = [ start_time, elapsed_time ]
        self.current = name
        self.stats[self.current] = [time.time(), None]

    def playbook_on_task_start(self, name, is_conditional):
        self._record_task(name)

    def v2_playbook_on_handler_task_start(self, task):
        self._record_task('HANDLER: ' + task.name)

    def playbook_on_setup(self):
        self._log(tasktime())

    def playbook_on_stats(self, stats):
        self._log(tasktime())
        self._log(filled("", fchar="="))

        timestamp(self)

        # sort tasks by start time
        timeline = sorted(
            self.stats.items(),
            key=lambda value: value[1][0]
        )

        # Print  all timings
        for name, times in timeline:
            self._log(
                "{0}, {1}, {2:>6}, {3:<70}".format(
                    time.strftime('%H:%M:%S', time.localtime(times[0])),
                    seconds_to_hms(times[1]),
                    '{0:.01f}'.format(times[1]),
                    name,
                )
            )

        # Sort the tasks by their running time
        results = sorted(
            self.stats.items(),
            key=lambda value: value[1][1],
            reverse=True,
        )

        # Just keep the top 15
        results = results[:15]

        self._log(filled(("-------- Top 15 Tasks (by elapsed time)"), fchar="-"))

        for name, times in results:
            self._log(
                "{0}, {1}, {2:>6}, {3:<70}".format(
                    time.strftime('%H:%M:%S', time.localtime(times[0])),
                    seconds_to_hms(times[1]),
                    '{0:.01f}'.format(times[1]),
                    name,
                )
            )
