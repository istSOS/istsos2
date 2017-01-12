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
'''
This script get creates an HQ virtual procedure from an existing virtual procedure and curve rating file

Usage example: 
    
python scripts/sos_virtual_importer.py \
    -s http://localhost/istsos \
    -n sos \
    -vp Q_MAG_LOD \
    -sp A_MAG_LOD \
    -so urn:ogc:def:parameter:x-istsos:1.0:river:water:height \
    -sf test/scripts/data/in/HQ_curves/A_MAG_LOD_HQ.dat

'''

import sys
import traceback
import json
import pprint
from os import path

print path.abspath(".")
print path.normpath("%s/../" % path.abspath("."))
print path.abspath(path.dirname(__file__))
print path.normpath("%s/../../" % path.abspath(__file__))

sys.path.insert(0, path.abspath("."))

try:
    import lib.requests as req
    import lib.argparse as argparse
except ImportError as e:
    
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    exit()
    #raise e
    
fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
fmtshort = '%Y-%m-%dT%H:%M%z'

proc = """{"system_id":"V_TEST",
           "system":"V_TEST",
           "description":"",
           "keywords":"",
           "identification":[{
                    "definition":"urn:ogc:def:identifier:OGC:uniqueID",
                    "name":"uniqueID",
                    "value":""
            }],
           "classification":[
               {"name":"System Type",
                "definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
                "value":"virtual"},
               {"name":"Sensor Type",
                "definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
                "value":"virtual"}],
           "characteristics":"",
           "contacts":[],
           "documentation":[],
           "capabilities":[],
           "location":{},
           "interfaces":"",
           "inputs":[],
           "outputs":[
               {"name":"Time",
                "definition":"urn:ogc:def:parameter:x-istsos:1.0:time:iso8601",
                "uom":"iso8601",
                "description":"",
                "constraint":{}},
               {"name":"water-discharge",
                "definition":"urn:ogc:def:parameter:x-istsos:1.0:river:water:discharge",
                "uom":"m3/s",
                "description":"",
                "constraint":{}}],
            "history":[]}"""
            
def RCload(filename):
    #load HQ virtual procedure conf file to a list of dictionaries
    cvlist=[]
    with open(filename) as f:
        lines = f.readlines()
        items = [ i.strip().split("|") for i in lines if i.strip()!="" ]
        fields = items[0]
        for i in range(1,len(items)):
            cvdict = {}
            for f, field in enumerate(fields):
                cvdict[field]= items[i][f]
            cvlist.append(cvdict)
    return cvlist
    
def execute (args):  
    pp = pprint.PrettyPrinter(indent=2)
    try:

        sosurl = args['s']
        sosservice = args['n']
        vproc = args['vproc']
        sproc = args['sproc']
        sobs = args['sobs']
        sfile = args['sfile']
        #verbose = args['v']
        
        # get source procedure
        #======================
        spr = req.get("%s/wa/istsos/services/%s/procedures/%s" % (sosurl,sosservice,sproc))
        if not spr.json["success"]:
            raise Exception("Getting procedure description for '%s' unsuccessfull" % sproc)
        
        # creating the virtual procedure
        #======================
        npv = json.loads(proc)
        
        #-- set new procedure name        
        npv['system_id'] = vproc
        npv['system'] = vproc
        npv["identification"][0]["value"] = "urn:ogc:def:procedure:x-istsos:1.0:%s" % (vproc)
        
        #-- set new procedure systemType
        for c in npv['classification']:
            c['value']='virtual'
            
        #-- set new procedure FOI
        npv['location'] = spr.json['data']['location']
        
        #-- register new procedure 
        res = req.post("%s/wa/istsos/services/%s/procedures" % (sosurl,sosservice), 
                data=json.dumps(npv)
        )
        
        if not res.json["success"]:
            if res.json["message"].find("already exist")<0:
                raise Exception("Registering procedure %s failed: \n%s" % (vproc, res.json["message"]))
            else:
                cvlist = RCload(sfile)
                res = req.post("%s/wa/istsos/services/%s/virtualprocedures/%s/ratingcurve" % (sosurl,sosservice,vproc), 
                    data=json.dumps(cvlist)
                )
                if not res.json["success"]:
                    raise Exception("Saving rating curve %s failed: \n%s" % (vproc, res.json["message"]))
        else:
            # loading the virtual procedure code
            #===================================
            code = "# -*- coding: utf-8 -*-\n"
            code += "from istsoslib.responders.GOresponse import VirtualProcessHQ\n"
            code += "class istvp(VirtualProcessHQ):\n"
            code += "    # Declaring procedure from witch data will be calculated\n"
            code += "    procedures = {\n"
            found = False        
            for out in spr.json["data"]["outputs"]:
                if out["definition"]==sobs:
                    found = True
            if found:
                code += """        "%s": "%s"\n""" %(sproc,sobs)
            else:
                raise Exception("%s not observed by %s procedure" %(sproc,sobs))
            code += """    }\n"""
            
    
            scode = {"code":code}        
            
            res = req.post("%s/wa/istsos/services/%s/virtualprocedures/%s/code" % (sosurl,sosservice,vproc), 
                data=json.dumps(scode)
            )  
                        
            if not res.json["success"]:
                raise Exception("Saving code %s failed: \n%s" % (vproc, res.json["message"]))
             
            cvlist = RCload(sfile)
            print cvlist
            res = req.post("%s/wa/istsos/services/%s/virtualprocedures/%s/ratingcurve" % (sosurl,sosservice,vproc), 
                                data=json.dumps(cvlist)
                        )  
            if not res.json["success"]:
                raise Exception("Saving rating curve %s failed: \n%s" % (vproc, res.json["message"]))
        
            
    except Exception as e:    
        print "ERROR: %s\n\n" % e
        #traceback.print_exc()
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Import data from an external SOS to an istSOS instance.')

    parser.add_argument('-s',
        action = 'store',
        required=True,
        dest   = 's',
        metavar= 'soUrl',
        help   = 'SOS Server address IP (or domain name).')
    
    parser.add_argument('-n',
        action = 'store',
        required=True,
        dest   = 'n',
        metavar= 'service',
        help   = 'The name of the service instance.')
    
    parser.add_argument('-vp',
        action = 'store',        
        required=True,
        dest = 'vproc',
        metavar='virtualProcedure',
        help='Name of the new Virtual Procedure')
    
#    parser.add_argument('-vo',
#        action = 'store',
#        required=True,
#        dest = 'vobs',        
#        metavar='virtualObsProp',
#        help='Name of virtual observed property')
    
    parser.add_argument('-sp',
        action = 'store',
        required=True,
        dest = 'sproc',
        metavar='sourceProcedure',
        help='Name of the original Procedure which the virtual relies to')
        
    parser.add_argument('-so',
        action = 'store',
        required=True,
        dest = 'sobs',
        metavar='sourceObsProp',
        help='Name of original observed property which the virtual relies to')
    
    parser.add_argument('-sf',
        action = 'store',
        required=False,
        dest = 'sfile',
        metavar='sourceFile',
        default = None,
        help='Name of rating curve file which the virtual relies to')
    
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
        
       

    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)



