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

import sys
import os
from os import path
import traceback
import json
import pprint
import glob
from datetime import datetime
from datetime import timedelta
import copy

sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
    import lib.requests as requests
    from lib.requests.auth import HTTPBasicAuth
    import lib.isodate as iso
    from lib.pytz import timezone
    from scripts.raw2csv import DebugConverter
except ImportError as e:
    print """
Error loading internal libs:
 >> did you run the script from the istSOS root folder?\n\n"""
    raise e

datacache = None
isourn = 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601'


def execute(args, conf=None):

    def log(message):
        if conf is not None and 'logger' in conf:
            conf['logger'].log(message)
        else:
            print message

    def addMessage(self, message):
        if 'logger' in conf:
            conf['logger'].addMessage(message)
        else:
            print message

    def addWarning(self, message):
        if 'logger' in conf:
            conf['logger'].addWarning(message)
        else:
            print message

    def addException(self, message):
        if 'logger' in conf:
            conf['logger'].addException(message)
        else:
            print message

    pp = pprint.PrettyPrinter(indent=2)

    try:

        # Initializing URLs
        url = args['u']

        # Service instance name
        service = args['s']

        # Quality index
        quality = '100'
        if 'q' in args:
            quality = args['q']

        # Procedures
        procs = args['p']

        # Working directory, where the CSV files are located
        wd = args['wd']

        # File extension
        ext = '.dat'
        if 'e' in args:
            ext = args['e']

        debug = False
        if 'v' in args:
            debug = args['v']

        test = False
        if 't' in args:
            test = args['t']

        user = None
        if 'user' in args and args['user'] is not None:
            user = args['user']

        password = None
        if 'password' in args and args['password'] is not None:
            password = args['password']

        auth = None
        if user and password:
            auth = HTTPBasicAuth(user, password)

        noqi = False  # False meas that quality index is also migrated
        if 'noqi' in args:
            if args['noqi'] is True:
                noqi = True

        maxobs = 5000
        if 'm' in args:
            maxobs = int(args['m'])

        #req = requests.session()
        req = requests

        for proc in procs:

            log("\nProcedure: %s" % proc)

            if conf is not None and 'description' in conf:
                data = conf['description']
            else:
                # Load procedure description
                res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (
                    url,
                    service,
                    proc
                    ), auth=auth, verify=False)

                data = res.json()

                if data['success'] is False:
                    raise Exception(
                        "Description of procedure %s can not be loaded: %s" % (
                            proc, data['message']))
                else:
                    log("%s > %s" % (proc, data['message']))

                data = data['data']

            aid = data['assignedSensorId']

            # Getting observed properties from describeSensor response
            op = []
            for out in data['outputs']:
                if not noqi or not ':qualityIndex' in out['definition']:
                    op.append(out['definition'])

            # Load of a getobservation request
            res = req.get(
                "%s/wa/istsos/services/%s/operations/getobservation/"
                "offerings/%s/procedures/%s/observedproperties/%s/ev"
                "enttime/last" % (
                    url, service, 'temporary', proc, ','.join(op)),
                auth=auth,
                verify=False)

            data = res.json()

            if data['success'] is False:
                raise Exception(
                    "Last observation of procedure %s can not be "
                    "loaded: %s" % (proc, data['message']))
            else:
                log("%s > %s" % (proc, data['message']))

            data = data['data'][0]
            data['AssignedSensorId'] = aid

            # Set values array empty, can contain 1 value if
            # procedure not empty
            if len(data['result']['DataArray']['values']) == 1:
                lastMeasure = data['result']['DataArray']['values'][0]
            else:
                lastMeasure = None

            data['result']['DataArray']['values'] = []

            # discover json observed property disposition
            jsonindex = {}
            for pos in range(0, len(data['result']['DataArray']['field'])):
                field = data['result']['DataArray']['field'][pos]
                if not noqi:
                    jsonindex[field['definition']] = pos
                elif not ':qualityIndex' in field['definition']:
                    jsonindex[field['definition']] = pos
                elif ':qualityIndex' in field['definition'] and noqi:
                    data['result']['DataArray']['field'].pop(pos)

            log("Searching: %s" % os.path.join(
                wd, "%s_[0-9]*%s" % (proc, ext)))

            files = glob.glob(os.path.join(wd, "%s_*%s" % (proc, ext)))
            files.sort()

            if debug:
                log("%s > %s %s found" % (
                    proc, len(files), "Files" if len(files) > 1 else "File"))

            if len(files) > 0:
                for f in files:

                    # open file
                    file = open(f, 'rU')

                    # loop lines
                    lines = file.readlines()

                    obsindex = lines[0].strip(' \t\n\r').split(",")

                    # Check if all the observedProperties of the procedure are
                    # included in the CSV file (quality index is optional)
                    for k, v in jsonindex.iteritems():
                        if k in obsindex:
                            continue
                        elif ':qualityIndex' in k:
                            continue
                        else:
                            raise Exception(
                                "Mandatory observed property %s is not present"
                                " in the CSV." % k)

                    # loop lines (skipping header)
                    for i in range(1, len(lines)):
                        try:
                            line = lines[i]
                            lineArray = line.strip(' \t\n\r').split(",")

                            # Creating an empty array where the values will
                            # be inserted
                            observation = ['']*len(jsonindex)

                            for k, v in jsonindex.iteritems():
                                val = None
                                if k in obsindex:
                                    val = lineArray[obsindex.index(k)]
                                elif ':qualityIndex' in k:
                                    # Quality index is not present in the CSV
                                    # so the default value will be set
                                    val = quality

                                observation[v] = val

                            # attach to object
                            data['result']['DataArray']['values'].append(
                                observation)

                        except Exception as e:
                            raise Exception(
                                "Errore alla riga: %s - %s\n%s" % (
                                    i, lines[i], str(e)))

                log("Before insert ST: %s" % proc)
                if 'beginPosition' in data["samplingTime"]:
                    log(" > Begin: %s" % data["samplingTime"]["beginPosition"])
                if 'endPosition' in data["samplingTime"]:
                    log("   + End: %s" % data["samplingTime"]["endPosition"])

                dtstr = os.path.split(f)[1].replace(
                    "%s_" % proc, "").replace(ext, "")

                offset = False

                if '+' in dtstr:
                    offset = dtstr[dtstr.index('+'):]
                    offset = [offset[0:3], offset[3:5]]
                    dtstr = dtstr[:dtstr.index('+')]

                elif '-' in dtstr:
                    offset = dtstr[dtstr.index('-'):]
                    offset = [offset[0:3], offset[3:5]]
                    dtstr = dtstr[:dtstr.index('-')]

                ep = datetime.strptime(
                    dtstr, "%Y%m%d%H%M%S%f"
                ).replace(tzinfo=timezone('UTC'))

                if offset:
                    ep = ep - timedelta(
                        hours=int(offset[0]), minutes=int(offset[1]))

                # A kick in the brain code snippet
                # If there is at least one measure:
                if len(data['result']['DataArray']['values']) > 0:
                    # taking first observation as begin position
                    bp = iso.parse_datetime(
                        data['result']['DataArray']['values'][0][
                            jsonindex[isourn]]
                    )

                else:
                    # otherwise this can be an irrebular procedure where just
                    # the end position is moved forward
                    if ep > iso.parse_datetime(
                            data["samplingTime"]["endPosition"]):
                        bp = ep
                    else:
                        raise Exception(
                            "Something is wrong with begin position..")

                data["samplingTime"] = {
                    "beginPosition": bp.isoformat(),
                    "endPosition":  ep.isoformat()
                }

                log("Insert ST: %s" % proc)
                log(" > Begin: %s" % bp.isoformat())
                log("   + End: %s" % ep.isoformat())
                log(" > Values: %s" % len(
                    data['result']['DataArray']['values']))

                if not test and len(files) > 0:  # send to wa

                    if len(data['result']['DataArray']['values']) > maxobs:

                        total = len(data['result']['DataArray']['values'])
                        inserted = last = maxobs

                        while len(data['result']['DataArray']['values']) > 0:

                            tmpData = copy.deepcopy(data)
                            tmpData['result']['DataArray']['values'] = (
                                data['result']['DataArray']['values'][:last]
                            )
                            data['result']['DataArray']['values'] = (
                                data['result']['DataArray']['values'][last:]
                            )

                            if len(data['result']['DataArray']['values']) > 0:
                                tmpData["samplingTime"] = {
                                    "beginPosition": tmpData[
                                        'result'][
                                        'DataArray'][
                                        'values'][0][jsonindex[isourn]],
                                    "endPosition": data[
                                        'result'][
                                        'DataArray'][
                                        'values'][0][jsonindex[isourn]]
                                }
                            else:
                                tmpData["samplingTime"] = {
                                    "beginPosition": tmpData[
                                        'result'][
                                        'DataArray'][
                                        'values'][0][jsonindex[isourn]],
                                    "endPosition":   ep.isoformat()
                                }

                            res = req.post(
                                "%s/wa/istsos/services/%s/"
                                "operations/insertobservation" % (
                                    url,
                                    service),
                                auth=auth,
                                verify=False,
                                data=json.dumps({
                                    "ForceInsert": "true",
                                    "AssignedSensorId": aid,
                                    "Observation": tmpData
                                })
                            )

                            # read response
                            res.raise_for_status()
                            log(" > Insert observation success of %s/%s (%s / "
                                "%s) observations: %s" % (
                                    inserted, total,
                                    tmpData["samplingTime"]["beginPosition"],
                                    tmpData["samplingTime"]["endPosition"],
                                    res.json()['success']))

                            if not res.json()['success']:
                                log(res.json()['message'])

                            if len(
                                    data['result']['DataArray']['values']
                                    ) < maxobs:
                                last = len(
                                    data['result']['DataArray']['values'])
                            inserted += last

                    else:

                        res = req.post(
                            "%s/wa/istsos/services/%s/operations/"
                            "insertobservation" % (
                                url,
                                service),
                            auth=auth,
                            verify=False,
                            data=json.dumps({
                                "ForceInsert": "true",
                                "AssignedSensorId": aid,
                                "Observation": data
                            })
                        )

                        # read response
                        res.raise_for_status()
                        log(" > Insert observation success: %s" % (
                            res.json()['success']))

                        if not res.json()['success']:
                            log(res.json()['message'])

        pass

    except requests.exceptions.HTTPError as eh:
        #addException(str(eh))
        traceback.print_exc()

    except Exception as e:
        #addException(str(e))
        traceback.print_exc()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Import data from a csv file.')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='v',
        help='Activate verbose debug')

    parser.add_argument(
        '-t', '--test',
        action='store_true',
        dest='t',
        help='Test the script, deactivating the insert observation operations.'
    )

    parser.add_argument(
        '-p',
        action='store',
        required=True,
        nargs='+',
        dest='p',
        metavar='procedures',
        help='List of procedures to be aggregated.')

    parser.add_argument(
        '-m',
        action='store',
        dest='m',
        metavar='max observations',
        default='5000',
        help=('Maximum number of observations inserted per InsertObservation '
              'request (default: %(default)s).')
    )

    parser.add_argument(
        '-q',
        action='store',
        dest='q',
        metavar='quality index',
        default='100',
        help=('The quality index to set for all the measures of the CSV file, '
              'if not set into the CSV. (default: %(default)s).')
    )

    parser.add_argument(
        '-noqi',
        action='store_true',
        dest='noqi',
        help='Do not export quality index')

    parser.add_argument(
        '-u',
        action='store',
        dest='u',
        metavar='url',
        default='http://localhost:80/istsos',
        help=('IstSOS Server address IP (or domain name) used for all '
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
        '-w',
        action='store',
        required=True,
        dest='wd',
        metavar='working directory',
        help='Working directory where the csv files are located.')

    parser.add_argument(
        '-e',
        action='store',
        dest='e',
        metavar='file extension',
        default='.dat',
        help='Extension of the CSV file. (default: %(default)s)')

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
