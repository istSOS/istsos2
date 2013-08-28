# -*- coding: utf-8 -*-
import sys
from os import path
sys.path.insert(0, path.abspath(path.dirname(__file__)))

import test.walib.istsos.services.configsections as conf
import test.walib.istsos.services.dataqualities as data
import test.walib.istsos.services.epsgs as eps
import test.walib.istsos.services.observedproperties as obsprop
import test.walib.istsos.services.offerings as offer
import test.walib.istsos.services.operations as oper
import test.walib.istsos.services.procedures as proc
import test.walib.istsos.services.services as ser
import test.walib.istsos.services.systemtypes as syst
import test.walib.istsos.services.uoms as uom
import test.istsoslib.sosRequests as sos
import lib.argparse as argparse

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)

def run_tests(arg):
    
    verb = arg['v']
        
    
    if verb:
        f = open(path.abspath(path.dirname(__file__))+'/logs/test.log', 'w')
    else:
        f = None
    
    #=======================================================================    
    # CREATE A TEST ENVIRONMENT
    #=======================================================================
    #----- SET SOS SERVER CONFIGURATION ---------
    config = {
        "getobservation": {
            "maxgoperiod": "200", 
            "aggregatenodataqi": "-100", 
            "defaultqi": "100", 
            "aggregatenodata": "-999.9",
            "correct_qi" : "110",
            "stat_qi" : "200",
            "transactional_log" : "True"
            }, 
        "urn": {
            "process": "urn:ogc:def:process:x-istsos:1.0:", 
            "property": "urn:ogc:def:property:x-istsos:1.0:", 
            "offering": "urn:ogc:def:offering:x-istsos:1.0:", 
            "sensor": "urn:ogc:def:sensor:x-istsos:1.0:", 
            "phenomena": "urn:ogc:def:phenomenon:x-istsos:1.0:", 
            "feature": "urn:ogc:def:feature:x-istsos:1.0:", 
            "sensorType": "urn:ogc:def:sensorType:x-istsos:1.0:", 
            "dataType": "urn:ogc:def:dataType:x-istsos:1.0:", 
            "role": "urn:role:x-istsos:1.0:", 
            "refsystem": "urn:ogc:crs:EPSG:", 
            "time": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "keywords": "urn:ogc:def:keywords:x-istsos:1.0:", 
            "identifier": "urn:ogc:def:identifier:x-istsos:1.0:", 
            "parameter": "urn:ogc:def:parameter:x-istsos:1.0:", 
            "procedure": "urn:ogc:def:procedure:x-istsos:1.0:"
            }, 
        "connection": { 
            "dbname": arg['dbname'], 
            "host": arg['host'], 
            "user": arg['user'], 
            "password": arg['password'], 
            "port": arg['port']
            }, 
        "identification": {
            "title": "IST Sensor Observation Service 1", 
            "abstract": "hydro-meteorological monitoring network", 
            "urnversion": "1.0", 
            "authority": "x-istsos", 
            "fees": "NONE", 
            "keywords": "SOS,IST,SUPSI", 
            "accessconstrains": "NONE"
            }, 
        "serviceurl": {
            "url": "http://localhost/istsos/test"
            }, 
        "provider": {
            "contactcountry": "Switzerland", 
            "providername": "Istituto Scienze della Terra", 
            "contactposition": "Data manager", 
            "contactvoice": "+41586666200", 
            "contactadminarea": "Canton Ticino", 
            "contactemail": "geoservice@supsi.ch", 
            "contactdeliverypoint": "Campus Trevano", 
            "contactname": "Team Geomatica", 
            "contactpostalcode": "6952", 
            "contactcity": "Canobbio", 
            "providersite": "http://www.supsi.ch/ist", 
            "contactfax": "+41000000000000"
            }, 
        "geo": {
            "zaxisname": "altitude", 
            "xaxisname": "easting", 
            "yaxisname": "northing", 
            "allowedepsg": "4326,3857", 
            "istsosepsg": "21781"
            }
        } 
    address = 'http://localhost/istsos/wa/istsos/services/default/configsections'
    res = tput.PUT("", config, address)
    if not res['success']:
        raise SystemError("Unable to configure the SOS server: %s" % res['message'])
    
    #----- CREATE A SOS SERVICE ---------
    service = {
        "service": "test"
    }
    address = 'http://localhost/istsos/wa/istsos/services'
    res = tpost.POST("",service,address)
    if not res['success']:
        raise SystemError("Unable to create a new SOS service: %s" % res['message'])
    #----- ADD UNIT OF MEASURE ------
    tuom = {
        "name": "test", 
        "description": "test unit of measure"
        }
    address = 'http://localhost/istsos/wa/istsos/services/test/uoms'
    res = tpost.POST("",tuom,address)
    if not res['success']:
        raise SystemError("Unable to create a new SOS unit of measure: %s" % res['message'])
    #----- ADD OBSERVED PROPERTY ------
    opr = {
        "definition": "urn:ogc:def:parameter:x-istsos:1.0:test", 
        #"procedures": [], 
        "constraint": [],
        "name": "test", 
        "description": "test observed property"
        }
    address = 'http://localhost/istsos/wa/istsos/services/test/observedproperties'
    res = tpost.POST("",opr,address)
    if not res['success']:
        raise SystemError("Unable to create a new SOS observed property: %s" % res['message'])
    #----- ADD PROCEDURE ------
    tproc = {
        "inputs": [], 
        "description": "test procedure", 
        "classification": [
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType", 
            "name": "System Type", 
            "value": "insitu-fixed-point"
            }, 
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType", 
            "name": "Sensor Type", 
            "value": "test"
            }
        ], 
        "characteristics": "", 
        "interfaces": "", 
        "keywords": "A,B,C", 
        "contacts": [], 
        #"assignedSensorId": "6ecb65065eccaac8967089df62c81a24", 
        "documentation": [], 
        "system": "test", 
        "capabilities": [], 
        "identification": [], 
        "location": {
            "geometry": {
                "type": "Point", 
                "coordinates": ["1", "1", "1"]
                }, 
            "crs": {
                "type": "name", 
                "properties": {"name": "4326"}
                }, 
            "type": "Feature", 
            "properties": {"name": "test"}
            }, 
        "outputs": [
            {
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "constraint": { }, 
            "name": "Time", 
            "uom": "", 
            "description": ""
            }, 
            {
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:test", 
            "constraint": { }, 
            "name": "test", 
            "uom": "test", 
            "description": ""
            }
        ], 
        "system_id": "test", 
        "history": []
        }
    address = 'http://localhost/istsos/wa/istsos/services/test/offerings/temporary/procedures'
    res = tpost.POST("",tproc,address)
    if not res['success']:
        print res
        raise SystemError("Unable to create a new SOS procedure: %s" % res['message'])
    
    #=======================================================================
    # TEST RESTFUL SERVICE REQUESTS
    #=======================================================================    
    dataqualities = data.test_dataqualities(f, verb)
    epsgs = eps.test_epsgs(f, verb)
    observedproperties = obsprop.test_observedproperties(f, verb)
    offerings = offer.test_offerings(f, verb)
    operations = oper.test_operations(f, verb)
    procedures = proc.test_procedures(f, verb)
    services = ser.test_services(f, verb)
    systemtypes = syst.test_systemtypes(f, verb)
    uoms = uom.test_uoms(f, verb)
    configsections = conf.test_configsections(f, verb)

    
    #=======================================================================
    # TEST SOS SERVICE REQUESTS
    #=======================================================================    
    if verb: print '\n-----------------getCapabilities----------------------------\n'
    getCapabilities = sos.getCapabilities(f, verb)
    if verb: print '\n-----------------describeSensor-----------------------------\n'
    describeSensor = sos.describeSensor(f, verb)
    if verb: print '\n-----------------getObservation-----------------------------\n'
    getObservation = sos.getObservation(f, verb)
    if verb: print '\n-----------------registerSensor-----------------------------\n'
    registerSensor = sos.registerSensor(f, verb)
    if verb: print '\n-----------------insertObservation--------------------------\n'
    insertObservation = sos.insertObservation(f, verb)
    if verb: print '\n-----------------getFeatureOfInterest-----------------------\n'
    featureofInterest = sos.getFeatureOfInterest(f, verb)
    
    f.close()
    
    if verb: 
        print '\n#############################################################'
        print '------------------------Failed tests:------------------------'
        print '#############################################################'
    
        print '\nConfigsections:'
        for el in configsections:
            if not configsections[el]:
                print el

        print '\nDataqualities:'
        for el in dataqualities:
            if not dataqualities[el]:
                print el
        
        print '\nEpsgs:'
        for el in epsgs:
            if not epsgs[el]:
                print el
          
        print '\nObservedproperties:'
        for el in observedproperties:
            if not observedproperties[el]:
                print el
            
        print '\nOfferings:'
        for el in offerings:
            if not offerings[el]:
                print el
            
        print '\nOperations:'
        for el in operations:
            if not operations[el]:
                print el
            
        print '\nProcedures:'
        for el in procedures:
            if not procedures[el]:
                print el
            
        print '\nServices:'
        for el in services:
            if not services[el]:
                print el
          
        print '\nSystemtypes:'
        print 'services/name/systemtypes non é implementato'
 
        """        
        for el in systemtypes:
            if not systemtypes[el]:
            print el
        """    

        print '\nUoms:'
        for el in uoms:
            if not uoms[el]:
                print el
    
        print '\ngetCapabilities:'
        for el in getCapabilities:
            if not getCapabilities[el]:
                print el
    
        print '\ndescribeSensor:'
        for el in describeSensor:
            if not describeSensor[el]:
                print el
    
        print '\ngetObservation:'
        for el in getObservation:
            if not getObservation[el]:
                print el
    
        print '\nregisterSensor:'
        for el in registerSensor:
            if not registerSensor[el]:
                print el
    
        print '\ninsertObservation:'
        for el in insertObservation:
            if not insertObservation[el]:
                print el
    
        print '\ngetFeatureOfInterest:'
        for el in featureofInterest:
            if not featureofInterest[el]:
                print el
        


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Import data from a csv file.')
    """
    conn = [user,password,host,dbname]
    """    
    parser.add_argument('user', action = 'store', help   = 'PostGIS user')
    parser.add_argument('password', action = 'store', help   = 'PostGIS password')
    parser.add_argument('host', action = 'store', help   = 'PostGIS host address')
    parser.add_argument('dbname', action = 'store', help   = 'PostGIS database name')
    parser.add_argument('-p', action = 'store', default = '5432', dest   = 'port', help   = 'PostGIS connection port')
    parser.add_argument('-v','--verbose', action = 'store_true', dest   = 'v', help   = 'Activate verbose debug')
    args = parser.parse_args()
    #print args.__dict__
    #exit()
    run_tests(args.__dict__)