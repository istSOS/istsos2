# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2014 Massimiliano Cannata, Milan Antonovic
#
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
from os import path
from walib import configManager


defaultCFGpath = path.join(path.dirname(path.split(path.abspath(__file__))[0]),
                                         "services/default.cfg")
serviceconf = configManager.waServiceConfig(defaultCFGpath)
services_path = path.join(path.dirname(path.split(path.abspath(__file__))[0]),
                                             "services/notifications.aps")


def delNotification(name):

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


def addNotification(name, func_name, interval):
    """
    add the funtion to .aps
    1) append on .aps the function "name"

    !!! The function should terminate with a call
    to notify() in case the condition is met
    """
    import datetime
    now = datetime.datetime.now()
    startDate = now.strftime('%Y-%m-%d %H:%M:%S')

    f = open(func_name, 'r')
    code = f.read()
    f.close()

    flag = __check_valid_python(code, func_name)
    if flag:
        return flag

    flag = __check_valid_name(name, func_name)
    if flag:
        return flag

    if not "notify(" in code:
        return "The function MUST contain a notificationScheduler.notify() call"

    aps_file = open(services_path, 'a')
    aps_file.writelines(
        """
### start %s ###
@sched.interval_schedule(minutes=%s, start_date='%s')
%s
### end %s ###""" % (name, interval, startDate, code, name)
    )
    aps_file.close()


def __check_valid_python(code, func_name):
    try:
        # check only the syntax
        compile(code, func_name, 'exec')
    except Exception, e:
        return "Error on function: " + str(e)


def __check_valid_name(name, func_name):

    flag_name = False
    flag_not = False
    for line in open(func_name, 'r'):
        if 'def' in line:
            if name in line:
                flag_name = True
        elif 'notify' in line:
            if name in line:
                flag_not = True

    if not flag_name and not flag_not:
        return '\nThe function name nust be equal to notification name!!!'


def createSimpleNotification(name, service, params, cql, interval, period=None):
    """
    Inputs:
        params = dict of {key:val1, key:val1, ...} to compose
                the GetObservation request returning 1
                value (latest, max of aggregation, etc..)
        cql = cql condition to be verified (e.g.: >40)
"""

    import datetime
    import json
    now = datetime.datetime.now()
    startDate = now.strftime('%Y-%m-%d %H:%M:%S')

    aps_file = open(services_path, 'a')

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
    from pytz import timezone
    now = datetime.datetime.now().replace(tzinfo=timezone(time.tzname[0]))
    endDate = now.strftime('%%Y-%%m-%%dT%%H:%%M:%%S%%z')
    eventTime = now - datetime.timedelta(hours=%s)
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

    # write to notification.aps
    aps_file.writelines(
"""### start %s ###
@sched.interval_schedule(minutes=%s, start_date='%s')
def %s():
    %s
    import lib.requests as requests
    res = requests.get('%s', params=rparams)

    result = res.json['ObservationCollection']['member'][0]['result']['DataArray']['values']

    import wnslib.notificationScheduler as nS

    if len(result) ==0:
        message = "no data found, procedure: " + rparams['procedures']
        nS.notify('%s',message)

    for el in result:
        if float(el[1]) %s:

            message = 'Condition met on the requested notification\\nDate: '
            message += str(el[0]) + '\\nCondition: ' + str(el[1]) + '%s'
            nS.notify('%s',message)
            break;
### end %s ### """ % (name, interval, startDate, name, config, link, name,
         cql, name, name, name)
    )
    aps_file.close()
