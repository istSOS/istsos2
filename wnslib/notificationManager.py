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

defaultCFGpath = path.join(path.dirname(path.split(path.abspath(__file__))[0]),
                                         "services/default.cfg")
serviceconf = configManager.waServiceConfig(defaultCFGpath)
services_path = path.join(path.dirname(path.split(path.abspath(__file__))[0]),
                                             "services/notifications.aps")
wns_script_path = path.join(path.dirname(path.split(path.abspath(__file__))[0]),
                                             "scripts/wns/")


def delNotification(name):
    """Delete selected notification

    remove notification from notification.aps, data-base and
    remove the function file

    Args:
        name (string): Name of the notification

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
    """Add new function to notification.asp file.

    The function should terminate with a call
    to notify() in case the condition is met

    Args:
        name (string): Name of the function
        func_path (string): path to the function
        interval (integer): number of minutes how ofter the function is executed
        store (boolean): flag, if true the system store the notification result

    Returns:
        return message error if problem with file
    """

    print func_path
    f = open(func_path, 'r')
    code = f.read()
    f.close()

    # check code vaidity
    flag = __check_valid_python(code, func_path)
    if flag:
        return flag

    # check correct name
    flag = __check_valid_name(name, func_path)
    if flag:
        return flag

    if not "notify(" in code:
        return "The function MUST contain a notificationScheduler.notify() call"

    # write code to file
    write_script_file(code, name)

    write_to_aps(name, interval, store)


def __check_valid_python(code, func_path):
    """Check if a script is correct

    Args:
        code: name of the function
        func_path: path to the function file

    Returns:
        a string error if code not valid
    """
    try:
        # check only the syntax
        compile(code, func_path, 'exec')
    except Exception, e:
        return "Error on function: " + str(e)


def __check_valid_name(name, func_path):
    """Check valid function name

    Args:
        name: name of the function
        func_path: path to the function file

    Returns:
        a string error if name not valid

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
        return '\nThe function name must be equal to notification name!!!'


def createSimpleNotification(name, service, params, cql, interval,
                                                period=None, store=False):
    """ Create simple notifcation

    Create new python script for simplenotification and add to
    notification.aps file

    Args:
        name: Name of the function
        service: service
        params: params to compose getObservation request
        cql: condition to reach to send notification
        interval: interval
        period: isodate period over witch the getObservation is executed
        store: flag, if true the system store the notification result

    Returns:

    """
    """
    Inputs:
        params = dict of {key:val1, key:val1, ...} to compose
                the GetObservation request returning 1
                value (latest, max of aggregation, etc..)
        cql = cql condition to be verified (e.g.: >40)
"""
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
        }
    }

    if len(result) ==0:
        message = "no data found, procedure: " + rparams['procedure']
        notify['twitter']['public'] = message
        notify['twitter']['private'] = message
        notify['mail']['subject'] = "notification from %s"
        notify['mail']['message'] = message
        nS.notify('%s',notify)

    for el in result:
        if float(el[1]) %s:

            message = 'Condition met on the requested notification\\nDate: '
            message += str(el[0]) + '\\nCondition: ' + str(el[1]) + '%s'
            notify['twitter']['public'] = message
            notify['twitter']['private'] = message
            notify['mail']['subject'] = "notification from %s"
            notify['mail']['message'] = message
            nS.notify('%s',notify)
            return {'message' : message}
            """ % (name, config, link, name, name,
         cql, name, name, name)

    # create script file
    write_script_file(code_string, name)

    write_to_aps(name, interval, store)


def write_to_aps(name, interval, store):
    """Add function call to notification.aps

    Args:
        name (String): name of the function
        interval (Integer): interval, how often is performed the notification
        store (boolean): True if the system must store the notification result

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

    from wnslib import wnslogger
    logger = wnslogger.wnsLogger()
    import scripts.wns.%s as %s
    try:
        logger.logInfo("execute %s")
        res = %s.%s()
    except:
        import sys
        import traceback
        logger.logError(sys.exc_info()[1])
        logger.logError(''.join(traceback.format_tb(sys.exc_info()[2])))
        return

""" % (name, interval, startDate, name, name, name, name,
                                                name, name)
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

    create a function_name.py in the scripts/wns folder

    Args:
        code (String): python code
        name (String): name of the function

    """
    script = open(wns_script_path + name + ".py", 'w')
    script.write(code)
    script.close()


def delete_script_file(name):
    """remove function python file
    remove function_name.py and function_name.pyc files

    Args:
        name (String): function name
    """
    if os.path.exists(wns_script_path + name + '.py'):
        os.remove(wns_script_path + name + '.py')
        print "file removed"
        if os.path.exists(wns_script_path + name + '.pyc'):
            os.remove(wns_script_path + name + '.pyc')
    else:
        print "file not found"

