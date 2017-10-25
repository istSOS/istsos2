# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2010-2017 IST-SUPSI (www.supsi.ch/ist)
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

'''
This script register new procedures importing data from a csv file
containing the followings columns:

1.  name
2.  description
3.  keyword
4.  long name
5.  modelNumber
6.  manufacturer
7.  sensorType
8.  foi-epsg
9.  foi-coordinates
10. foi-name
11. observed property
12. uom
13. begin position
14. end position
15. resolution
16. acquisition interval
17. quality index - lower bound
18. quality index - upper bound


separated with a semicolumn symbol ";"

'''

import sys
import os
from os import path
import traceback
import json
import pprint
import glob
from datetime import datetime

#print path.abspath(".")
#print path.normpath("%s/../" % path.abspath("."))

sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
    from scripts import istsosutils as iu
    import lib.requests as requests
    from lib.requests.auth import HTTPBasicAuth

except ImportError as e:
    print """
Error loading internal libs:
>> did you run the script from the istSOS root folder?"""
    raise e


def execute(args, logger=None):

    try:
        # Service instance name
        csv = args['csv']

        user = None
        if 'user' in args and args['user'] is not None:
            user = args['user']

        password = None
        if 'password' in args and args['password'] is not None:
            password = args['password']

        auth = None
        bauth = None
        if user and password:
            auth = [user, password]
            bauth = HTTPBasicAuth(user, password)

        # Initializing URLs
        service = iu.Service(args['u'], args['s'], auth)

        file = open(csv, 'rU')

        # loop lines
        lines = file.readlines()

        # loop lines (skipping header)
        for i in range(0, len(lines)):
            line = lines[i].strip(' \t\n\r').split(";")

            proc = iu.Procedure(line[0])
            proc.setSystemType('insitu-fixed-point')
            proc.setDescription(line[1])
            proc.setKeywords(line[2])
            proc.setLongName(line[3])
            proc.setModelNumber(line[4])
            proc.setManufacturer(line[5])
            proc.setSensorType(line[6])
            coords = line[8].split(',')
            proc.setFoi(line[9], line[7], coords[0], coords[1], coords[2])
            if line[16] != '':
                proc.setResolution(line[16])
            if line[17] != '':
                proc.setAcquisitionInterval(line[17])

            o1 = line[10].split(',')
            o2 = line[11].split(',')
            o3 = line[12].split(',')
            uom = line[13].split(',')
            cLower = []
            if line[18] != '-':
                cLower = line[18].split(',')
            cUpper = []
            if line[19] != '-':
                cUpper = line[19].split(',')

            if len(cLower) + len(cUpper) > 0:

                if (len(o1) + len(o2) +
                        len(o3) + len(cLower) + len(cUpper)) != (len(o1)*5):
                    raise Exception("observed property lenght missmatch")

                for idx in range(0, len(o1)):
                    proc.addObservedProperty(
                        o3[idx],
                        'urn:ogc:def:parameter:x-istsos:1.0:%s:%s%s' % (
                            o1[idx],
                            o2[idx],
                            ":%s" % o3[idx] if  o3[idx] != '' else ''
                        ),
                        uom[idx],
                        upper=cUpper[idx],
                        lower=cLower[idx]
                    )
            else:
                if (len(o1) + len(o2) + len(o3)) != (len(o1)*3):
                    raise Exception("observed property lenght missmatch")

                for idx in range(0, len(o1)):
                    proc.addObservedProperty(
                        o3[idx],
                        'urn:ogc:def:parameter:x-istsos:1.0:%s:%s%s' % (
                            o1[idx],
                            o2[idx],
                            ":%s" % o3[idx] if  o3[idx] != '' else ''
                        ),
                        uom[idx]
                    )

            # print proc.toJson()
            service.registerProcedure(proc)

            # Setting the begin position
            if line[14]:
                # Getting the Sensor id
                aid = service.getProcedure(
                    proc.name).description['assignedSensorId']

                # Getting observation template
                tmpl = service.getSOSProcedure(proc.name)
                tmpl['AssignedSensorId'] = aid
                tmpl["samplingTime"] = {
                    "beginPosition": line[14],
                    "endPosition":  line[14]
                }
                res = requests.post(
                    "%s/wa/istsos/services/%s/"
                    "operations/insertobservation" % (
                        args['u'], args['s']),
                    auth=bauth,
                    verify=False,
                    data=json.dumps({
                        "ForceInsert": "true",
                        "AssignedSensorId": aid,
                        "Observation": tmpl
                    })
                )
                res.raise_for_status()
                print " > Sampling time configured: %s" % line[14]

    except Exception as e:
        print "ERROR: %s\n\n" % e
        traceback.print_exc()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Registers new sensor from a csv file.')

    parser.add_argument(
        '-csv',
        action='store',
        required=True,
        dest='csv',
        metavar='csv file',
        help='The csv file containing the procedures metadata')

    parser.add_argument(
        '-u',
        action='store',
        dest='u',
        metavar='url',
        default='http://localhost:80/istsos',
        help=(
            'IstSOS Server address IP (or domain name) used for all '
            'request. (default: %(default)s).')
        )

    parser.add_argument(
        '-s',
        action='store',
        required=True,
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
