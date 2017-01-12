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
    usage example:
        python scripts/constrain2db.py 
            -f /home/maxi/Desktop/const_csv.txt 
            -s http://localhost/istsos/wa/istsos/services/demo 
            -r urn:ogc:def:parameter:x-istsos:1.0:qualityIndex:check:lev1 
            -v
"""

import sys
import os
from os import path
import traceback
import json
import pprint
import glob

sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
    import lib.requests as requests
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def execute(args):  
    pp = pprint.PrettyPrinter(indent=2)
    try:
    
        # verbose
        verbose = args['v']
        
        # veryverbose
        veryverbose = args['vv']
        if veryverbose:
            verbose = True
        
        # istSOS service
        service = args['s']
        
        # const constraint role
        role = "urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable"
        
        # filename
        csvfile = args['f']
        
        req = requests.session()
        
        # Open CSV file
        fo = open(csvfile, "rw+")
        
        #check file validity
        rlines = [ row.strip().split(",") for row in fo.readlines() if row.strip() is not ""]
        lines = []
        for line in rlines:
            lines.append([c.strip() for c in line ])
        # load sensor description
        res = req.get("%s/procedures/operations/getlist" % (service), 
                      prefetch=True, verify=False)
        
        jj = json.loads(res.content)
        if veryverbose:
            print "RETRIVING PRECEDURES..."
            pp.pprint(res.json)
            print "---------------------"
        elif verbose:
            if jj['success'] is False:
                pp.pprint(res.json)
                print "---------------------"
        
        procedures = dict( ( i["name"], [ j["name"] for j in i["observedproperties"] ] ) for i in jj["data"] )
        
        for nr,line in enumerate(lines):
            line = [ l.strip() for l in line ]
            if len(line)==4:
                if not line[0] in procedures.keys():
                    raise Exception("[line %s]: procedure '%s' not observed by the istsos service!" %(nr,line[0]) )
                if not "-".join(line[1].split(":")[-2:]) in procedures[line[0]]:
                    raise Exception("[line %s]: procedure '%s' does not observe property '%s'!" %(nr,line[0],line[1]) )
                if not (is_number(line[2]) or line[2] is ""):
                    raise Exception("[line %s]: value '%s' at column 3 should represent min values if present, check it is a number!" %(nr,line[2]) )
                if not (is_number(line[3]) or line[3] is ""):
                    raise Exception("[line %s]: value '%s' at column 4 should represent min values if present, check it is a number!" %(nr,line[3]) )
            else:
                raise Exception("[line %s]: %s input file must contain 4 row: station name, observed property URI, min, max" %(nr,line))
        
        for nr,line in enumerate(lines):
            if line:
                # load sensor description
                res = req.get("%s/procedures/%s" % (service,line[0]), 
                              prefetch=True, verify=False)
                
                ds = json.loads(res.content)
                if veryverbose:
                    print "RETRIVING PRECEDURES..."
                    pp.pprint(res.json)
                    print "---------------------"
                elif verbose:
                    if ds['success'] is False:
                        pp.pprint(res.json)
                        print "---------------------"
                                
                #update constraints in Json
                for opr in ds["data"]["outputs"]:
                    if opr["definition"] == line[1]:
                        opr["constraint"] = {}
                        opr["constraint"]["role"]=role
                        if line[2] and line[3]:
                            opr["constraint"]["interval"]=[float(line[2]),float(line[3])]
                        elif not line[2] and line[3]:
                            opr["constraint"]["max"]=float(line[3])
                        elif line[2] and not line[3]:
                            opr["constraint"]["min"]=float(line[2])
                
                # send Json request to update constrain on service
                res = req.put("%s/procedures/%s" % (service,line[0]),
                            prefetch=True,
                            verify=False,
                            data=json.dumps(ds["data"])
                        )
                # read response
                jj = json.loads(res.content)
                if veryverbose:
                    print "SAVING PRECEDURE %s..." % line[0]
                    pp.pprint(json.dumps(ds["data"]))
                    print "---------------------"
                
                print "---------------------"
                print " > Updated %s procedure success: %s" %(line[0],res.json['success'])

                if verbose:
                    if jj['success'] is False:
                        pp.pprint(res.json)
                
                print "---------------------"
                
                
    except Exception as e:
        print "ERROR: %s\n\n" % e
        traceback.print_exc()
            
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Update PROCEDUREs constraints from CSV file with line format: PROCEDURE_NAME,OBSERVED_PROPERTY_URN,MIN,MAX,ROLE')
    
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
    
    parser.add_argument('-vv','--veryverbose',
        action = 'store_true',
        dest   = 'vv',
        help   = 'Activate very verbose debug')
        
    parser.add_argument('-f','--file',
        action = 'store',
        required=True,
        dest   = 'f',
        help   = 'CSV file path')
        
    parser.add_argument('-s', '--istsos',
        action='store',
        required=True,
        dest='s',
        help='istSOS WA service address (e.g.: http://localhost/istsos/wa/istsos/services/demo).')
    
    
    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)

   