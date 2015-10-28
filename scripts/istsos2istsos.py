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
    
    
"""

'''
Examples:
    
1. Simple copy 1 to 1

python scripts/istsos2istsos.py -v -procedure P_BED \
    -b 2014-01-10T00:00:00+01:00 -e 2014-01-11T00:00:00+01:00 \
    --surl http://localhost/istsos --ssrv sosraw \
    --dsrv sos
    

2. Copy applying an aggregate function SUM of 10 minutes

python scripts/istsos2istsos.py -v -procedure P_BED \
    -f SUM -r PT10M -val 0 -qi 100 \
    -b 2014-01-10T00:00:00+01:00 -e 2014-01-11T00:00:00+01:00 \
    --surl http://localhost/istsos --ssrv sosraw \
    --dsrv sos

    
'''
import sys
from os import path
from datetime import timedelta
import pprint
import json

sys.path.insert(0, path.abspath("."))

try:
    import lib.argparse as argparse
    import lib.requests as requests
    import lib.isodate as iso
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e
    
fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
pp = pprint.PrettyPrinter(indent=4)

def execute (args, logger=None):
    
    def log(message):
        if debug:
            if logger:
                logger.log(message)
            else:
                print message
                
                
    # SCRIPT CONFIGURATION
    # =========================================================================
    
    # Activate and print verbose information
    debug = args['v'] if args.has_key('v') else False
        
    # Procedure name
    procedure = args['procedure']
    # Begin date
    begin = args['begin'] if args.has_key('begin') else "*"
    # End date
    end = args['end'] if args.has_key('end') else "*"    
    # Global User and password valid for all connections
    suser = duser = auser = args['user'] if args.has_key('user') else None
    spwd = dpwd = apwd = args['pwd'] if args.has_key('pwd') else None
    
    # Activate this will copy also the quality index from source to destination
    cpqi = args['cpqi'] if args.has_key('cpqi') else False
    
    # Aggregating function configuration
    resolution = args['resolution'] if 'resolution' in args else None
    function = args['function'] if 'function' in args else None
    nodataValue = args['nodataValue'] if 'nodataValue' in args else None
    nodataQI = args['nodataQI'] if 'nodataQI' in args else None
    
    # Retroactive aggregation
    retro = args['retro'] if 'retro' in args else 0
    
    # Force using last position as end position during insert sensor operation
    lm = args['lm'] if 'lm' in args else False
    
    # SOURCE istSOS CONFIG ==================================
    # Location
    surl = args['surl']
    # Service instance name
    ssrv = args['ssrv']
    # User and password if given this will be used for source istSOS
    if args.has_key('suser'):
        suser = args['suser']
    if args.has_key('spwd'):
        spwd = args['spwd']
    
    # DESTINATION istSOS CONFIG =============================
    # Location (if not given, same as source will be used)
    durl = args['durl'] if (args.has_key('durl') and args['durl'] is not None) else surl
    # Service instance name
    dsrv = args['dsrv']
    # User and password if given this will be used for destination istSOS
    if args.has_key('duser'):
        duser = args['duser']
    if args.has_key('dpwd'):
        dpwd = args['dpwd']
        
    # ALTERNATIVE istSOS SERVICE FOR QI EXTRAPOLATION =======
    # Location (if not given, same as source will be used)
    aurl = args['aurl'] if (args.has_key('aurl') and args['aurl'] is not None) else None
    # Service instance name
    asrv = args['asrv'] if (args.has_key('asrv') and args['asrv'] is not None) else None
    # User and password if given this will be used for extrapolation QI istSOS
    if args.has_key('auser'):
        auser = args['auser']
    if args.has_key('apwd'):
        apwd = args['apwd']
    
            
    # PROCESSING STARTS HERE ==================================================
    
    log("\nistSOS > 2 > istSOS STARTED:")
    log("==============================\n")
    
    #req = requests.session()
    req = requests
    
    # Load procedure description        
    log("1. Loading procedure description: %s" % procedure)
        
    # Loading describe sensor from source =====================================
    res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (
        surl,
        ssrv,
        procedure
        ), auth=(suser, spwd), verify=False)
    sdata = res.json()
    if sdata['success']==False:
        raise Exception ("Description of procedure %s can not be loaded from source service: %s" % (procedure, sdata['message']))
    else:
        log("   > DS Source Ok.")
            
    # Loading describe sensor from destination ================================
    res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (
            durl, dsrv, procedure
        ), auth=(duser, dpwd), verify=False)
    ddata = res.json()
    if ddata['success']==False:
        raise Exception ("Description of procedure %s can not be loaded from destination service: %s" % (procedure, ddata['message']))
    else:
        log("   > DS Destination Ok.")
        
    # Load of a getobservation template from destination =======================================
    res = req.get("%s/wa/istsos/services/%s/operations/getobservation/offerings/%s/procedures/%s/observedproperties/:/eventtime/last?qualityIndex=False" % (
            durl, dsrv, 'temporary', procedure
        ),  params={
            "qualityIndex": cpqi
        }, auth=(duser, dpwd), verify=False)
    dtemplate = res.json()
    if dtemplate['success']==False:
        raise Exception ("Observation template of procedure %s can not be loaded: %s" % (procedure, dtemplate['message']))
    else:
        dtemplate = dtemplate['data'][0]
        dtemplate['AssignedSensorId'] = ddata['data']['assignedSensorId']
        dtemplate['result']['DataArray']['values'] = []
        log("     > GO Template Ok.")

    # Loading describe sensor from QI EXTRAPOLATION service ===================
    if aurl and asrv:
        res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (
                aurl, asrv, procedure
            ), auth=(auser, apwd), verify=False)
        adata = res.json()
        if adata['success']==False:
            raise Exception ("Description of procedure %s can not be loaded from destination service: %s" % (procedure, adata['message']))
        else:
            log("   > DS QI Extrapolation Ok.")

    log("\n2. Identifying processing interval:")
    
    # Check if mesaures are present in source procedure, by identifying the sampling time constraint 
    #  located always in the first position of the outputs, if it is empty an exception is thrown
    if (not 'constraint' in sdata['data']['outputs'][0] 
            or not 'interval' in sdata['data']['outputs'][0]['constraint'] ):
        raise Exception ("There is no data in the source procedure to be copied to the destination procedure.")
    else:
        # Check if the contraint interval contains a valid ISO date begin position
        try:
            iso.parse_datetime(sdata['data']['outputs'][0]['constraint']['interval'][0])
        except Exception:
            raise Exception ("The date in the source procedure constraint interval (%s) is not valid." % 
                sdata['data']['outputs'][0]['constraint']['interval'][0])
        
        # Check if the contraint interval contains a valid ISO date end position
        try:
            iso.parse_datetime(sdata['data']['outputs'][0]['constraint']['interval'][1])
        except Exception:
            raise Exception ("The date in the source procedure constraint interval (%s) is not valid." % 
                sdata['data']['outputs'][0]['constraint']['interval'][1])
    
    log("   > Source interval is valid")
    
    # Looking for start (IO beginPOsition) instant processing 
    #   If the default value (*) is used, then the endPosition of 
    #   the "destination" service procedure will be used. But if the destination
    # procedure is empty , then the begin position of the source will be used
    start = None
    stop = None
    if begin == "*":
        if ('constraint' in ddata['data']['outputs'][0] 
            and 'interval' in ddata['data']['outputs'][0]['constraint']):
                try:
                    if function and resolution:
                        # getting last inserted observations of "destination" service
                        log("Aggregation requested: getting last inserted observations of \"destination\" service")
                        params = {
                            "request": "GetObservation",
                            "service": "SOS",
                            "version": "1.0.0",
                            "observedProperty": ':',
                            "procedure": procedure,
                            "responseFormat": "application/json",
                            "offering": 'temporary'
                        }
                        res = req.get("%s/%s" % (durl,dsrv), params=params, auth=(duser, dpwd), verify=False)
                        obs = res.json()
                        start = iso.parse_datetime(obs['ObservationCollection']['member'][0]['result']['DataArray']['values'][0][0])
                    else:
                        # The endPosition of the destination will be used as Start/IO BeginPosition
                        start = iso.parse_datetime(ddata['data']['outputs'][0]['constraint']['interval'][1])
                    if retro > 0: # Retroactive aggregation
                        log("Retroactive aggregation active.")
                        if start-timedelta(minutes=retro) > iso.parse_datetime(ddata['data']['outputs'][0]['constraint']['interval'][0]):
                            start = start-timedelta(minutes=retro)
                        else:
                            start = iso.parse_datetime(ddata['data']['outputs'][0]['constraint']['interval'][0])
                            
                    log("Start: %s" % start)
                    
                except Exception as ee:
                    print "Error setting start date for proc %s: %s" % (procedure,ee)
                    raise Exception ("The date in the destination procedure %s constraint interval (%s) is not valid." % 
                        (procedure,ddata['data']['outputs'][0]['constraint']['interval'][0]))
        else:
            # The beginPosition of the source will be used as Start/IO BeginPosition
            start = iso.parse_datetime(sdata['data']['outputs'][0]['constraint']['interval'][0])           
    else:
        start = iso.parse_datetime(begin)
    
    if end == "*":
        # The endPosition of the source will be used as Stop/IO EndPosition
        stop = iso.parse_datetime(sdata['data']['outputs'][0]['constraint']['interval'][1])   
    else:
        stop = iso.parse_datetime(end)
    
    log("   > Destination interval is valid")
    log("   > Start processing: %s" % start)
    log("   > Stop processing: %s" % stop)
    if retro > 0:
        log("   > Retro aggregation: %s minutes" % retro)
    
    # Insertion loop step timedelta
    interval = timedelta(days=15)
    if start<stop and start+interval>stop:
        interval = stop-start
    
    log("   > Insertion loop step: %s" % interval)
        
    if function and resolution:
        try:
            iso.duration_isoformat(resolution)
        except:
            raise Exception ("The resolution (%s) to apply in the aggregating function is not valid." % resolution)
        log("   > Function(Resolution) : %s(%s)" % (function,resolution))
        
    while start+interval<=stop:        
        
        nextStart = start + interval
        
        params = {
            "request": "GetObservation",
            "service": "SOS",
            "version": "1.0.0",
            "observedProperty": ':',
            "procedure": procedure,
            "qualityIndex": str(cpqi),
            "responseFormat": "application/json",
            "offering": 'temporary',
            "eventTime": "%s/%s" % (start.isoformat(), nextStart.isoformat())
        }
        
        if function and resolution:
            
            params['aggregateFunction'] = function
            params['aggregateInterval'] = resolution
            
            if nodataValue != None:
                params['aggregateNodata'] = nodataValue
            if nodataQI != None:
                params['aggregateNodataQi'] = nodataQI
        
        res = req.get("%s/%s" % (surl,ssrv),  params=params, auth=(suser, spwd), verify=False)
        
        # Check if an Exception occured
        if 'ExceptionReport' in res.content:
            raise Exception (res.content)
        
        smeasures = res.json()['ObservationCollection']['member'][0]
        #pp.pprint(smeasures)
        
        log("   > %s measures from: %s to: %s" % (len(smeasures['result']['DataArray']['values']), start.isoformat(), nextStart.isoformat()))
        
        dtemplate["samplingTime"] = {}
        if lm and len(smeasures['result']['DataArray']['values'])>0:
            dtemplate["samplingTime"]["beginPosition"] = smeasures['result']['DataArray']['values'][0][0]
            dtemplate["samplingTime"]["endPosition"] = smeasures['result']['DataArray']['values'][-1][0]
        else:
            dtemplate["samplingTime"]["beginPosition"] = start.isoformat()
            dtemplate["samplingTime"]["endPosition"] = nextStart.isoformat()
            
        dtemplate['result']['DataArray']['values'] = smeasures['result']['DataArray']['values']
        dtemplate['result']['DataArray']['field'] = smeasures['result']['DataArray']['field']
        
        # POST data to WA
        res = req.post("%s/wa/istsos/services/%s/operations/insertobservation" % (
            durl,
            dsrv), 
            auth=(duser, dpwd),
            verify=False,
            data=json.dumps({
                "ForceInsert": "true",
                "AssignedSensorId": ddata['data']['assignedSensorId'],
                "Observation": dtemplate
            })
        )
        
        # read response
        log("     > Insert observation success: %s" % res.json()['success'])
        
        #print res.json()
        
        if not res.json()['success']:
            raise Exception ('Error inserting observation: %s' % res.json()['message'])
        
        start = nextStart
        if start<stop and start+interval>stop:
            interval = stop-start
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Copy data from an istSOS service to another one, also re-aggregation function are permitted during the data transmission.')
    
    # SCRIPT CONFIGURATION
    # =========================================================================
    
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
    
    parser.add_argument('-procedure',
        action = 'store',
        dest   = 'procedure',
        help   = 'Procedure name')
    
    parser.add_argument('-b', '--begin',
        action = 'store',
        dest   = 'begin',
        default= '*',
        metavar= '1978-10-08T03:56:00+01:00',
        help   = 'Begin position date of the processing in ISO 8601. If the default value (%(default)s) is used, then the endPosition of the \"destination\" service procedure will be used.')
    
    parser.add_argument('-e', '--end',
        action = 'store',
        dest   = 'end',
        default= '*',
        metavar= '2014-01-27T11:27:00+01:00',
        help   = 'End position date of the processing in ISO 8601. If the default value (%(default)s) is used, then the endPosition of the "source" service procedure will be used.')
        
    parser.add_argument('-u', '-user',
        action = 'store',
        dest   = 'user',
        metavar= 'username',
        help   = 'Global User valid for all connections')
        
    parser.add_argument('-p', '-pwd',
        action = 'store',
        dest   = 'pwd',
        metavar= 'password',
        help   = 'Global Password valid for all connections')
    
    parser.add_argument('-cpqi','--copyqualityindex',
        action = 'store_true',
        dest   = 'cpqi',
        help   = 'Activate this will copy also the quality index from source to destination.')
        
    parser.add_argument('-f','--function',
        action = 'store',
        dest   = 'function',
        choices=('SUM', 'AVG', 'MAX', 'MIN', 'COUNT'),
        help   = 'Aggregate function to be applied (choices: %(choices)s).')
        
    parser.add_argument('-r','--resolution',
        action = 'store',
        dest   = 'resolution',
        help   = 'The duration (in ISO 8601, eg: PT10M = 10 minutes) of the interval to be used with the aggregate function (-f | --function). If not set, the procedure\'s default resolution will be used (as defined in the describeSensor response).')
        
    parser.add_argument('-nv', '--nodataValue',
        action = 'store',
        dest   = 'nodataValue',
        metavar= 'value',
        default= 0,
        help   = 'Substitute for nodata observation in aggregation functions (default: %(default)s).')
        
    parser.add_argument('-nvqi', '--nodataQI',
        action = 'store',
        dest   = 'nodataQI',
        metavar= 'qi',
        default= 110,
        help   = 'Substitute for nodata quality index in aggregation functions (default: %(default)s).')
        
    parser.add_argument('--retro',
        action = 'store',
        dest   = 'retro',
        default= 0,
        type = int,
        help   = 'Retroactively aggregate of %(default)s minutes in the past from the begin (normally used with begin = *)')
        
    parser.add_argument('-lm','--uselastmeasure',
        action = 'store_true',
        dest   = 'lm',
        help   = 'Activate this to use the last measure as end position during copy, otherwise "-e | --end" will be used')
        
    # SOURCE istSOS CONFIG ==================================
        
    parser.add_argument('--surl',
        action = 'store',
        dest   = 'surl',
        metavar= 'https://example.com/istsos',
        help   = 'Base url with path of the source istSOS service')
        
    parser.add_argument('--ssrv',
        action = 'store',
        dest   = 'ssrv',
        metavar= 'sosraw',
        help   = 'Source service instance name')
        
    parser.add_argument('--suser',
        action = 'store',
        dest   = 'suser',
        metavar= 'username',
        help   = 'Username, if given this will be used for source istSOS')
        
    parser.add_argument('--spwd',
        action = 'store',
        dest   = 'spwd',
        metavar= 'password',
        help   = 'Password, if given this will be used for source istSOS')
        
        
    # DESTINATION istSOS CONFIG =============================
        
    parser.add_argument('--durl',
        action = 'store',
        dest   = 'durl',
        metavar= 'https://example.com/istsos',
        help   = 'Base url with path of the destination istSOS service (if not given source url surl will be used)')
        
    parser.add_argument('--dsrv',
        action = 'store',
        dest   = 'dsrv',
        metavar= 'sos',
        help   = 'Destination service instance name')
        
    parser.add_argument('--duser',
        action = 'store',
        dest   = 'duser',
        metavar= 'username',
        help   = 'Username, if given this will be used for destination istSOS')
        
    parser.add_argument('--dpwd',
        action = 'store',
        dest   = 'dpwd',
        metavar= 'password',
        help   = 'Password, if given this will be used for destination istSOS')
        
       
    # ALTERNATIVE istSOS SERVICE FOR QI EXTRAPOLATION ======= 
        
    parser.add_argument('--aurl',
        action = 'store',
        dest   = 'aurl',
        metavar= 'https://example.com/istsos',
        help   = 'Base url with path of the QI EXTRAPOLATION istSOS service')
        
    parser.add_argument('--asrv',
        action = 'store',
        dest   = 'asrv',
        metavar= 'sosday',
        help   = 'QI EXTRAPOLATION service instance name')
        
    parser.add_argument('--auser',
        action = 'store',
        dest   = 'auser',
        metavar= 'username',
        help   = 'Username, if given this will be used for istSOS QI EXTRAPOLATION')
        
    parser.add_argument('--apwd',
        action = 'store',
        dest   = 'apwd',
        metavar= 'password',
        help   = 'Password, if given this will be used for istSOS QI EXTRAPOLATION')
        
    args = parser.parse_args()
    
    execute(args.__dict__)
    
