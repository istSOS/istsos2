# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
"""
description:
    the scheduler dynamically check if scheduled job for each service
    are changed, and update the defined job.
    The scheduled job for a service are instantiated by a file named
    "serviceName.aps" that includes the jobs according the decoration methods
    of the python APScheduler library; for example:

    @sched.interval_schedule(seconds=4)
    def demo_job4():
        print 'demo job4'

    @sched.cron_schedule(second='*/30')
    def demo_decorated_task():
        print "I am printed at every minute at the 30th second!"

"""

#---------------------------------
import os
import logging
logging.basicConfig()


def recursive_glob(rootdir='.', suffix=''):

    return [(os.path.splitext(filename)[0], os.path.join(rootdir, filename))
            for rootdir, dirnames, filenames in os.walk(rootdir)
            for filename in filenames if filename.endswith(suffix)]

import hashlib
schedmd5 = {}
wns_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wns")

from lib.apscheduler.scheduler import Scheduler
from lib.apscheduler import threadpool

sched = Scheduler(daemonic=False)
sched._threadpool = threadpool.ThreadPool(core_threads=10,
                                            max_threads=50, keepalive=10)

sched.start()
print "Running..."


#===========================
#START THE ISTSOS SCHEDULER
#===========================
@sched.interval_schedule(seconds=5)
def istsos_job():
    global schedmd5
    #print "Checking changes"

    if not schedmd5:
        print " > Initialization.."
        for service, scheduler in recursive_glob(rootdir=wns_path,
                                                                suffix=".aps"):
            schedmd5[service] = hashlib.md5(open(scheduler).read()).hexdigest()
            execfile(scheduler)
    else:
        for service, scheduler in recursive_glob(rootdir=wns_path,
                                                                suffix=".aps"):
            md5_now = hashlib.md5(open(scheduler).read()).hexdigest()
            if not schedmd5[service] == md5_now:
                print "  > Change detectd: %s" % service
                schedmd5[service] = md5_now
                jobs = sched.get_jobs()
                for j in jobs[1:]:
                    print " job: %s" % j.name
                    if j.name.startswith(service):
                        sched.unschedule_job(j)
                execfile(scheduler)
