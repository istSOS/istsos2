# -*- coding: utf-8 -*-
#===============================================================================
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
#===============================================================================
from os import path
from walib import configManager
import os
import sys

import config

defaultCFGpath = path.join(config.services_path, "default.cfg")
serviceconf = configManager.waServiceConfig(defaultCFGpath)
services_path = path.join(config.wns_path, "notifications.aps")
wns_script_path = path.join(config.wns_path, "scripts")


def delNotification(name):
    """Delete selected notification

    remove notification from notification.aps, data-base and
    remove the function file

    Args:
        name (str): Name of the notification

    """
    aps_file = open(services_path, 'r')
    data = aps_file.readlines()
    aps_file.close()

    x = 0
    start = '### start ' + name + ' ###'
    end = '### end ' + name + ' ###'

    while not start in data[x]:
        x += 1

    while not end in data[x]:
        del data[x]
    del data[x]

    aps_file = open(services_path, 'w')
    aps_file.writelines(data)
    aps_file.close()
    delete_script_file(name)


def addNotification(name, func_path, interval, store=False):
    """

    Add new complex notification

    Args:
        name (str): Name of the function
        func_path (str): path to the function
        interval (int): number of minutes how ofter the function is executed
        store (bool): flag, if true the system store the notification result
                        default False

    Raises:
        Exception: raise exception if python function is wrong

    """

    print func_path
    f = open(func_path, 'r')
    code = f.read()
    f.close()

    # check code vaidity
    __check_valid_python(code, func_path)
    #if flag:
    #    return flag

    # check correct name
    __check_valid_name(name, func_path)
    #if flag:
    #    return flag

    if not "notify(" in code:
        msg = "The function MUST contain a notificationScheduler.notify() call"
        raise Exception(msg)

    # write code to file
    write_script_file(code, name)

    write_to_aps(name, interval, store)


def __check_valid_python(code, func_path):
    """

    Check if a script is syntaxly correct

    Args:
        code (str): name of the function
        func_path (str): path to the function file

    Raises:
        Exception: Exception if syntax not valid
    """
    try:
        # check only the syntax
        compile(code, func_path, 'exec')
    except Exception as e:
        print "Exception in validate python"
        raise e


def __check_valid_name(name, func_path):
    """

    Check valid function name

    Args:
        name (str): name of the function
        func_path (str): path to the function file

    Raises:
        Exception: raise exception if name not valid

    """
    flag_name = False
    flag_not = False
    for line in open(func_path, 'r'):
        if 'def' in line:
            if name in line:
                flag_name = True
        elif 'notify' in line:
            if name in line:
                flag_not = True

    if not flag_name and not flag_not:
        msg = "The function name must be equal to notification name!!!"
        raise Exception(msg)
        #return '\nThe function name must be equal to notification name!!!'


def createSimpleNotification(name, service, params, cql, interval,
                                                period=None, store=False):
    """ Create simple notifcation

    Create new python script for simplenotification and add to
    notification.aps file

    Args:
        name (str): Name of the function
        service (str): service
        params (dict): params to compose getObservation request
        cql (str): condition to reach to send notification
        interval (int): interval
        period (str): isodate period over witch the getObservation is executed
        store (bool): flag, if true the system store the notification result

    Raises:
        Exception: exception if something goes wrong

    """

    import traceback
    try:
        import json

        rparams = {
            "request": "GetObservation",
            "service": "SOS",
            "version": "1.0.0",
            "observedProperty": params['observedProperty'],
            "responseFormat": "application/json",
            "offering": params['offering']
        }

        if "procedure" in params:
            rparams['procedure'] = params["procedure"]

        if period:
            config = """
        import datetime
        import time
        import lib.isodate as isodate
        from lib.pytz import timezone
        now = datetime.datetime.now().replace(tzinfo=timezone(time.tzname[0]))
        endDate = now.strftime('%%Y-%%m-%%dT%%H:%%M:%%S%%z')
        period = isodate.parse_duration('%s')
        eventTime = now - period #datetime.timedelta(hours=)
        startDate = eventTime.strftime('%%Y-%%m-%%dT%%H:%%M:%%S%%z')

        rparams = %s
        rparams['eventTime'] = str(startDate) + "/" +str(endDate)

    """ % (period, json.dumps(rparams))
        else:
            config = """
    rparams = %s
    """ % json.dumps(rparams)

        link = serviceconf.serviceurl["url"].replace('test', '')
        link += service

        code_string = """
def %s():
    %s
    import lib.requests as requests
    res = requests.get('%s', params=rparams)

    result = res.json()['ObservationCollection']['member'][0]['result']['DataArray']['values']

    import wnslib.notificationScheduler as nS
    notify = {
        "twitter": {
            "public": "",
            "private": ""
        },
        "mail": {
            "subject": "",
            "message": ""
        },
        "alert":{
            "message": ""
        }
    }

    if len(result) ==0:
        message = "no data found, procedure: " + rparams['procedure']
        notify['twitter']['public'] = message
        notify['twitter']['private'] = message
        notify['mail']['subject'] = "notification from %s"
        notify['mail']['message'] = message
        notify['alert']['message'] = message
        return {'message', message}
        nS.notify('%s',notify)

    for el in result:
        if float(el[1]) %s:

            message = 'Notification - Date: '
            message += str(el[0]) + ' - Condition: ' + str(el[1]) + '%s'
            notify['twitter']['public'] = message
            notify['twitter']['private'] = message
            notify['mail']['subject'] = "notification from %s"
            notify['mail']['message'] = message
            notify['alert']['message'] = message
            nS.notify('%s',notify)
            return {'message' : message}
            """ % (name, config, link, name, name,
             cql, name, name, name)

        # create script file
        write_script_file(code_string, name)

        write_to_aps(name, interval, store)

    except Exception as e:
        print >> sys.stderr, traceback.print_exc()
        raise e


def write_to_aps(name, interval, store):
    """Add function call to notification.aps

    Args:
        name (str): name of the function
        interval (int): interval, how often is performed the notification
        store (bool): True if the system must store the notification result

    """

    import datetime

    now = datetime.datetime.now()
    startDate = now.strftime('%Y-%m-%d %H:%M:%S')
    aps_file = open(services_path, 'a')

    # write to notification.aps
    aps_file.writelines(
        """
### start %s ###
@sched.interval_schedule(minutes=%s, start_date='%s')
def notifications_%s():

    import wns.scripts.%s as %s
    try:
        res = %s.%s()
    except:
        return
""" % (name, interval, startDate, name, name, name, name,
                                                name)
    )

    if store:
        aps_file.writelines(
"""
    from wnslib import response
    r = response.Response()
    r.setNotification('%s')
    r.setResponse(res)
    r.writeToDB()
""" % (name,)
        )

    aps_file.writelines(
"""### end %s ###""" % (name,)
        )
    aps_file.close()


def write_script_file(code, name):
    """Create function python file

    create a function_name.py in the wns/scripts folder

    Args:
        code (str): python code
        name (str): name of the function

    """

    function_path = path.join(wns_script_path, name + ".py")
    script = open(function_path, 'w')
    script.write(code)
    script.close()


def delete_script_file(name):
    """

    remove function_name.py and function_name.pyc files

    Args:
        name (str): function name
    """
    if os.path.exists(wns_script_path + name + '.py'):
        os.remove(wns_script_path + name + '.py')
        if os.path.exists(wns_script_path + name + '.pyc'):
            os.remove(wns_script_path + name + '.pyc')

        print "file removed"
    else:
        print "file not found"

