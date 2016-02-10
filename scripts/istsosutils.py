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

import sys
from datetime import timedelta
from datetime import datetime
import pprint
from StringIO import StringIO
import json
try:
    import lib.requests as req
    from lib.requests.auth import HTTPBasicAuth
    import lib.argparse as argparse
    from lib.etree import et
    import lib.isodate as iso
except ImportError as e:
    print "\nError loading internal libs:"
    raise e

class Service(object):

    """
    Base class handling istSOS WA requests
    """
    
    def __init__(self, host, service, basicAuth=None):
        """
        Initialize Service object
        """
        self.host = host
        self.service = service
        self.auth = None
        self.user = None
        self.password = None
        if basicAuth:
            self.user = basicAuth[0]
            self.password = basicAuth[1]
            self.auth = HTTPBasicAuth(self.user, self.password)
        
       
    def parse_and_get_ns(self, xml):
        events = "start", "start-ns"
        root = None
        ns = {}
        for event, elem in et.iterparse(xml, events):
            if event == "start-ns":
                if elem[0] in ns and ns[elem[0]] != elem[1]:
                    raise KeyError("Duplicate prefix with different URI found.")
                ns[elem[0]] = "%s" % elem[1]
            elif event == "start":
                if root is None:
                    root = elem 
        return et.ElementTree(root), ns
       
    def getSOSProcedureSamplingtime(self, name):
        """
            Execute a getObservation and extract the begin and endPosition.
            
            > Return an array of two dates.
        
        """        
        ret = self.extractSamplingFromGOJson(
            self.getSOSProcedure(name)
        )
        print " > %s: %s - %s" % (name, ret[0], ret[1]) 
        return ret
        
            
    def extractSamplingFromGOJson(self, json):
        
        if "beginPosition" in json["samplingTime"]:
            
            begin = json["samplingTime"]["beginPosition"]
            end = json["samplingTime"]["endPosition"]
            
        
            return [
                iso.parse_datetime(begin),
                iso.parse_datetime(end)
            ]
        
        else:
            return [None,None]
       
    def getSOSProceduresList(self): 
        """
            Execute a getCapabilties and extract all the procedures name.
            
            > Return an array of procedures name strings.  
        
        """
        # Executing request
        
        params = {
            'service': 'SOS', 
            'version': '1.0.0',
            'request': 'GetCapabilities',
            'section': 'contents'
        }
        
        print "Requesting a getCapabilitie: %s/%s" % (self.host,self.service)
        print params
        
        res = req.get("%s/%s" % (self.host,self.service), params=params, auth=self.auth)
        
        # Parsing response
        gc, gcNs = self.parse_and_get_ns(StringIO(res.content))
        
        offerings = gc.findall("{%s}Contents/{%s}ObservationOfferingList/{%s}ObservationOffering" % (gcNs['sos'],gcNs['sos'],gcNs['sos']) )
        
        procedures = {}
        
        for offering in offerings:
            offeringName = offering.find("{%s}name" % (gcNs['gml']) ).text.split(":")[-1]
            
            # For each offering get the procedures
            elProcs = offering.findall("{%s}procedure" % (gcNs['sos']) )
            for p in elProcs:
                pname = p.get('{%s}href' % gcNs['xlink'])
                
                procedures[pname] = True
                
                #print pname
                
        return procedures.keys()
        
        
    def getProcedures(self):
        res = req.get(
            "%s/wa/istsos/services/%s/procedures/operations/getlist" % (
                self.host,self.service
            ), auth=self.auth
        )
        json = res.json()
        if not json['success']:
            raise Exception("Error loading procedures list: %s" % (json['message']))     
        
        procedures = []
        for data in json['data']:
            procedure = Procedure(data['name'])
            procedure.merge(data)
            procedures.append(procedure)
        
        
        print "Procedures list result:"
        print " - Found: %s procedures" % len(procedures)
        
        
        return procedures
        
        
    def getProcedure(self,name):
        ret = Procedure(name)
        res = req.get(
            "%s/wa/istsos/services/%s/procedures/%s" % (
                self.host,self.service,name
            ), auth=self.auth
        )
        json = res.json()
        if not json['success']:
            raise Exception("Error loading %s description: %s" % (self.name, json['message']))        
        ret.description = json['data']
                
        return ret
        
    def getSOSProcedure(self,name):
    
        params = {
            'service': 'SOS', 
            'version': '1.0.0',
            'request': 'GetObservation',
            'observedProperty': ':',
            'offering': 'temporary',
            'responseFormat': 'application/json',
            'procedure': name
        }
        
        print "Requesting %s GetObservation: %s/%s" % (name,self.host,self.service)
        #print params
        
        res = req.get("%s/%s" % (self.host,self.service), params=params, auth=self.auth)
        
        #print res.json()
        
        
        
        json = res.json()['ObservationCollection']['member'][0]
        
        return json
    
    def registerProcedure(self, procedure):
        request = {
            "system_id": procedure.name,
            "system": procedure.name,
            "classification": [
                {
                    "name": "System Type",
                    "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType",
                    "value": procedure.systemType
                },
                {
                    "name": "Sensor Type",
                    "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType",
                    "value": procedure.sensorType
                }
            ],
            "outputs": [
                {
                    "name": "Time",
                    "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601",
                    "uom": "iso8601",
                    "description":"",
                    "constraint":{}
                }
            ],
            "description": procedure.description,
            "keywords": procedure.keywords,
            "identification": [{
                    "definition":'urn:ogc:def:identifier:OGC:uniqueID',
                    "name":"uniqueID",
                    "value": "urn:ogc:def:procedure:x-istsos:1.0:%s" % procedure.name
            }],
            "location": {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": procedure.xyz
                },
                "crs": {
                    "type": "name",
                    "properties": {"name": procedure.epsg}
                },
                "properties": {"name": procedure.foiname}
            },
            "characteristics": "",
            "contacts": [],
            "documentation": [],
            "interfaces": "",
            "inputs": [],
            "history": [],
            "capabilities": []
        }
        for obs in procedure.observedProperty:
            request["outputs"].append({
                "name": procedure.observedProperty[obs][0],
                "definition": procedure.observedProperty[obs][1],
                "uom": procedure.observedProperty[obs][2],
                "description": procedure.observedProperty[obs][3],
                "constraint":{}
            })
        res = req.post("%s/wa/istsos/services/%s/procedures" % (self.host,self.service), 
                data=json.dumps(request), auth=self.auth
        ) 
        json = res.json()
        if not json["success"]:
            #print json.dumps(procedures[pname].data)
            raise Exception("Registering procedure %s failed: \n%s" % (pname, json["message"]))
        else:
            print json["message"]
            
    def getSOSProcedureObservations(self, name, begin, end, qi = False):
        """
            Execute a getObservation
            
            > Return an array observations.  
        
        """
        begin1 = ""
        end1 = ""
        
        
        # Checking dates format
        if isinstance(begin, datetime):
            # Check tz
            if begin.tzinfo is None:
                raise Exception("Time Zone (tzinfo) is mandatory in datetime objects")
            begin1 = begin.isoformat()
        elif isinstance(begin, str):
            tmp = iso.parse_datetime(begin)
            if tmp.tzinfo is None:
                raise Exception("Time Zone (tzinfo) is mandatory in datetime objects")
            begin1 = tmp.isoformat()
            
            
        if isinstance(end, datetime):
            # Check tz
            if end.tzinfo is None:
                raise Exception("Time Zone (tzinfo) is mandatory in datetime objects")
            end1 = end.isoformat()
        elif isinstance(end, str):
            tmp = iso.parse_datetime(end)
            if tmp.tzinfo is None:
                raise Exception("Time Zone (tzinfo) is mandatory in datetime objects")
            end1 = tmp.isoformat()
            
        # Executing request
        res = req.get("%s/%s" % (self.host, self.service), params={
            'service': 'SOS', 
            'version': '1.0.0',
            'request': 'GetObservation',
            'offering': 'temporary',
            'responseFormat': 'application/json',
            'procedure': name,
            'qualityIndex': qi,
            'eventTime': "%s/%s" % (begin1,end1),
            'observedProperty': ":"
        }, auth=self.auth)
        
        json = res.json()
        
        return json['ObservationCollection']['member'][0]['result']['DataArray']['values']
        
    def getSharedProcedureListWith(self, service2):
        
        """
        
        Return a list of procedures equals in each istSOS service 
        
        """
        
        procedures1 = self.getSOSProceduresList()
        procedures2 = service2.getSOSProceduresList()

        procedures1 = [p.replace('urn:ogc:def:procedure:x-istsos:1.0:', '') for p in procedures1]
        procedures2 = [p.replace('urn:ogc:def:procedure:x-istsos:1.0:', '') for p in procedures2]

        procedures1.sort()
        procedures2.sort()

        procedures = [] # ListTable()

        stop1 = len(procedures1)
        stop2 = len(procedures2)
        cnt1 = cnt2 = 0
        stop = max(stop1,stop2)

        for i in range(0,stop):

            row = []
            tmp1 = None
            tmp2 = None
            
            if (cnt1)<stop1:
                tmp1 = procedures1[cnt1]
                
            if (cnt2)<stop2:
                tmp2 = procedures2[cnt2]
            
            if tmp1 == None:
                row = [None,tmp2]
                cnt1 += 1
                
            elif tmp2 == None:
                row = [tmp1,None]
                cnt2 += 1
                
            elif tmp1 == tmp2:
                row = [tmp1,tmp2]
                cnt1 += 1
                cnt2 += 1
                
            elif tmp1 < tmp2:
                row = [tmp1,None]

                cnt1 += 1
                
            elif tmp1 > tmp2:
                row = [None,tmp2]
                cnt2 += 1
                
            procedures.append(row)
            
            print row
            

        procedures = list(set(procedures1) & set(procedures2))
        procedures.sort()
        return procedures

class Procedure(dict):

    """
    Base class for istSOS WNS
    """
    def __init__(self, name=None):
        """
        Initialize Procedure object
        """
        self.name = name
        self.outputs = []
        self.observedProperty = {}
        
    def merge(self, data):
        for key in data:
            self[key] = data[key]
        
    def setName(self,name):
        self.name = name
    
    def setDescription(self,description):
        self.description = description
        
    def setKeywords(self,keywords):
        self.keywords = keywords
        
    def setSystemType(self, systemType):
        if systemType in ['virtual','insitu-fixed-point']:
            self.systemType = systemType
        else:
            raise Exception("System type supported virtual, insitu-fixed-point only.")
                
    def setSensorType(self, sensorType):
        self.sensorType = sensorType    
    
    def setFoi(self, name, epsg, x, y, z):
        """ 
        name: feature of interest name
        epsg: coordinates system
        xyz: array of coordinates 
        """
        self.foiname = name
        self.epsg = epsg
        self.xyz = [x,y,z]
    
    def addObservedProperty(self, name, definition, uom, description=""):
        self.observedProperty[name] = [name, definition, uom, description]
        
        
        
        
        
        
