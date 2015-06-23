#  -*- coding: utf-8 -*-
# istsos WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
#
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
    
def test_procedures(doc):
    #services_name_procedures_POST(sname, post)
    #services_name_procedures_name_GET(sname, pname)
    #services_name_procedures_name_PUT(sname, pname, put)
    #services_name_procedures_name_DELETE(sname, pname)
    #services_name_procedures_operations_getlist_GET(sname)
    #services_name_procedures_name_ratingcurve_GET(sname, pname)
    #services_name_procedures_name_ratingcurve_POST(sname, pname, post)
    
    doc.write('\n-----------------PROCEDURES----------------------\n')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    pname = 'test_post'
    prat = "Q_TICINO"
    
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
        
    post_rat = [ 
         {
          'A': '42',
          'B': '42',
          'C': '42',
          'K': '42',
          'from': '1982-01-01T00:00+00:00',
          'low_val': '0',
          'to': '1983-01-01T00:00+00:00',
          'up_val': '1000'
         }
        ]
        
    success_get1 = False
    success_post = False
    success_getlist = False
    success_put = False
    success_delete = False
    success_get2 = False
    success_postrat = False
    
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
    
    get7 = tget.services_name_procedures_name_ratingcurve_GET(sname, prat)
    time.sleep(1)
    get8 = tget.services_name_procedures_name_ratingcurve_GET(sname, prat)
    post2 = tpost.services_name_procedures_name_ratingcurve_POST(sname, prat, post_rat)
    get9 = tget.services_name_procedures_name_ratingcurve_GET(sname, prat)
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            doc.write('services_name_procedures_name_GET: SUCCESS')
            success_get1 = True
        else:
            doc.write('services_name_procedures_name_GET: FAILED')
            doc.write('\n\nservices_name_procedures_name_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))            
    else:
        doc.write('services_name_procedures_name_GET: FAILED')
        doc.write('\n\nservices_name_procedures_name_GET: the requests did not succeed')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get2))            
    
     
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
            doc.write('services_name_procedures_POST: SUCCESS')
            success_post = True
        #if anything else wrong, failure
        else:
            doc.write('services_name_procedures_POST: FAILED')
            doc.write('\n\nservices_name_procedures_POST: posted data does not correspond')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get1['data']))
    #If post not successful, failure
    else:
        doc.write('services_name_procedures_POST: FAILED')
        doc.write('\n\nservices_name_procedures_POST: post did not succeed')
        doc.write('\nPost:\n')
        doc.write(pp.pformat(post1))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get1))
            
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            doc.write('services_name_procedures_name_PUT: FAILED')
            doc.write('\n\nservices_name_procedures_name_PUT: data did not change')
            doc.write('\nPut:\n')
            doc.write(pp.pformat(put1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        
        else:
            
            print 'get3:\n'
            print pp.pformat(get3)
            print 'put, after:\n'
            print pp.pformat(put)
            
            temp = deldic(get3['data'], [['location', 'crs']])
            ptloc = deldic(put['location'], ['crs'])
            
            
            print '\ntemp:\n'
            print pp.pformat(temp)
            print '\nptloc, after:\n'
            print pp.pformat(ptloc)
            
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
                doc.write('services_name_procedures_name_PUT: SUCCESS')
                success_put = True
            else:
                doc.write('services_name_procedures_name_PUT: FAILED')
                doc.write('\n\nservices_name_procedures_name_PUT: data does not correspond')
                doc.write('\nPut:\n')
                doc.write(pp.pformat(put1))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
    #If post not successful, failure
    else:
        doc.write('services_name_procedures_name_PUT: FAILED')
        doc.write('\n\nservices_name_procedures_name_PUT: request did not succeed')
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
            doc.write('services_name_procedures_name_DELETE: FAILED')
            doc.write('\n\nservices_name_procedures_name_DELETE: data did not change')
            doc.write('\nDelete:\n')
            doc.write(pp.pformat(delete1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get3))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get4))
        #For the success, second get should be void
        else:
            if not get4['success']:
                #doc.write('the delete is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_procedures_name_DELETE: SUCCESS')
                success_delete = True
            else:
                doc.write('services_name_procedures_name_DELETE: FAILED')
                doc.write('\n\nservices_name_procedures_name_DELETE: data has not been deleted')
                doc.write('\nDelete:\n')
                doc.write(pp.pformat(delete1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get3))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get4))
    #If post not successful, failure
    else:
        doc.write('services_name_procedures_name_DELETE: FAILED')
        doc.write('\n\nservices_name_procedures_name_DELETE: request did not succeed')
        doc.write('\nDelete:\n')
        doc.write(pp.pformat(delete1))
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get3))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get4))
            
    
    
    #Check for two successful requests to have the same result
    if get5['success'] and get6['success']:
        if get5 == get6:
            doc.write('services_name_procedures_operations_getlist_GET: SUCCESS')
            success_getlist = True
        else:
            doc.write('services_name_procedures_operations_getlist_GET: FAILED')
            doc.write('\n\nservices_name_procedures_operations_getlist_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get5))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get6))            
    else:
        doc.write('services_name_procedures_operations_getlist_GET: FAILED')
        doc.write('\n\nservices_name_procedures_operations_getlist_GET: the requests did not succeed')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get5))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get6))            
        
        
        
    #Check for two successful requests to have the same result    
    if get7['success'] and get8['success']:
        if get7 == get8:
            doc.write('services_name_procedures_name_ratingcurve_GET: SUCCESS')
            success_get2 = True
        else:
            doc.write('services_name_procedures_name_ratingcurve_GET: FAILED')
            doc.write('\n\nservices_name_procedures_name_ratingcurve_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get7))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get8))            
    else:
        doc.write('services_name_procedures_name_ratingcurve_GET: FAILED')
        doc.write('\n\nservices_name_procedures_name_ratingcurve_GET: the requests did not succeed')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get7))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get8))
        
    
    
    #Checks for the POST to be successful by comparing two GETs
    if post2['success']:
        #If gets before and after are the same, failure
        if get8 == get9:
            doc.write('services_name_procedures_name_ratingcurve_POST: FAILED')
            doc.write('\n\nservices_name_procedures_name_ratingcurve_POST: the data has not changed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get8))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get9))
        #If second get has same or less entries than first, failure
        elif get9['total'] != len(post_rat):
            doc.write('services_name_procedures_name_ratingcurve_POST: FAILED')
            doc.write('\n\nservices_name_procedures_name_ratingcurve_POST: post does not have correct length')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post2))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get8))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get9))
        #If second get has one more entry than first, look for the 
        #inserted value. If found, success, else failure
        elif get9['total'] == len(post_rat):
            for data in get9['data']:
                temp = post_rat[0]
                if (data['A'] == temp['A'] 
                    and data['B'] == temp['B']
                    and data['C'] == temp['C']
                    and data['K'] == temp['K']
                    and data['from'] == temp['from']
                    and data['to'] == temp['to']
                    and data['up_val'] == temp['up_val']
                    and data['low_val'] == temp['low_val']
                    ):
                    doc.write('services_name_procedures_name_ratingcurve_POST: SUCCESS')
                    success_postrat = True
                    break
            if not success_postrat:
                doc.write('services_name_procedures_name_ratingcurve_POST: FAILED')
                doc.write('\n\nservices_name_procedures_name_ratingcurve_POST: posted data does not correspond')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post2))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get8))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get9))
        #if anything else wrong, failure
        else:
            doc.write('services_name_procedures_name_ratingcurve_POST: FAILED')
            doc.write('\n\nservices_name_procedures_name_ratingcurve_POST: something went wrong')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post2))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get8))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get9))
    #If post not successful, failure
    else:
        doc.write('services_name_procedures_name_ratingcurve_POST: FAILED')
        doc.write('\n\nservices_name_procedures_name_ratingcurve_POST: post failed')
        doc.write('\nPost:\n')
        doc.write(pp.pformat(post2))
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get8))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get9))
    
    
    
    result = {
        'services_name_procedures_name_GET' : success_get1,
        'services_name_procedures_POST' : success_post,
        'services_name_procedures_operations_getlist_GET' : success_getlist,
        'services_name_procedures_name_PUT' : success_put,
        'services_name_procedures_name_DELETE' : success_delete,
        'services_name_procedures_name_ratingcurve_GET' : success_get2,
        'services_name_procedures_name_ratingcurve_POST' : success_postrat
        }
        
    return result
