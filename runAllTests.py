# -*- coding: utf-8 -*-
import sys
import time
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

    ntests = 0
    passed = []
    failed = []
    start_time = time.time()
    
    f = open(path.abspath(path.dirname(__file__))+'/logs/test.log', 'w')
        
    v = arg['v']

    ms = 'UNIT TESTING'   
    print ms
    f.write('\n'+ms+'\n=================================')
    
    ms = 'CREATING TESTING ENVIRONMENT'   
    if v: print '|---' + ms
    f.write('\n'+ms+'\n=================================')
    
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
    ms = 'server configuration set'
    if v: print '\t|---' + ms
    f.write('\n'+ms)
    
    #----- CREATE A SOS SERVICE ---------
    service = {
        "service": "test"
    }
    address = 'http://localhost/istsos/wa/istsos/services'
    res = tpost.POST("",service,address)
    if not res['success']:
        if res['message'].find("already exists"):
            deladdress = 'http://localhost/istsos/wa/istsos/services/test'
            delres = tdelete.DELETE("",deladdress)
            if delres['success']:
                res = tpost.POST("",service,address)
                if not res['success']:
                    raise SystemError("Unable to create a new SOS service: %s" % res['message'])
            else:
                raise SystemError("Unable to delete existing test SOS service: %s" % res['message'])
        else:
            raise SystemError("Unable to create a new SOS service: %s" % res['message'])
    ms = 'service test created'
    if v: print '\t|---' + ms
    f.write('\n'+ms)
    #----- ADD UNIT OF MEASURE ------
    tuom = {
        "name": "test", 
        "description": "test unit of measure"
        }
    address = 'http://localhost/istsos/wa/istsos/services/test/uoms'
    res = tpost.POST("",tuom,address)
    if not res['success']:
        raise SystemError("Unable to create a new SOS unit of measure: %s" % res['message'])
    ms = 'unit of measure test created'
    if v: print '\t|---' + ms
    f.write('\n'+ms)
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
    ms = 'observed property test created'
    if v: print '\t|---' + ms
    f.write('\n'+ms)
    #----- ADD PROCEDURE ------
    tproc = {
        'capabilities': [],
        'characteristics': '',
        'classification': [
            {'definition': 'urn:ogc:def:classifier:x-istsos:1.0:systemType',
             'name': 'System Type',
             'value': 'insitu-fixed-point'},
            {'definition': 'urn:ogc:def:classifier:x-istsos:1.0:sensorType',
             'name': 'Sensor Type',
             'value': 'test_type'}],
        'contacts': [],
        'description': 'test procedure',
        'documentation': [],
        'history': [],
        'identification': [],
        'inputs': [],
        'interfaces': '',
        'keywords': 'A,B,C',
        'location': 
            {'crs': 
                {'properties': 
                    {'name': '4326'}, 
                'type': 'name'},
            'geometry': 
                {'coordinates': ['1', '1', '1'], 
                'type': 'Point'},
            'properties': 
                {'name': 'test'},
            'type': 'Feature'},
         'outputs': [
             {'constraint': 
                 {'interval': None, 'role': None},
              'definition': 'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601',
              'description': '',
              'name': 'Time',
              'uom': 'iso8601'},
             {'constraint': {'min': '0',
              'role': 'urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0'},
               'definition': 'urn:ogc:def:parameter:x-istsos:1.0:test',
               'description': 'test opr',
               'name': 'test',
               'uom': 'test'}],
         'system': 'test',
         'system_id': 'test'}
    address = 'http://localhost/istsos/wa/istsos/services/test/procedures'
    res = tpost.POST("",tproc,address)
    if not res['success']:
        print res
        raise SystemError("Unable to create a new SOS procedure: %s" % res['message'])
    ms = 'procedure test created'
    if v: print '\t|---' + ms
    f.write('\n'+ms)
    
    #=======================================================================
    # TEST RESTFUL SERVICE REQUESTS
    #=======================================================================
    ms = 'TESTING RESTFUL SERVICE REQUESTS\n'   
    if v: print '|---' + ms
    f.write('\n'+ms+'\n=================================')   
    
    if v: print '\t|---TESTING dataqualities \n'
    dataqualities = data.test_dataqualities(f, v)
    if v:
        for el in dataqualities: print '\t\t|---' + el
    for k,v in dataqualities.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING epsg\n'
    epsgs = eps.test_epsgs(f, v)
    if v:
        for el in epsgs: print '\t\t|---' + el
    for k,v in epsgs.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING observedproperties \n'
    observedproperties = obsprop.test_observedproperties(f, v)
    if v:
        for el in observedproperties: print '\t\t|---' + el
    for k,v in observedproperties.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING offerings \n'
    offerings = offer.test_offerings(f, v)
    if v:
        for el in observedproperties: print '\t\t|---' + el
    for k,v in offerings.items():
        passed.append(el) if v else failed.append(el)
         
    if v: print '\t|---TESTING operations \n'
    operations = oper.test_operations(f, v)
    if v:
        for el in operations: print '\t\t|---' + el
    for k,v in operations.items():
        passed.append(el) if v else failed.append(el)
           
    if v: print '\t|---TESTING procedures \n'
    procedures = proc.test_procedures(f, v)
    if v:
        for el in procedures: print '\t\t|---' + el
    for k,v in procedures.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING services \n'
    services = ser.test_services(f, v)
    if v:
        for el in services: print '\t\t|---' + el
    for k,v in services.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING systemtypes \n'
    systemtypes = syst.test_systemtypes(f, v)
    if v:
        for el in systemtypes: print '\t\t|---' + el
    for k,v in systemtypes.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING uoms \n'
    uoms = uom.test_uoms(f, v)
    if v:
        for el in uoms: print '\t\t|---' + el
    for k,v in uoms.items():
        passed.append(el) if v else failed.append(el)
           
    if v: print '\t|---TESTING configsections \n'
    configsections = conf.test_configsections(f, v)
    if v:
        for el in configsections: print '\t\t|---' + el
    for k,v in configsections.items():
        passed.append(el) if v else failed.append(el)
      
    #=======================================================================
    # TEST SOS SERVICE REQUESTS
    #=======================================================================    
    ms = 'TESTING SOS SERVICE REQUESTS\n'   
    if v: print '|---' + ms
    f.write('\n'+ms+'\n=================================')   
    
    if v: print '\t|---TESTING getCapabilities \n'
    getCapabilities = sos.getCapabilities(f, v)
    if v:
        for el in getCapabilities: 
            print '\t\t|---' + el
    for k,v in getCapabilities.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING registerSensor \n'
    registerSensor = sos.registerSensor(f, v)
    if v:
        for el in registerSensor: 
            print '\t\t|---' + el
    for k,v in registerSensor.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING describeSensor \n'
    describeSensor = sos.describeSensor(f, v)
    if v:
        for el in describeSensor: 
            print '\t\t|---' + el
    for k,v in describeSensor.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING getFeatureOfInterest \n'
    featureofInterest = sos.getFeatureOfInterest(f, v)
    if v:
        for el in featureofInterest: 
            print '\t\t|---' + el
    for k,v in featureofInterest.items():
        passed.append(el) if v else failed.append(el)
           
    if v: print '\t|---TESTING insertObservation \n'
    insertObservation = sos.insertObservation(f, v)
    if v:
        for el in insertObservation: 
            print '\t\t|---' + el
    for k,v in insertObservation.items():
        passed.append(el) if v else failed.append(el)
            
    if v: print '\t|---TESTING getObservation \n'
    getObservation = sos.getObservation(f, v)
    if v:
        for el in getObservation: 
            print '\t\t|---' + el
    for k,v in getObservation.items():
        passed.append(el) if v else failed.append(el)
            
    # delete sensor
    f.close()
    
    duration = ('%s seconds') %(time.time() - start_time)
    npassed = len(passed)
    nfailed = len(failed)
    #calculate results statistics
    
    #=========================================================    
    # WRITE TEST RESULTS    
    #=========================================================
    print "results:"
    print "--test duration: %s" % duration
    print "--run tests:     %s" % npassed
    print "--passed tests:  %s" % nfailed
    print "--failed tests:  %s" % (npassed+nfailed)
    if len(failed) >0:    
        print ""
        print "failed test list: %s" %("\n -".join(failed))
    
    """
    --Run Summary: 
                Type      Total     Ran  Passed  Failed
               suites       17      17     n/a       0
               tests       143     143     143       0
               asserts    1228    1228    1228       0    
    """
    
    if v: 
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