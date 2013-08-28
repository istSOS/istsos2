# -*- coding: utf-8 -*-

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)
import pprint
import time

def deldic(d, k):
    c = d.copy()
    for el in k:
        if type(el) == list:
            del c[el[0]][el[1]]
        else:
            del c[el]
    return c

def test_configsections(doc):
    #services_name_configsections_GET(sname)
    #services_name_configsections_PUT(sname, put)
    #services_name_configsections_DELETE(sname)
    #services_name_configsections_getobservation_GET(sname)
    #services_name_configsections_getobservation_PUT(sname, putob)
    #services_name_configsections_getobservation_DELETE(sname)
    #services_name_configsections_identification_GET(sname)
    #services_name_configsections_identification_PUT(sname, putid)
    #services_name_configsections_identification_DELETE(sname)
    #services_name_configsections_geo_GET(sname)
    #services_name_configsections_geo_PUT(sname, putgeo)
    #services_name_configsections_geo_DELETE(sname)
    #services_name_configsections_connection_GET(sname)
    #services_name_configsections_connection_PUT(sname, putcon)
    #services_name_configsections_connection_operations_validatedb_GET(sname)
    #services_name_configsections_serviceurl_GET(sname)
    #services_name_configsections_serviceurl_PUT(sname, putsrv)
    #services_name_configsections_serviceurl_DELETE(sname)
    #services_name_configsections_provider_GET(sname)
    #services_name_configsections_provider_PUT(sname, putpro)
    #services_name_configsections_provider_DELETE(sname)
    
    doc.write('\n\n-----------------CONFIGSECTIONS---------------------')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
        
    put = {
        "getobservation": {
            #"default": True, 
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
            #"default": True, 
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
            #"default": True, 
            "dbname": "istsos", 
            "host": "localhost", 
            "user": "postgres", 
            "password": "postgres", 
            "port": "5432"
            }, 
        "identification": {
            "title": "IST Sensor Observation Service 1", 
            #"default": False, 
            "abstract": "hydro-meteorological monitoring network", 
            "urnversion": "1.0", 
            "authority": "x-istsos", 
            "fees": "NONE", 
            "keywords": "SOS,IST,SUPSI", 
            "accessconstrains": "NONE"
            }, 
        "serviceurl": {
            #"default": True, 
            "url": "http://localhost/istsos/test"
            }, 
        "provider": {
            "contactcountry": "Switzerland", 
            "providername": "Istituto Scienze della Terra", 
            #"default": True, 
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
            #"default": True, 
            "xaxisname": "easting", 
            "yaxisname": "northing", 
            "allowedepsg": "4326,3857", 
            "istsosepsg": "21781"
            }
        }     
        
    putob = {
        #"default": False, 
        "maxgoperiod": "600", 
        "aggregatenodataqi": "-100", 
        "defaultqi": "100", 
        "aggregatenodata": "-999.9",
        "correct_qi" : "110",
        "stat_qi" : "200",
        "transactional_log": "'True"
        }
        
    putid = {
        "title": "IST Sensor Observation Service 1", 
        #"default": False, 
        "abstract": "hydro-meteorological monitoring network", 
        "urnversion": "1.0", 
        "authority": "x-istsos", 
        "fees": "YUP, sure", 
        "keywords": "SOS,IST,SUPSI, test", 
        "accessconstrains": "NONE"}
        
    putgeo = {
        "zaxisname": "altitude", 
        #"default": False, 
        "xaxisname": "easting", 
        "yaxisname": "northing_u", 
        "allowedepsg": "4326,3857", 
        "istsosepsg": "21781"
        }
        
    putcon = {
        #"default": False, 
        "dbname": "istsos", 
        "host": "localhost", 
        "user": "postgres", 
        "password": "postgres", 
        "port": "5432"
        }
        
    putsrv = {
        #"default": True, 
        "url": "http://localhost/istsos/test"
        }
    
    putpro = {
        "contactcountry": "SwitzerlandCH", 
        "providername": "South Hampton Institute of Technology", 
        #"default": False, 
        "contactposition": "Data manager", 
        "contactvoice": "+41586666200", 
        "contactadminarea": "Canton Ticino", 
        "contactemail": "geoservice@supsi.ch", 
        "contactdeliverypoint": "Campus Trevano", 
        "contactname": "Team Geomatica", 
        "contactpostalcode": "6952", 
        "contactcity": "Canobbio", 
        "providersite": "http://www.supsi.ch/ist", 
        "contactfax": "+41586666209"
        }
        
    success_get = False
    success_put = False
    success_del = False
    success_getob = False
    success_putob = False
    success_delob = False
    success_getid = False
    success_putid = False
    success_delid = False
    success_getgeo = False
    success_putgeo = False
    success_delgeo = False
    success_getcon = False
    success_putcon = False
    success_getconop = False
    success_getsrv = False
    success_putsrv = False
    success_delsrv = False
    success_getpro = False
    success_putpro = False
    success_delpro = False
    
    get1 = tget.services_name_configsections_GET(sname)
    time.sleep(1)
    get2 = tget.services_name_configsections_GET(sname)
    put1 = tput.services_name_configsections_PUT(sname, put)
    get3 = tget.services_name_configsections_GET(sname)
    delete1 = tdelete.services_name_configsections_DELETE(sname)
    get4 = tget.services_name_configsections_GET(sname)
    
    getob1 = tget.services_name_configsections_getobservation_GET(sname)
    time.sleep(1)
    getob2 = tget.services_name_configsections_getobservation_GET(sname)
    putob1 = tput.services_name_configsections_getobservation_PUT(sname, putob)
    getob3 = tget.services_name_configsections_getobservation_GET(sname)
    deleteob1 = tdelete.services_name_configsections_getobservation_DELETE(sname)
    getob4 = tget.services_name_configsections_getobservation_GET(sname)
    
    getid1 = tget.services_name_configsections_identification_GET(sname)
    time.sleep(1)
    getid2 = tget.services_name_configsections_identification_GET(sname)
    putid1 = tput.services_name_configsections_identification_PUT(sname, putid)
    getid3 = tget.services_name_configsections_identification_GET(sname)
    deleteid1 = tdelete.services_name_configsections_identification_DELETE(sname)
    getid4 = tget.services_name_configsections_identification_GET(sname)
    
    getgeo1 = tget.services_name_configsections_geo_GET(sname)
    time.sleep(1)
    getgeo2 = tget.services_name_configsections_geo_GET(sname)
    putgeo1 = tput.services_name_configsections_geo_PUT(sname, putgeo)
    getgeo3 = tget.services_name_configsections_geo_GET(sname)
    deletegeo1 = tdelete.services_name_configsections_geo_DELETE(sname)
    getgeo4 = tget.services_name_configsections_geo_GET(sname)
    
    getcon1 = tget.services_name_configsections_connection_GET(sname)
    time.sleep(1)
    getcon2 = tget.services_name_configsections_connection_GET(sname)
    putcon1 = tput.services_name_configsections_connection_PUT(sname, putcon)
    getcon3 = tget.services_name_configsections_connection_GET(sname)
    
    getcon4 = tget.services_name_configsections_connection_operations_validatedb_GET(sname)
    time.sleep(1)
    getcon5 = tget.services_name_configsections_connection_operations_validatedb_GET(sname)
    
    getpro1 = tget.services_name_configsections_provider_GET(sname)
    time.sleep(1)
    getpro2 = tget.services_name_configsections_provider_GET(sname)
    putpro1 = tput.services_name_configsections_provider_PUT(sname, putpro)
    getpro3 = tget.services_name_configsections_provider_GET(sname)
    deletepro1 = tdelete.services_name_configsections_provider_DELETE(sname)
    getpro4 = tget.services_name_configsections_provider_GET(sname)
    
    getsrv1 = tget.services_name_configsections_serviceurl_GET(sname)
    time.sleep(1)
    getsrv2 = tget.services_name_configsections_serviceurl_GET(sname)
    putsrv1 = tput.services_name_configsections_serviceurl_PUT(sname, putsrv)
    getsrv3 = tget.services_name_configsections_serviceurl_GET(sname)
    deletesrv1 = tdelete.services_name_configsections_serviceurl_DELETE(sname)
    getsrv4 = tget.services_name_configsections_serviceurl_GET(sname)
    
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #configsections
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            doc.write('services_name_configsections_GET: SUCCESS')
            success_get = True
        else:
            doc.write('services_name_configsections_GET: FAILED')
            doc.write('\n\nservices_name_configsections_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
    else:
        doc.write('services_name_configsections_GET: FAILED')
        doc.write('\n\nservices_name_configsections_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get2))
        
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            doc.write('services_name_configsections_PUT: FAILED')
            doc.write('\n\nservices_name_configsections_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(put1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            temp = deldic(get3['data'], [['getobservation','default'],['urn','default'],['connection','default'],['identification','default'],['serviceurl','default'],['provider','default'],['geo','default']])
            if (temp['getobservation'] == put['getobservation'] 
                and temp['urn'] == put['urn'] 
                and temp['connection'] == put['connection'] 
                and temp['identification'] == put['identification'] 
                and temp['serviceurl'] == put['serviceurl'] 
                and temp['provider'] == put['provider'] 
                and temp['geo'] == put['geo']
                ):
                doc.write('services_name_configsections_PUT: SUCCESS')
                success_put = True
            else:
                doc.write('services_name_configsections_PUT: FAILED')
                doc.write('\n\nservices_name_configsections_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_PUT: FAILED')
        doc.write('\n\nservices_name_configsections_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(put1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get3))
        
            
            
            
    #Checks for the DELETE to be successful by comparing two GETs
    if delete1['success']:
        #If gets before and after are the same, failure
        if get3 == get4:
            doc.write('services_name_configsections_DELETE: FAILED')
            doc.write('\n\nservices_name_configsections_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(delete1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get4))
        #For the success, second get should be void
        else:
            if get4['total'] == get3['total'] - 1:
                #print 'the delete is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_DELETE: SUCCESS')
                success_del = True
            else:
                doc.write('services_name_configsections_DELETE: FAILED')
                doc.write('\n\nservices_name_configsections_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get4))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_DELETE: FAILED')
        doc.write('\n\nservices_name_configsections_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(delete1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get4))
        
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #observations
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if getob1['success'] and getob2['success']:
        if getob1 == getob2:
            doc.write('services_name_configsections_getobservation_GET: SUCCESS')
            success_getob = True
        else:
            doc.write('services_name_configsections_getobservation_GET: FAILED')
            doc.write('\n\nservices_name_configsections_getobservation_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getob1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getob2))
    else:
        doc.write('services_name_configsections_getobservation_GET: FAILED')
        doc.write('\n\nservices_name_configsections_getobservation_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getob1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getob2))
        
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if putob1['success']:
        #If gets before and after are the same, failure
        if getob2 == getob3:
            doc.write('services_name_configsections_getobservation_PUTT: FAILED')
            doc.write('\n\nservices_name_configsections_getobservation_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(putob1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getob2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getob3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (getob3['data']['maxgoperiod'] == putob['maxgoperiod']
                #and getob3['data']['default'] == putob['default']
                and getob3['data']['aggregatenodataqi'] == putob['aggregatenodataqi'] 
                and getob3['data']['defaultqi'] == putob['defaultqi'] 
                and getob3['data']['aggregatenodata'] == putob['aggregatenodata']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_getobservation_PUTT: SUCCESS')
                success_putob = True
            else:
                doc.write('services_name_configsections_getobservation_PUTT: FAILED')
                doc.write('\n\nservices_name_configsections_getobservation_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(putob1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getob2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getob3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_getobservation_PUTT: FAILED')
        doc.write('\n\nservices_name_configsections_getobservation_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(putob1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getob2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getob3))
        
            
            
            
    #Checks for the DELETE to be successful by comparing two GETs
    if deleteob1['success']:
        #If gets before and after are the same, failure
        if getob3 == getob4:
            doc.write('services_name_configsections_getobservations_DELETE: FAILED')
            doc.write('\n\nservices_name_configsections_getobservations_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(deleteob1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getob3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getob4))
        #For the success, second get should be void
        else:
            if getob4['total'] <= getob3['total'] and getob4['data']['default']:
                doc.write('services_name_configsections_getobservations_DELETE: SUCCESS')
                success_delob = True
            else:
                doc.write('services_name_configsections_getobservations_DELETE: FAILED')
                doc.write('\n\nservices_name_configsections_getobservations_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(deleteob1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getob3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getob4))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_getobservations_DELETE: FAILED')
        doc.write('\n\nservices_name_configsections_getobservations_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(deleteob1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getob3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getob4))
        
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #identification
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if getid1['success'] and getid2['success']:
        if getid1 == getid2:
            doc.write('services_name_configsections_identificaiton_GET: SUCCESS')
            success_getid = True
        else:
            doc.write('services_name_configsections_identificaiton_GET: FAILED')
            doc.write('\n\nservices_name_configsections_identificaiton_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getid1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getid2))
    else:
        doc.write('services_name_configsections_identificaiton_GET: FAILED')
        doc.write('\n\nservices_name_configsections_identification_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getid1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getid2))
        
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if putid1['success']:
        #If gets before and after are the same, failure
        if getid2 == getid3:
            doc.write('services_name_configsections_identification_PUT: FAILED')
            doc.write('\n\nservices_name_configsections_identification_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(putid1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getid2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getid3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (getid3['data']['title'] == putid['title'] 
                #and getid3['data']['default'] == putid['default'] 
                and getid3['data']['abstract'] == putid['abstract'] 
                and getid3['data']['urnversion'] == putid['urnversion'] 
                and getid3['data']['authority'] == putid['authority'] 
                and getid3['data']['fees'] == putid['fees'] 
                and getid3['data']['keywords'] == putid['keywords'] 
                and getid3['data']['accessconstrains'] == putid['accessconstrains']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_identification_PUT: SUCCESS')
                success_putid = True
            else:
                doc.write('services_name_configsections_identification_PUT: FAILED')
                doc.write('\n\nservices_name_configsections_identification_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(putid1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getid2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getid3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_identification_PUT: FAILED')
        doc.write('\n\nservices_name_configsections_identification_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(putid1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getid2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getid3))
            
    #Checks for the DELETE to be successful by comparing two GETs
    if deleteid1['success']:
        #If gets before and after are the same, failure
        if getid3 == getid4:
            doc.write('services_name_configsections_identification_DELETE: FAILED')
            doc.write('\n\nservices_name_configsections_identification_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(deleteid1))     
            doc.write('\nGet, before:\idn')
            doc.write(pp.pformat(get3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getid4))
        #For the success, second get should be void
        else:
            if getid4['total'] <= getid3['total'] and getid4['data']['default']:
                doc.write('services_name_configsections_identification_DELETE: SUCCESS')
                success_delid = True
            else:
                doc.write('services_name_configsections_identification_DELETE: FAILED')
                doc.write('\n\nservices_name_configsections_identification_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(deleteid1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getid3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getid4))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_identification_DELETE: FAILED')
        doc.write('\n\nservices_name_configsections_identification_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(deleteid1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getid3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getid4))
        
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #geo
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if getgeo1['success'] and getgeo2['success']:
        if getgeo1 == getgeo2:
            doc.write('services_name_configsections_geo_GET: SUCCESS')
            success_getgeo = True
        else:
            doc.write('services_name_configsections_geo_GET: FAILED')
            doc.write('\n\nservices_name_configsections_geo_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getgeo1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getgeo2))
    else:
        doc.write('services_name_configsections_geo_GET: FAILED')
        doc.write('\n\nservices_name_configsections_geo_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getgeo1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getgeo2))
        
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if putgeo1['success']:
        #If gets before and after are the same, failure
        if getgeo2 == getgeo3:
            doc.write('services_name_configsections_geo_PUT: FAILED')
            doc.write('\n\nservices_name_configsections_geo_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(putgeo1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getgeo2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getgeo3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (getgeo3['data']['zaxisname'] == putgeo['zaxisname'] 
                #and getgeo3['data']['default'] == putgeo['default'] 
                and getgeo3['data']['xaxisname'] == putgeo['xaxisname'] 
                and getgeo3['data']['yaxisname'] == putgeo['yaxisname'] 
                and getgeo3['data']['allowedepsg'] == putgeo['allowedepsg'] 
                and getgeo3['data']['istsosepsg'] == putgeo['istsosepsg']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_geo_PUT: SUCCESS')
                success_putgeo = True
            else:
                doc.write('services_name_configsections_geo_PUT: FAILED')
                doc.write('\n\nservices_name_configsections_geo_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(putgeo1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getgeo2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getgeo3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_geo_PUT: FAILED')
        doc.write('\n\nservices_name_configsections_geo_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(putgeo1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getgeo2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getgeo3))
             
            
    #Checks for the DELETE to be successful by comparing two GETs
    if deletegeo1['success']:
        #If gets before and after are the same, failure
        if getgeo3 == getgeo4:
            doc.write('services_name_configsections_geo_DELETE: FAILED')
            doc.write('\n\nservices_name_configsections_geo_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(deletegeo1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getgeo3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getgeo4))
        #For the success, second get should be void
        else:
            if getgeo4['total'] <= getgeo3['total'] and getgeo4['data']['default']:
                doc.write('services_name_configsections_geo_DELETE: SUCCESS')
                success_delgeo = True
            else:
                doc.write('services_name_configsections_geo_DELETE: FAILED')
                doc.write('\n\nservices_name_configsections_geo_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(deletegeo1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getgeo3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getgeo4))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_geo_DELETE: FAILED')
        doc.write('\n\nservices_name_configsections_geo_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(deletegeo1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getgeo3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getgeo4))
        
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #serviceurl
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if getsrv1['success'] and getsrv2['success']:
        if getsrv1 == getsrv2:
            doc.write('services_name_configsections_serviceurl_GET: SUCCESS')
            success_getsrv = True
        else:
            doc.write('services_name_configsections_serviceurl_GET: FAILED')
            doc.write('\n\nservices_name_configsections_serviceurl_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getsrv1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getsrv2))
    else:
        doc.write('services_name_configsections_serviceurl_GET: FAILED')
        doc.write('\n\nservices_name_configsections_serviceurl_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getsrv1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getsrv2))
        
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if putsrv1['success']:
        #If gets before and after are the same, failure
        if getsrv2 == getsrv3:
            doc.write('services_name_configsections_serviceurl_PUT: FAILED')
            doc.write('\n\nservices_name_configsections_serviceurl_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(putsrv1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getsrv2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getsrv3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (getsrv3['data']['url'] == putsrv['url']
                #and getsrv3['data']['default'] == putsrv['default']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_serviceurl_PUT: SUCCESS')
                success_putsrv = True
            else:
                doc.write('services_name_configsections_serviceurl_PUT: FAILED')
                doc.write('\n\nservices_name_configsections_serviceurl_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(putsrv1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getsrv2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getsrv3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_serviceurl_PUT: FAILED')
        doc.write('\n\nservices_name_configsections_serviceurl_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(putsrv1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getsrv2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getsrv3))
            
            
            
    #Checks for the DELETE to be successful by comparing two GETs
    if deletesrv1['success']:
        #If gets before and after are the same, failure
        if getsrv3 == getsrv4:
            doc.write('services_name_configsections_serviceurl_DELETE: FAILED')
            doc.write('\n\nservices_name_configsections_serviceurl_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(deletesrv1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getsrv3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getsrv4))
        #For the success, second get should be void
        else:
            if getsrv4['total'] <= getsrv3['total'] and getsrv4['data']['default']:
                doc.write('services_name_configsections_serviceurl_DELETE: SUCCESS')
                success_delsrv = True
            else:
                doc.write('services_name_configsections_serviceurl_DELETE: FAILED')
                doc.write('\n\nservices_name_configsections_serviceurl_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(deletesrv1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getsrv3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getsrv4))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_serviceurl_DELETE: FAILED')
        doc.write('\n\nservices_name_configsections_serviceurl_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(deletesrv1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getsrv3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getsrv4))
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #provider
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if getpro1['success'] and getpro2['success']:
        if getpro1 == getpro2:
            doc.write('services_name_configsections_provider_GET: SUCCESS')            
            success_getpro = True
        else:
            doc.write('services_name_configsections_provider_GET: FAILED')
            doc.write('\n\nservices_name_configsections_provider_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getpro1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getpro2))
    else:
        doc.write('services_name_configsections_provider_GET: FAILED')
        doc.write('\n\nservices_name_configsections_provider_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getpro1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getpro2))
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if putpro1['success']:
        #If gets before and after are the same, failure
        if getpro2 == getpro3:
            doc.write('services_name_configsections_provider_PUT: FAILED')
            doc.write('\n\nservices_name_configsections_provider_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(putpro1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getpro2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getpro3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (getpro3['data']['contactcountry'] == putpro['contactcountry'] 
                and getpro3['data']['providername'] == putpro['providername'] 
                and getpro3['data']['contactposition'] == putpro['contactposition'] 
                and getpro3['data']['contactvoice'] == putpro['contactvoice'] 
                and getpro3['data']['contactadminarea'] == putpro['contactadminarea'] 
                and getpro3['data']['contactemail'] == putpro['contactemail'] 
                and getpro3['data']['contactdeliverypoint'] == putpro['contactdeliverypoint'] 
                and getpro3['data']['contactname'] == putpro['contactname'] 
                and getpro3['data']['contactpostalcode'] == putpro['contactpostalcode'] 
                and getpro3['data']['contactcity'] == putpro['contactcity'] 
                and getpro3['data']['providersite'] == putpro['providersite'] 
                and getpro3['data']['contactfax'] == putpro['contactfax']
                #and getpro3['data']['default'] == putpro['default']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_provider_PUT: SUCCESS')
                success_putpro = True
            else:
                doc.write('services_name_configsections_provider_PUT: FAILED')
                doc.write('\n\nservices_name_configsections_provider_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(putpro1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getpro2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getpro3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_provider_PUT: FAILED')
        doc.write('\n\nservices_name_configsections_provider_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(putpro1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getpro2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getpro3))
            
    #Checks for the DELETE to be successful by comparing two GETs
    if deletepro1['success']:
        #If gets before and after are the same, failure
        if getpro3 == getpro4:
            doc.write('services_name_configsections_provider_DELETE: FAILED')
            doc.write('\n\nservices_name_configsections_provider_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(deletepro1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getpro3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getpro4))
        #For the success, second get should be void
        else:
            if getpro4['total'] <= getpro3['total'] and getpro4['data']['default']:
                #print 'the delete is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_provider_DELETE: SUCCESS')
                success_delpro = True
            else:
                doc.write('services_name_configsections_provider_DELETE: FAILED')
                doc.write('\n\nservices_name_configsections_provider_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(deletepro1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getpro3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getpro4))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_provider_DELETE: FAILED')
        doc.write('\n\nservices_name_configsections_provider_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(deletepro1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getpro3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getpro4))
            
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #connection
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    #Check for two successful requests to have the same result
    if getcon1['success'] and getcon2['success']:
        if getcon1 == getcon2:
            doc.write('services_name_configsections_connection_GET: SUCCESS')
            success_getcon = True
        else:
            doc.write('services_name_configsections_connection_GET: FAILED')
            doc.write('\n\nservices_name_configsections_connection_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getcon1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getcon2))
    else:
        doc.write('services_name_configsections_connection_GET: FAILED')
        doc.write('\n\nservices_name_configsections_connection_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getcon1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getcon2))
    
     
    #Checks for the PUT to be successful by comparing two GETs
    if putcon1['success']:
        #If gets before and after are the same, failure
        if getcon2 == getcon3:
            doc.write('services_name_configsections_connection_PUT: FAILED')
            doc.write('\n\nservices_name_configsections_connection_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(putcon1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(getcon2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(getcon3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (getcon3['data']['dbname'] == putcon['dbname'] 
                and getcon3['data']['host'] == putcon['host'] 
                and getcon3['data']['user'] == putcon['user'] 
                and getcon3['data']['password'] == putcon['password'] 
                and getcon3['data']['port'] == putcon['port']
                #and getcon3['data']['default'] == putcon['default']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_configsections_connection_PUT: SUCCESS')
                success_putcon = True
            else:
                doc.write('services_name_configsections_connection_PUT: FAILED')
                doc.write('\n\nservices_name_configsections_connection_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(putcon1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(getcon2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(getcon3))
    #If post not successful, failure
    else:
        doc.write('services_name_configsections_connection_PUT: FAILED')
        doc.write('\n\nservices_name_configsections_connection_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(putcon1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(getcon2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(getcon3))    
    
    #Check for two successful requests to have the same result
    if getcon4['success'] and getcon5['success']:
        if getcon4 == getcon5:
            doc.write('services_name_configsections_connection_operations_validatedb_GET: SUCCESS')
            success_getconop = True
        else:
            doc.write('services_name_configsections_connection_operations_validatedb_GET: FAILED')
            doc.write('\n\nservices_name_configsections_connection_operations_validatedb_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(getcon4))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(getcon5))
    else:
        doc.write('services_name_configsections_connection_operations_validatedb_GET: FAILED')
        doc.write('\n\nservices_name_configsections_connection_operations_validatedb_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(getcon4))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(getcon5))
    
    result = {
        'services_name_configsections_GET' : success_get,
        'services_name_configsections_PUT' : success_put,
        'services_name_configsections_DELETE' : success_del,
        'services_name_configsections_getobservation_GET' : success_getob,
        'services_name_configsections_getobservation_PUT' : success_putob,
        'services_name_configsections_getobservation_DELETE' : success_delob,
        'services_name_configsections_identification_GET' : success_getid,
        'services_name_configsections_identification_PUT' : success_putid,
        'services_name_configsections_identification_DELETE' : success_delid,
        'services_name_configsections_geo_GET' : success_getgeo,
        'services_name_configsections_geo_PUT' : success_putgeo,
        'services_name_configsections_geo_DELETE' : success_delgeo,
        'services_name_configsections_connection_GET' : success_getcon,
        'services_name_configsections_connection_PUT' : success_putcon,
        'services_name_configsections_connection_operations_validatedb_GET' : success_getconop,
        'services_name_configsections_serviceurl_GET' : success_getsrv,
        'services_name_configsections_serviceurl_PUT' : success_putsrv,
        'services_name_configsections_serviceurl_DELETE' : success_delsrv,
        'services_name_configsections_provider_GET' : success_getpro,
        'services_name_configsections_provider_PUT' : success_putpro,
        'services_name_configsections_provider_DELETE' : success_delpro,
        }
        
    return result