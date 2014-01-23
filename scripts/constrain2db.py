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
# Created on Mon Jan 20 12:05:08 2014
#---------------------------------------------------------------------------
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

def execute(args):  
    pp = pprint.PrettyPrinter(indent=2)
    try:
    
        # verbose
        verbose = args['v']
        
        # istSOS service
        service = args['s']
        
        # const constraint role
        role = args['r']
        
        # filename
        csvfile = args['f']
        
        req = requests.session()
        
        # Open CSV file
        fo = open(csvfile, "rw+")
        for row in fo.readlines():
            if len(row.strip())>0:
                #put line in line list
                line = row.split(",")
                # load sensor description
                res = req.get("%s/procedures/%s" % (service,line[0]), 
                              prefetch=True, verify=False)
                
                if verbose:
                    pp.pprint(res.json)
                    print "---------------------"
                
                    
                ds = json.loads(res.content)
                                
                #update constraints in Json
                for opr in ds["data"]["outputs"]:
                    if opr["definition"] == line[1]:
                        opr["constraint"] = {}
                        if role:
                            opr["constraint"]["role"]=role
                        else:
                            try:
                                opr["constraint"]["role"]=line[4]
                            except:
                                pass
                        if line[2] and line[3]:
                            opr["constraint"]["interval"]=[float(line[2]),float(line[3])]
                        elif not line[2] and line[3]:
                            opr["constraint"]["max"]=line[3]
                        elif line[2] and not line[3]:
                            opr["constraint"]["min"]=line[2]
                
                # send Json request to update constrain on service
                res = req.put("%s/procedures/%s" % (service,line[0]),
                            prefetch=True,
                            verify=False,
                            data=json.dumps(ds["data"])
                        )
                        # read response
                if verbose:
                    pp.pprint(res.json)
                    print "---------------------"
                else:
                    print " > Updated procedure success: %s" % res.json['success']
                
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
        
    parser.add_argument('-f','--file',
        action = 'store',
        required=True,
        dest   = 'f',
        help   = 'CSV file path')
        
    parser.add_argument('-s', '--istsos',
        action='store',
        required=True,
        dest='s',
        help='istSOS service address.')
    
    parser.add_argument('-r', '--role',
        action='store',
        required=True,
        dest='r',
        help='constant constraint role.to use')
    
    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)

   