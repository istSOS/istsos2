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
    
def test_procedures(doc, v):
    #services_name_procedures_POST(sname, post)
    #services_name_procedures_name_GET(sname, pname)
    #services_name_procedures_name_PUT(sname, pname, put)
    #services_name_procedures_name_DELETE(sname, pname)
    #services_name_procedures_operations_getlist_GET(sname)
    
    print '\n-----------------PROCEDURES----------------------\n'
    
    if v:
        doc.write('\n\n-----------------PROCEDURES-------------------------')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    pname = 'test_post'
    
    post = {
        "inputs": [], 
        "description": "Weather in Usmate Carate", 
        "classification": [
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType", 
            "name": "System Type", 
            "value": "insitu-fixed-point"
            }, 
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType", 
            "name": "Sensor Type", 
            "value": "tipping bucket rain gauge"
            }
        ], 
        "characteristics": "", 
        "interfaces": "", 
        "keywords": "weather,meteorological,IST", 
        "contacts": [], 
        #"assignedSensorId": "6ecb65065eccaac8967089df62c81a24", 
        "documentation": [], 
        "system": "test_post", 
        "capabilities": [], 
        "identification": [], 
        "location": {
            "geometry": {
                "type": "Point", 
                "coordinates": ["8.96127", "46.02723", "344.1"]
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
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall", 
            "constraint": { }, 
            "name": "air-rainfall", 
            "uom": "mm", 
            "description": ""
            }
        ], 
        "system_id": "test_post", 
        "history": []
        }
        
    put = {
        "inputs": [], 
        "description": "updated description", 
        "classification": [
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType", 
            "name": "System Type", 
            "value": "insitu-fixed-point"
            }, 
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType", 
            "name": "Sensor Type", 
            "value": "tipping bucket rain gauge"
            }
        ], 
        "characteristics": "", 
        "interfaces": "", 
        "keywords": "weather,meteorological,IST,test_update", 
        "contacts": [], 
        #"assignedSensorId": "6ecb65065eccaac8967089df62c81a24", 
        "documentation": [], 
        "system": "test_post", 
        "capabilities": [], 
        "identification": [], 
        "location": {
            "geometry": {
                "type": "Point", 
                "coordinates": ["8.96127", "46.02723", "344.1"]
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
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall", 
            "constraint": { },
            "name": "air-rainfall", 
            "uom": "mm", 
            "description": ""
            }
        ], 
        "system_id": "test_post", 
        "history": []
        }        
        
    success_get1 = False
    success_post = False
    success_getlist = False
    success_put = False
    success_delete = False
    
    post1 = tpost.services_name_procedures_POST(sname, post)
    get1 = tget.services_name_procedures_name_GET(sname, pname)
    time.sleep(1)
    get2 = tget.services_name_procedures_name_GET(sname, pname)
    put1 = tput.services_name_procedures_name_PUT(sname, pname, put)
    get3 = tget.services_name_procedures_name_GET(sname, pname)
    delete1 = tdelete.services_name_procedures_name_DELETE(sname, pname)
    get4 = tget.services_name_procedures_name_GET(sname, pname)
    get5 = tget.services_name_procedures_operations_getlist_GET(sname)
    time.sleep(1)
    get6 = tget.services_name_procedures_operations_getlist_GET(sname)
    
    
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            print 'services_name_procedures_name_GET: SUCCESS'
            success_get1 = True
        else:
            if v:
                doc.write('\n\nservices_name_procedures_name_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get1))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get2))            
            print 'services_name_procedures_name_GETT: FAILED'
    else:
        if v:
            doc.write('\n\nservices_name_procedures_name_GET: the requests did not succeed')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))            
        print 'services_name_procedures_name_GET: FAILED'
    
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        temp = deldic(get1['data'], [['location', 'crs']])
        postloc = deldic(post['location'], ['crs'])
        if (get1['data']['description'] == post['description']
            and temp['inputs'] == post['inputs']
            and temp['classification'] == post['classification']
            and temp['characteristics'] == post['characteristics']
            and temp['interfaces'] == post['interfaces']
            and temp['keywords'] == post['keywords']
            and temp['contacts'] == post['contacts']
            #and temp['assignedSensorId'] == post['assignedSensorId']
            and temp['documentation'] == post['documentation']
            and temp['system'] == post['system']
            and temp['capabilities'] == post['capabilities']
            and temp['identification'] == post['identification']
            and temp['location'] == postloc
            and temp['outputs'] == post['outputs']
            and temp['system_id'] == post['system_id']
            and temp['history'] == post['history']
            ):
            print 'services_name_procedures_POST: SUCCESS'
            success_post = True
        #if anything else wrong, failure
        else:
            if v:
                doc.write('\n\nservices_name_procedures_POST: posted data does not correspond')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get1['data']))
            print 'services_name_procedures_POST: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\nservices_name_procedures_POST: post did not succeed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get1))
        print 'services_name_procedures_POST: FAILED'
            
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            if v:
                doc.write('\n\nservices_name_procedures_name_PUT: data did not change')
                doc.write('\nPut:\n')
                doc.write(pp.pformat(put1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
            print 'services_name_procedures_name_PUT: FAILED'
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            temp = deldic(get3['data'], [['location', 'crs']])
            putloc = deldic(put['location'], ['crs'])
            
            if (temp['description'] == put['description']
                and temp['inputs'] == put['inputs']
                and temp['classification'] == put['classification']
                and temp['characteristics'] == put['characteristics']
                and temp['interfaces'] == put['interfaces']
                and temp['keywords'] == put['keywords']
                and temp['contacts'] == put['contacts']
                #and temp['assignedSensorId'] == put['assignedSensorId']
                and temp['documentation'] == put['documentation']
                and temp['system'] == put['system']
                and temp['capabilities'] == put['capabilities']
                and temp['identification'] == put['identification']
                and temp['location'] == putloc
                and temp['outputs'] == put['outputs']
                and temp['system_id'] == put['system_id']
                and temp['history'] == put['history']
                ):
                print 'services_name_procedures_name_PUT: SUCCESS'
                success_put = True
            else:
                if v:   
                    doc.write('\n\nservices_name_procedures_name_PUT: data does not correspond')
                    doc.write('\nPut:\n')
                    doc.write(pp.pformat(put1))
                    doc.write('\nGet, after:\n')
                    doc.write(pp.pformat(get3))
                print 'services_name_procedures_name_PUT: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\nservices_name_procedures_name_PUT: request did not succeed')
            doc.write('\nPut:\n')
            doc.write(pp.pformat(put1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
            print 'services_name_procedures_name_PUT: FAILED'
            
            
            
    #Checks for the DELETE to be successful by comparing two GETs
    if delete1['success']:
        #If gets before and after are the same, failure
        if get3 == get4:
            if v:
                doc.write('\n\nservices_name_procedures_name_DELETE: data did not change')
                doc.write('\nDelete:\n')
                doc.write(pp.pformat(delete1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get4))
            print 'services_name_procedures_name_DELETE: FAILED'
        #For the success, second get should be void
        else:
            if not get4['success']:
                #print 'the delete is successful:\n'
                #pp.pprint(get6)
                print 'services_name_procedures_name_DELETE: SUCCESS'
                success_delete = True
            else:
                if v:
                    doc.write('\n\nservices_name_procedures_name_DELETE: data has not been deleted')
                    doc.write('\nDelete:\n')
                    doc.write(pp.pformat(delete1))
                    doc.write('\nGet, before:\n')
                    doc.write(pp.pformat(get3))
                    doc.write('\nGet, after:\n')
                    doc.write(pp.pformat(get4))
                print 'services_name_procedures_name_DELETE: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\nservices_name_procedures_name_DELETE: request did not succeed')
            doc.write('\nDelete:\n')
            doc.write(pp.pformat(delete1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get4))
        print 'services_name_procedures_name_DELETE: FAILED'
            
    
    
    #Check for two successful requests to have the same result
    if get5['success'] and get6['success']:
        if get5 == get6:
            print 'services_name_procedures_operations_getlist_GET: SUCCESS'
            success_getlist = True
        else:
            if v:
                doc.write('\n\nservices_name_procedures_operations_getlist_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get5))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get6))            
            print 'services_name_procedures_operations_getlist_GET: FAILED'
    else:
        if v:
            doc.write('\n\nservices_name_procedures_operations_getlist_GET: the requests did not succeed')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get5))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get6))            
        print 'services_name_procedures_operations_getlist_GET: FAILED'
        
    
    
    result = {
        'services_name_procedures_name_GET' : success_get1,
        'services_name_procedures_POST' : success_post,
        'services_name_procedures_operations_getlist_GET' : success_getlist,
        'services_name_procedures_name_PUT' : success_put,
        'services_name_procedures_name_DELETE' : success_delete
        }
        
    return result