# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
#---------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#---------------------------------------------------------------------------
# Created on Tue Nov 12 17:15:04 2013
#---------------------------------------------------------------------------
"""
description:
    
"""

#---------------------------------
import os
def recursive_glob(rootdir='.', suffix=''):
    return [( os.path.splitext(filename)[0] ,os.path.join(rootdir, filename) )
            for rootdir, dirnames, filenames in os.walk(rootdir)
            for filename in filenames if filename.endswith(suffix)]
#---------------------------------
import logging
#logging.basicConfig()
errorlog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs","scheduler.log")
logging.basicConfig(filename=errorlog_path,level=logging.INFO)            
#---------------------------------
import hashlib
schedmd5 = {}
services_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "services")
#schedfile = '/home/maxi/virtualenvDIR/scheduler/mytest.py'
#---------------------------------
from apscheduler.scheduler import Scheduler
sched = Scheduler(daemonic=False)
#sched = Scheduler()
sched.start()

sched.add_cron_job()
#===========================
#START THE ISTSOS SCHEDULER 
#===========================
@sched.interval_schedule(seconds=1)
def istsos_job():
    global schedmd5
#    print schedmd5
    if not schedmd5:
        for service,scheduler in recursive_glob(rootdir=services_path ,suffix=".aps"):
            schedmd5[service]=hashlib.md5(open(scheduler).read()).hexdigest()
            execfile(scheduler)
    else:
        for service,scheduler in recursive_glob(rootdir=services_path ,suffix=".aps"):
            md5_now = hashlib.md5(open(scheduler).read()).hexdigest()
            if not schedmd5[service] == md5_now:
                schedmd5[service] = md5_now
                jobs = sched.get_jobs()
                for j in jobs[1:]:
                    if j.name.startswith(service):
                        sched.unschedule_job(j)
                execfile(scheduler)
            
#while True:
#    pass



#=============================================
# THE FILE TO BE RED AND EXECUTED
#=============================================
#@sched.interval_schedule(seconds=3)
#def timed_job():
#    print 'This job is run every three minutes.'
#
#@sched.interval_schedule(seconds=3)
#def timed_job2():
#    print 'This job2.'
#
#@sched.cron_schedule(day_of_week='mon-fri', hour=17)
#def scheduled_job():
#    print 'This job is run every weekday at 5pm.'
#
#
#=============================================