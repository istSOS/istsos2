# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2014 Milan Antonovic, Massimiliano Cannata
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
"""
description:
    
    Generate a text/csv;subtype=istSOS2 file merging two or more procedures
    
    Example:
    
    python scripts/istsos2istsos.py -v 
        -b 2014-01-10T00:00:00+01:00 -e 2014-01-11T00:00:00+01:00 \
        -procedures T_TRE H_TRE P_TRE \
        -src http://localhost/istsos/sos
    
"""

import sys
from os import path
from datetime import timedelta
import pprint
import json

sys.path.insert(0, path.abspath("."))

try:
    import lib.argparse as argparse
    import lib.requests as req
    import lib.isodate as iso
    import istsosutils
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e
    
    
def execute (args, logger=None):
    
    # SCRIPT CONFIGURATION
    # =========================================================================
    
    # Activate and print verbose information
    debug = args['v'] if args.has_key('v') else False
        
    # Procedure name
    procedures = args['procedures']
    # Begin date
    begin = args['begin'] if args.has_key('begin') else "*"
    # End date
    end = args['end'] if args.has_key('end') else "*"   
    
    # Aggregating function configuration
    resolution = args['resolution'] if 'resolution' in args else None
    function = args['function'] if 'function' in args else None
    nodataValue = args['nodataValue'] if 'nodataValue' in args else None
    nodataQI = args['nodataQI'] if 'nodataQI' in args else None
    
    src = args['src']
    service = args['service']
    
    def log(message):
        if debug:
            if logger:
                logger.log(message)
            else:
                print message
    
    
    log("\nProcedure aggregation stared")
    log("============================\n")
    
    
    for procedure in procedures:
        print procedure
        
        res = req.get(
            "%s/wa/istsos/services/%s/procedures/%s" % (
                src,service,procedure
            ), prefetch=True, verify=False
        )
        
        
        
        print res.json['success']
    
    
    
    
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Copy data from an istSOS service to another one, also re-aggregation function are permitted during the data transmission.')
    
    # SCRIPT CONFIGURATION
    # =========================================================================
    
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
    
    parser.add_argument('-procedures',
        action = 'store',
        dest   = 'procedures',
        nargs  = '+',
        help   = 'Procedures name (two or more)')
    
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
        
    # SOURCE istSOS CONFIG ==================================
        
    parser.add_argument('-src',
        action = 'store',
        dest   = 'src',
        metavar= 'https://example.com/istsos',
        help   = 'Base url with path of the source istSOS service')
    
    parser.add_argument('-service',
        action = 'store',
        dest   = 'service',
        metavar= 'sos',
        help   = 'Service name of the istSOS instance')
        
    args = parser.parse_args()
    
    execute(args.__dict__)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
