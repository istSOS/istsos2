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
This script get minimal metadata from an existing SOS and populate an istsos instance
'''

import sys
import traceback
import json
import pprint
from datetime import timedelta
import calendar
import time
from StringIO import StringIO
from os import path

#print path.abspath(".")
#print path.normpath("%s/../" % path.abspath("."))
#print path.abspath(path.dirname(__file__))
#print path.normpath("%s/../../" % path.abspath(__file__))

sys.path.insert(0, path.abspath("."))
try:
    import lib.requests as req
    from lib.requests.auth import HTTPBasicAuth
    import lib.argparse as argparse
    from lib.etree import et
    import lib.isodate as iso
except ImportError as e:
    
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    exit()
    #raise e
    
fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
fmtshort = '%Y-%m-%dT%H:%M%z'

class Procedure():
    def __init__(self,name,offering,url,service,auth=None):
        self.offering = offering
        self.url = url
        self.service = service
        self.oid = ""
        self.begin = ""
        self.end = ""
        self.template = None
        self.auth = auth
        self.data = {
            "system_id": "",
            "system": "",
            "classification": [
                {
                    "name": "System Type",
                    "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType",
                    "value": "insitu-fixed-point"
                },
                {
                    "name": "Sensor Type",
                    "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType",
                    "value": "unknown"
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
            "description": "",
            "keywords": "",
            "identification": [{
                    "definition":'urn:ogc:def:identifier:OGC:uniqueID',
                    "name":"uniqueID",
                    "value":""
            }],
            "characteristics": "",
            "contacts": [{"role":"urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:owner","organizationName":"Istituto scienze della Terra","individualName":"Maurizio Pozzoni","voice":"+41(0)586666200","fax":"+41(0)586666209","email":"ist@supsi.ch","web":"http://www.supsi.ch/ist","deliveryPoint":"Via Trevano, c.p. 72","city":"Canobbio","administrativeArea":"Ticino","postalcode":"6952","country":"Svizzera"}],
            "documentation": [],
            "interfaces": "",
            "inputs": [],
            "history": [],
            "capabilities": []
        }
        self.data["system"] = name
        self.data["system_id"] = name
        self.data["identification"][0]["value"] = "urn:ogc:def:procedure:x-istsos:1.0:%s" % (name)
    
    def __str__(self):
        return "%s, samplingTime: %s - %s" % (self.data["system"], self.begin, self.end)
    
    def setSystemType(self, systemType):
        if systemType in ['virtual','insitu-fixed-point']:
            self.data['location']['classification'][0]['value'] = systemType
        else:
            raise Exception("System type supported virtual, insitu-fixed-point only.")
    
    def setFoi(self, name, epsg, point):
        
        not_allowed_NCName = [' ', '!','"', '#', '$', '%', '&', '\'', 
                          '(', ')', '*', '+', ',', '/', ':', ';', 
                          '<', '=', '>', '?', '@', '[', '\\', ']', 
                          '^', '`', '{', '|', '}', '~']
                          
        for c in not_allowed_NCName:
            name = name.replace(c,'_')
                
        self.data['location'] = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": point
            },
            "crs": {
                "type": "name",
                "properties": {"name": epsg}
            },
            "properties": {"name": name.replace(' ','_')}
        }
    
    def addObservedProperty(self, name, definition, uom):
        self.data["outputs"].append({
            "name":name,
            "definition":"urn:ogc:def:parameter:x-istsos:1.0:%s" % definition,
            "uom":uom,
            "description":"",
            "constraint":{}
        });
        
    def getIoTemplate(self):
        if not self.template:
            res = req.get(
                "%s/wa/istsos/services/%s/operations/getobservation/offerings/%s/procedures/%s/observedproperties/urn/eventtime/last" % (
                    self.url,
                    self.service,
                    self.offering,
                    self.data["system"]
                ), auth=self.auth
            )
            try:
                self.template = res.json()['data'][0]
            except Exception as e:
                print res.text
                raise e
        return self.template #res.json()['data'][0]

    
def parse_and_get_ns(xml):
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
   
def execute (args):
    pp = pprint.PrettyPrinter(indent=2)
    try:
    
        istsos_version = args['istsos'] if 'istsos' in args else None
        
        debug = args['v']
        test = args['t']
        
        procs = args['p']
        omit = args['o']
        procedures = {}
        
        src = args['s']
        dst = args['d']
        srv = args['n']
        
        duser = None
        if 'du' in args:
            duser = args['du']
        dpassw = None
        if 'dp' in args:
            dpassw = args['dp']
            
        #print "%s:%s" % (duser,'*'*len(dpassw))
            
        auth = None
        if duser and dpassw:
            print "User and password!"
            auth = HTTPBasicAuth(duser, dpassw)
        
        appendData = False
        if 'a' in args and args['a']:
            print "Append data: enabled."
            appendData = True
        
        
        dfrom = None
        dto = None
        if 'from' in args and type('') == type(args['from']):
            print "From: %s" % args['from']
            dfrom = iso.parse_datetime(args['from'])
            appendData = None
        if 'to' in args and type('') == type(args['to']):
            print "To: %s" % args['to']
            dto = iso.parse_datetime(args['to'])
            appendData = None
        
        registerOnly = args['r']
        
        virtual = False
        hq = False
        
        
        # Executing request
        res = req.get("%s" % (src), params={
            'service': 'SOS', 
            'version': '1.0.0',
            'request': 'GetCapabilities',
            'section': 'contents'
        }, verify=False)
        
        # Parsing response
        gc, gcNs = parse_and_get_ns(StringIO(res.content))
        
        # Extract all offerings
        elOfferings = gc.findall("{%s}Contents/{%s}ObservationOfferingList/{%s}ObservationOffering" % (gcNs['sos'],gcNs['sos'],gcNs['sos']))
        
        for offering in elOfferings:
            offeringName = offering.find("{%s}name" % (gcNs['gml']) ).text.split(":")[-1]
            
            if offeringName != 'temporary':
                continue
            
            # For each offering get the procedures
            elProcs = offering.findall("{%s}procedure" % (gcNs['sos']) )
            for p in elProcs:
                pname = p.get('{%s}href' % gcNs['xlink'])
                
                if (
                        type(procs) == type([]) and pname not in procs
                    ) or (
                        type(omit) == type([]) and pname in omit
                    ):
                    continue
                    
                print "\n%s" % pname
                print "================================"
                
                procedures[pname] = Procedure(pname, offeringName, dst, srv, auth)
                
                if virtual:
                    procedures[pname].setSystemType('virtual')
                               
                res = req.get("%s" % (src), params={
                    'service': 'SOS', 
                    'version': '1.0.0',
                    'request': 'DescribeSensor',
                    'outputFormat': 'text/xml;subtype=\'sensorML/1.0.0\'',
                    'procedure': pname
                }, verify=False)
                
                #print res.content
                
                ds, dsNs = parse_and_get_ns(StringIO(res.content))
                
                #print res.content
                
                
                #print "Root: %s" % ds.getroot().tag
                if ds.getroot().tag == 'ExceptionReport':
                    print "Error on DS for %s" % pname
                    continue
                    
                
                
                #print "Outputs found: %s" % len(elDescribe)
                
                observedProperties = []
                print "istsos_version: ", istsos_version
                uniqidurn = 'urn:ogc:def:parameter:x-ist::'
                if istsos_version != None and istsos_version == '2':
                    uniqidurn = 'urn:ogc:def:parameter:x-ist:1.0:'
                    elFields = ds.findall("{%s}member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output/{%s}DataRecord/{%s}field" % (
                                    dsNs['sml'],dsNs['sml'],dsNs['sml'],dsNs['sml'],dsNs['sml'],dsNs['swe'],dsNs['swe']) )
                    print "Observed properties (v2): %s " % len(elFields)
                    for fs in elFields:
                        print fs.get('name')
                        if fs.get('name') != 'Time':
                            observedProperties.append(fs.find("{%s}Quantity" % (dsNs['swe'])).get('definition').replace(uniqidurn,''))
                        
                else:
                    elDescribe = ds.findall("member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output" % (dsNs['sml'],dsNs['sml'],dsNs['sml'],dsNs['sml']) )
                    print "Observed properties: %s " % len(elDescribe)
                    for ds in elDescribe:
                        definition = ds.find("{%s}ObservableProperty" % (dsNs['swe'])).get('definition').replace(uniqidurn,'')
                        #print definition
                        if definition.find('time:iso8601')<0:
                            observedProperties.append(definition)
                            
                #print {
                #    'service': 'SOS', 
                #    'version': '1.0.0',
                #    'request': 'GetObservation',
                #    'offering': offeringName,
                #    'responseFormat': 'text/xml;subtype=\'sensorML/1.0.0\'',
                #    'procedure': pname,
                #    'observedProperty': ",".join(observedProperties)
                #}
                
                res = req.get("%s" % (src), params={
                    'service': 'SOS', 
                    'version': '1.0.0',
                    'request': 'GetObservation',
                    'offering': offeringName,
                    'responseFormat': 'text/xml;subtype=\'sensorML/1.0.0\'',
                    'procedure': pname,
                    'observedProperty': ",".join(observedProperties)
                }, verify=False)
                              
                go, goNs = parse_and_get_ns(StringIO(res.content))
                
                
                if go.getroot().tag == 'ExceptionReport':
                    print "Error on GO for %s:\nparams:%s\n%s" % (pname,{
                        'service': 'SOS', 
                        'version': '1.0.0',
                        'request': 'GetObservation',
                        'offering': offeringName,
                        'responseFormat': 'text/xml;subtype=\'sensorML/1.0.0\'',
                        'procedure': pname,
                        'observedProperty': ",".join(observedProperties)
                    },res.content)
                    continue
                
                # Extracting begin and end position
                begin = go.find("{%s}member/{%s}Observation/{%s}samplingTime/{%s}TimePeriod/{%s}beginPosition" % (
                    goNs['om'], goNs['om'], goNs['om'], goNs['gml'], goNs['gml'])
                )
                end = go.find("{%s}member/{%s}Observation/{%s}samplingTime/{%s}TimePeriod/{%s}endPosition" % (
                    goNs['om'], goNs['om'], goNs['om'], goNs['gml'], goNs['gml'])
                )
                procedures[pname].begin = begin.text
                procedures[pname].end  = end.text
                
                # Extracting Feature of Interest and coordinates
                foi = go.find("{%s}member/{%s}Observation/{%s}featureOfInterest" % (
                    goNs['om'], goNs['om'], goNs['om'])
                )
                point = foi.find("{%s}Point" % (
                    goNs['gml'])
                )
                
                if point == None:
                    point = foi.find("{%s}FeatureCollection/{%s}location/{%s}Point" % (
                        goNs['gml'],goNs['gml'],goNs['gml'])
                    )
                
                coord = point.find("{%s}coordinates" % (
                    goNs['gml'])
                ).text.split(",")
                
                if len(coord) == 2:
                    coord.append('0')
                
                procedures[pname].setFoi(
                    foi.get('{%s}href' % gcNs['xlink']).split(":")[-1],
                    point.get('srsName'),
                    coord
                )
                
                # Extracting UOM
                fields = go.findall("{%s}member/{%s}Observation/{%s}result/{%s}DataArray/{%s}elementType/{%s}DataRecord/{%s}field" % (
                    goNs['om'], goNs['om'], goNs['om'], goNs['swe'], goNs['swe'], goNs['swe'], goNs['swe'])
                )
                
                for field in fields:
                    if field.get('name')!='Time':
                        qty = field.find("{%s}Quantity" % (
                            goNs['swe'])
                        )
                        uom = field.find("{%s}Quantity/{%s}uom" % (
                            goNs['swe'],goNs['swe'])
                        )                        
                        procedures[pname].addObservedProperty(
                            field.get('name'),
                            qty.get('definition').replace(uniqidurn,''), 
                            uom.get('code')
                        )
                
                if dfrom:
                    begin = dfrom
                    _begin = dfrom
                else:
                    begin = iso.parse_datetime(procedures[pname].begin)
                    _begin = iso.parse_datetime(procedures[pname].begin)
                    
                if dto:
                    end = dto
                else:
                    end = iso.parse_datetime(procedures[pname].end)
                
                # ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
                # REGISTRATION PROCESS
                # ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
                
                # Check if procedure already exist
                res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (dst,srv,pname), auth=auth, verify=False)  
                if not res.json()["success"]:
                    #print procedures[pname].data
                    # Registering procedure to istSOS   
                    res = req.post("%s/wa/istsos/services/%s/procedures" % (dst,srv), 
                            data=json.dumps(procedures[pname].data), auth=auth
                    ) 
                    if not res.json()["success"]:
                        #print json.dumps(procedures[pname].data)
                        raise Exception("Registering procedure %s failed: \n%s" % (pname, res.json()["message"]))
                    
                    # Getting details (describe sensor) to get the assignedSensorId
                    res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (dst,srv,pname), auth=auth)  
                    
                    # Getting an InsertObservation template
                    template = procedures[pname].getIoTemplate()  
                    
                else:
                    # Getting an InsertObservation template
                    template = procedures[pname].getIoTemplate()  
                    try:
                        if appendData and ('endPosition' in template['samplingTime']):
                            procedures[pname].begin = template['samplingTime']['endPosition']
                            begin = iso.parse_datetime(template['samplingTime']['endPosition'])     
                    except Exception as exproc:
                        print res.text
                        raise exproc
                
                procedures[pname].oid = res.json()["data"]["assignedSensorId"]
                days = int(args['i'])
                interval = timedelta(days=int(days))
                
                
                if not registerOnly:
                
                    if virtual and hq:
                        # ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
                        # VIRTUAL PROCEDURE CODE INITIALIZATION
                        # ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
                        pass
                        
                    else:
                        print "Starting migration.."
                        
                        # ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
                        # PROCEDURE OBSERVATIONS MIGRATION
                        # ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
                        
                        oOrder = []
                        
                        passedLoops = 0
                        
                        lastPrint = ""
                        
                        startTime = time.time()
                        
                        print "%s: %s - %s" % (pname, procedures[pname].begin, procedures[pname].end)
                        
                        if begin<end and begin+interval>end:
                            interval = end-begin
                        
                        while (begin+interval)<=end:
                            loopTotalTime = time.time()
                                
                            nextPosition = begin + interval
                            
                            passedLoops = passedLoops+1
                            
                            t = float(calendar.timegm(end.utctimetuple())-calendar.timegm(_begin.utctimetuple()))
                            t1 = float(calendar.timegm(nextPosition.utctimetuple())-calendar.timegm(_begin.utctimetuple()))
                            try:
                                percentage = round((t1/t)*100,2)
                            except:
                                percentage = 0
                            if percentage > 100:
                                percentage = 100
                            lastPrint = "%s > %s%% (%s / %s %s days)" % ("\b"*len(lastPrint),percentage, begin.strftime(fmtshort), nextPosition.strftime(fmtshort), days)
                            
                            looptime = time.time()
                            # GetObservation from source SOS
                            params={
                                'service': 'SOS', 
                                'version': '1.0.0',
                                'request': 'GetObservation',
                                'eventTime': '%s/%s' % (
                                        begin.strftime(fmt),
                                        nextPosition.strftime(fmt)),
                                'qualityIndex': 'True',
                                'offering': offeringName,
                                'responseFormat': 'text/xml;subtype=\'sensorML/1.0.0\'',
                                'procedure': pname,
                                'observedProperty': ",".join(observedProperties)
                            }
                            try:
                                res = req.get("%s" % (src), params=params, verify=False)
                            except Exception:
                                res = req.get("%s" % (src), params=params, verify=False)
                            
                            gotime = timedelta(seconds=int(time.time() - looptime))
                            
                            if gotime > timedelta(seconds=int(10)):
                                if days > 1:
                                    days = int(days/2)
                                    if days <= 1:
                                        days = 1 
                                interval = timedelta(days=days)
                            elif gotime < timedelta(seconds=int(5)):
                                days = days + 1
                                interval = timedelta(days=days)
                            
                            lastPrint = "%s - GO: '%s'" % (lastPrint, gotime)
                            
                            go, goNs = parse_and_get_ns(StringIO(res.content))
                                                        
                            if len(oOrder)==0:
                                fields = go.findall("{%s}member/{%s}Observation/{%s}result/{%s}DataArray/{%s}elementType/{%s}DataRecord/{%s}field" % (
                                    goNs['om'], goNs['om'], goNs['om'], goNs['swe'], goNs['swe'], goNs['swe'], goNs['swe'])
                                )
                                for field in fields:
                                    oOrder.append(qty.get('definition').replace('urn:ogc:def:parameter:x-ist::',''))
                            
                            values = go.find("{%s}member/{%s}Observation/{%s}result/{%s}DataArray/{%s}values" % (
                                goNs['om'], goNs['om'], goNs['om'], goNs['swe'], goNs['swe'])
                            )
                            
                            if values.text:
                            
                                rows = values.text.strip().split("@")
                                
                                lastPrint = "%s " % (lastPrint)
                                
                                copy = []
                                
                                for row in rows:
                                    copy.append(row.split(","))
                                
                                # InsertObservation to istSOS
                                template['result']['DataArray']['values'] = copy
                                template['samplingTime'] = {
                                    "beginPosition": copy[0][0],
                                    "endPosition": nextPosition.strftime(fmt)
                                }
                                '''template['samplingTime'] = {
                                    "beginPosition": begin.strftime(fmt),
                                    "endPosition": nextPosition.strftime(fmt)
                                }'''
                                
                                template[u"AssignedSensorId"] = procedures[pname].oid
                                
                                looptime = time.time() 
                                res = req.post("%s/wa/istsos/services/%s/operations/insertobservation" % (
                                    dst,
                                    srv
                                ), auth=auth, data = json.dumps({
                                    u"AssignedSensorId": procedures[pname].oid,
                                    u"ForceInsert": u"true",
                                    u"Observation": template
                                }))
                                
                                iotime = timedelta(seconds=int(time.time() - looptime))
                                lastPrint = "%s - IO: '%s'" % (lastPrint, iotime)
                                                    
                            begin = nextPosition
                            if begin<end and begin+interval>end:
                                interval = end-begin
                                
                            if percentage < 100:
                                lastPrint = "%s - Step time: '%s' - Elapsed: %s  " % (
                                    lastPrint, 
                                    timedelta(seconds=int(time.time() - loopTotalTime)), 
                                    timedelta(seconds=int(time.time() - startTime))
                                )
                            else:
                                lastPrint = "%s - Step time: '%s'  " % (
                                    lastPrint, 
                                    timedelta(seconds=int(time.time() - loopTotalTime))
                                )
                            
                            sys.stdout.write(lastPrint)
                            sys.stdout.flush()
                        
                        
                        print " > Completed in %s" % timedelta(seconds=int(time.time() - startTime))
            break
    except Exception as e:    
        print "ERROR: %s\n\n" % e
        traceback.print_exc()
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Import data from an external SOS to an istSOS instance.')
    
    parser.add_argument('--istsos',
        action = 'store',
        dest   = 'istsos',
        metavar= 'istsos',
        help   = 'Set source istSOS version (accepted versions only 2)')
        
    parser.add_argument('-p', 
        action='store',
        dest='p',
        nargs='+',
        metavar='procedures',
        default= 'ALL',
        help='List of procedures to be migrated, (default: %(default)s).')
        
    parser.add_argument('-o', 
        action='store',
        dest='o',
        nargs='+',
        metavar='procedures',
        help='List of procedures to be omitted.')
        
    parser.add_argument('-s',
        action = 'store',
        required=True,
        dest   = 's',
        metavar= 'surl',
        help   = 'Source SOS Server address IP (or domain name).')
        
    parser.add_argument('-d',
        action = 'store',
        required=True,
        dest   = 'd',
        metavar= 'durl',
        help   = 'Destination istSOS Server address IP (or domain name).')
    
    parser.add_argument('-n',
        action = 'store',
        required=True,
        dest   = 'n',
        metavar= 'service',
        help   = 'The name of the service instance.')
    
    parser.add_argument('-r','--registeronly',
        action = 'store_true',
        dest   = 'r',
        help   = 'Add this parameter if you want to register the procedures without migrating the data.')
    
    
    parser.add_argument('-a',
        action = 'store_true',
        dest   = 'a',
        help   = 'Add this parameter, if you want to append after existing observations instead of replacing all the dataset.')
    
    parser.add_argument('--from', 
        action='store',
        dest='from',
        default= None,
        help='Import observations from date (ISODATE Format).')  
        
    parser.add_argument('--to', 
        action='store',
        dest='to',
        default= None,
        help='Import observations to date (ISODATE Format).')  
        
    parser.add_argument('-i', 
        action='store',
        dest='i',
        default= '14',
        help='Days interval, (default: %(default)s).')  
          
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
        
    parser.add_argument('-t','--test',
        action = 'store_true',
        dest   = 't',
        help   = 'Use to test the command, deactivating the insert observation operations.')
        
    parser.add_argument('-du',
        action = 'store',
        dest   = 'du',
        metavar= 'destination user name')
        
    parser.add_argument('-dp',
        action = 'store',
        dest   = 'dp',
        metavar= 'destination password')

    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)



