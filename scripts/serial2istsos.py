# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# =============================================================================

__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__license__ = 'GPL2'
__version__ = '1.0'

import serial
from datetime import datetime
from datetime import timedelta
from dateutil.tz import tzlocal
import json
import argparse
import time
import sys
from os import path

#import requests
#from pytz import timezone
#import isodate as iso

try:
    sys.path.insert(0, path.abspath("."))
    from lib.pytz import timezone
    import lib.requests as requests
    from lib.requests.auth import HTTPBasicAuth
    import lib.isodate as iso
except ImportError as e:
    print """Error loading internal libs:
 >> please run the script from the istSOS root folder.\n\n"""
    print str(e)
    raise e

"""
    This script is an example build using an Arduino Board with DHT11 sensor,
    an ultra low-cost digital temperature and humidity sensor.
    See the istSOS tutorial for more info:
        > https://sourceforge.net/projects/istsos/files/Tutorials/

    Usage with inline params:

        python scripts/serial2istsos.py -v \
            -x /dev/ttyACM0 \
            -p arduino \
            -u http://istsos.org/istsos \
            -s demo

    Usage with config file:

        python scripts/serial2istsos.py -v \
            -c /home/istsos/config/arduino.json

    The config format:
    {
        "url": "http://istsos.org/istsos",
        "service": "demo",
        "port": "/dev/ttyACM0",
        "baud": "9600",
        "procedure": "arduino",
        "datetime": {
            "date": {
                "column": 4,
                "format": "%m/%d/%Y"
            },
            "time": {
                "column": 5,
                "format": "%H:%M:%S"
            },
            "tz": "+01:00"
        },
        "observations": [{
            "name": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity:relative",
            "column": 13,
            "nodata": -1
        },{
            "name": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
            "column": 14
        },{
            "name": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:heatindex",
            "column": 2
        }]
    }

    Date time configuration variations are optional, if not given, current
    timestamp will be used:

    - Single column date and time:

        "datetime": {
            "column": 0,
            "format": "%Y-%m-%d %H:%M:%S",
            "tz": "+01:00"
        }

    - Time and date in two separate columns

        "datetime": {
            "date": {
                "column": 0,
                "format": "%Y-%m-%d"
            },
            "time": {
                "column": 1,
                "format": "%H:%M:%S"
            },
            "tz": "+01:00"
        }
"""


def getDateTimeWithTimeZone(dt, tz):
    dt = dt.replace(tzinfo=timezone('UTC'))
    offset = tz.split(":")
    return dt - timedelta(hours=int(offset[0]), minutes=int(offset[1]))


def execute(args):

    dtconfig = False
    debug = False
    config = False
    header = 0

    user = None
    if 'user' in args and args['user'] is not None:
        user = args['user']
    password = None
    if 'password' in args and args['password'] is not None:
        password = args['password']

    auth = None
    if user and password:
        auth = HTTPBasicAuth(user, password)

    if 'c' in args and args['c'] is not None:
        with open(args['c'], 'r') as f:
            config = json.loads(f.read())

        url = config['url']
        service = config['service']
        procedure = config['procedure']

        if "datetime" in config:
            dtconfig = config["datetime"]

        if "header" in config:
            header = config["header"]

        s = serial.Serial(config['port'], config['baud'])

    else:
        url = args['u']
        service = args['s']
        procedure = args['p']

        s = serial.Serial(args['x'], args['b'])

    s.timeout = 5

    if 'v' in args:
        debug = args['v']

    # Requesting service configuration info
    res = requests.get('%s/wa/istsos/services/%s/configsections' % (
        url, service), auth=auth)
    istConfig = res.json()['data']
    defaultNaN = istConfig["getobservation"]["aggregatenodata"]

    # Requesting a describe sensor mainly to store the assignedSensorId
    res = requests.get(
        '%s/wa/istsos/services/%s/procedures/%s' % (
            url, service, procedure), auth=auth)

    ds = res.json()['data']
    if debug:
        print "Loading info: %s" % procedure

    # Preparing "io" object to send
    res = requests.get(
        '%s/wa/istsos/services/%s/operations/getobservation/offerings/'
        'temporary/procedures/%s/observedproperties/:/eventtime/last' % (
            url, service, procedure),
        params={
            "qualityIndex": "False"
        }, auth=auth)

    io = {
        "AssignedSensorId": ds['assignedSensorId'],
        "ForceInsert": "true",
        "Observation": res.json()['data'][0]
    }
    ec = int(io['Observation']['result']['DataArray']['elementCount']) - 1

    # If config file given, check observedproperties exactness
    observations = []
    columns = []
    nodata = []
    for idx in range(
            1, len(io["Observation"]['result']['DataArray']['field'])):
        observation = io["Observation"]['result']['DataArray']['field'][idx]
        observations.append(observation['definition'])
        columns.append((idx-1))
        nodata.append(defaultNaN)

    if config:
        for observation in config["observations"]:
            if observation['name'] not in observations:
                print "Warning: procedure \"%s\" does not observe %s" % (
                    procedure, observation['name']
                )
                s.close()
                exit()
            else:
                idx = observations.index(observation['name'])
                columns[idx] = int(observation['column'])
                if "nodata" in observation:
                    nodata[idx] = str(observation['nodata'])

    skip = True
    sample = True
    line = 0

    while True:
        if skip:
            # clear buffer (avoid bad read)
            print "Wait for serial"
            s.flushInput()
            s.readline()
            time.sleep(1)
            skip = False
            continue

        elif line < header:
            print "Skipping line: %s " % line
            s.flushInput()
            time.sleep(1)
            line = line + 1
            continue

        try:
            message = s.readline().strip()
            data = message.split(',')

            print data

            if dtconfig:
                if 'column' in dtconfig:
                    eventtime = datetime.strptime(
                        data[int(dtconfig['column'])],
                        dtconfig['format']
                    )

                elif 'date' in dtconfig and 'time' in dtconfig:
                    d = datetime.strptime(
                        data[int(dtconfig['date']['column'])],
                        dtconfig['date']['format']
                    )
                    t = datetime.strptime(
                        data[int(dtconfig['time']['column'])],
                        dtconfig['time']['format']
                    )
                    eventtime = datetime.combine(d, t.time())

                else:
                    print "Warning: date time configuration wrong"
                    s.close()
                    exit()

                if "tz" in dtconfig:
                    eventtime = getDateTimeWithTimeZone(eventtime, dtconfig["tz"])

            else:
                eventtime = datetime.now(tzlocal())

            io["Observation"]['samplingTime'] = {
                "beginPosition": eventtime.isoformat(),
                "endPosition": eventtime.isoformat()
            }
            ob = [eventtime.isoformat()]
            for idx in range(len(columns)):
                column = columns[idx]
                if nodata[idx] == data[column]:
                    ob.append(defaultNaN)
                else:
                    ob.append(data[column])

            io["Observation"]['result']['DataArray']['values'] = [ob]

            if sample:
                sample = False
                print "\nData sample:"
                for idx in range(len(observations)):
                    print "%s = %s" % (
                        observations[idx], data[columns[idx]]
                    )
                print "\n"

            if debug:
                print "Sending data: %s" % (", ".join(ob))

            res = requests.post(
                '%s/wa/istsos/services/%s/operations/insertobservation' % (
                    url, service
                ),
                data=json.dumps(io), auth=auth)

            line = line + 1

            try:
                res.raise_for_status()
                if debug:
                    print "  > Insert Ok!"
            except requests.exceptions.HTTPError as ex:
                print "Error: inserting data.."
                s.close()
                exit()

        except Exception as rex:
            print "Error: inserting data:\n%s" % rex

    s.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=("Load data read from a serial port "
                     "and execute insert data to istSOS")
    )

    parser.add_argument(
        '-v',
        action='store_true',
        dest='v',
        help='Activate verbose debug')

    parser.add_argument(
        '-c',
        action='store',
        dest='c',
        help='Config file instead of inline params')

    parser.add_argument(
        '-x',
        action='store',
        dest='x',
        help='Serial port to listen')

    parser.add_argument(
        '-b',
        action='store',
        dest='b',
        default=9600,
        help='serial port baudrate')

    parser.add_argument(
        '-p',
        action='store',
        dest='p',
        help='Procedure name')

    parser.add_argument(
        '-u',
        action='store',
        dest='u',
        metavar='url',
        default='http://localhost:80/istsos',
        help=('istSOS Server address IP (or domain name) used '
              'for all request. (default: %(default)s).'))

    parser.add_argument(
        '-s',
        action='store',
        dest='s',
        metavar='service',
        help='The name of the service instance.')

    parser.add_argument(
        '-user',
        action='store',
        dest='user',
        metavar='user name')

    parser.add_argument(
        '-password',
        action='store',
        dest='password',
        metavar='password')

    args = parser.parse_args()
    execute(args.__dict__)
