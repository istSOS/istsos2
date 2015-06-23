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

    
def test_services(doc):
    #services_GET()
    #services_POST(post)
    #services_name_GET(sname)
    #services_name_PUT(put, sname)
    #services_name_DELETE(sname_updated)
    #services_name_operations_insertobservation_POST(sname_insertob, post_observation)
    
    doc.write('\n-----------------SERVICES------------------------\n')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    sname_updated = 'prova_updated'
    sname_post = 'prova'
    sname_insertob = 'test'
    
    post = {
        "path": "/usr/local/istsos/services/prova/prova.cfg",
        "service": "prova"
    }
        
    put = {
        "service": "prova_updated", 
        "dbname": "istsos", 
        "host": "localhost", 
        "user": "postgres", 
        "password": "postgres", 
        "port": "5432"
    } 

      
    success_get1 = False
    success_post = False
    success_get2 = False
    success_put = False
    success_delete = False
    success_insertob = False
    
    get1 = tget.services_GET()
    time.sleep(1)
    get2 = tget.services_GET()    
    post1 = tpost.services_POST(post)
    get3 = tget.services_GET()
    
    get4 = tget.services_name_GET(sname)
    time.sleep(1)
    get5 = tget.services_name_GET(sname)
    put1 = tput.services_name_PUT(put, sname_post)
    get6 = tget.services_name_GET(sname_updated)
    delete1 = tdelete.services_name_DELETE(sname_updated)
    get7 = tget.services_name_GET(sname_updated)
    
    
    asi = tget.services_name_procedures_name_GET(sname, sname)['data']['assignedSensorId']
    post_observation = {
            "AssignedSensorId" : asi,
            "ForceInsert" : "true",
            "Observation" : {
                "procedure": "urn:ogc:object:procedure:x-istsos:1.01.0:test",
                "samplingTime": {
				    "beginPosition": "2012-01-01T13:00:00+01:00", 
				    "endPosition": "2012-01-01T17:00:00+01:00"
			    }, 
			    "observedProperty": {
				    "CompositePhenomenon": {
					    "id": "comp_126", 
					    "dimension": "2"
				    }, 
				    "component": [
					    "urn:ogc:def:parameter:x-istsos:1.01.0:time:iso8601", 
					    "urn:ogc:def:parameter:x-istsos:1.0:test"
				    ]
			    },
			    "featureOfInterest": {
				    "geom": "<gml:Point srsName='EPSG:4326'><gml:coordinates>15,15,15</gml:coordinates></gml:Point>", 
				    "name": "urn:ogc:object:feature:x-istsos:1.01.0:station:test"
			    }, 
			    "result": {
				    "DataArray": {
					    "elementCount": "2", 
					    "values": [
						    [
							    "2012-01-01T14:00:00+01:00", 
							    "10.000000"
						    ],
						    [
							    "2012-01-01T15:00:00+01:00", 
							    "20.000000"
						    ]
					    ], 
					    "field": [
						    {
							    "definition": "urn:ogc:def:parameter:x-istsos:1.01.0:time:iso8601", 
							    "name": "Time"
						    }, 
						    {
							    "definition": "urn:ogc:def:parameter:x-istsos:1.0:test", 
							    "name": "test", 
							    "uom": "test"
						    }
					    ]
				    }
			    }
		    } 
		}    
    
    post2 = tpost.services_name_operations_insertobservation_POST(sname_insertob, post_observation)
    
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            doc.write('services_GET: SUCCESS')
            success_get1 = True
        else:
            doc.write('services_GET: FAILED')
            doc.write('\n\nservices_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
    else:
        doc.write('services_GET: FAILED')
        doc.write('\n\nservices_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get2))
    
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            doc.write('services_POST: FAILED')
            doc.write('\n\nservices_POST: the data has not changed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #If second get has same or less entries than first, failure
        elif get3['total'] <= get2['total']:
            doc.write('services_POST: FAILED')
            doc.write('\n\nservices_POST: post failed or deleted another entry')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #If second get has one more entry than first, look for the 
        #inserted value. If found, success, else failure
        elif get3['total'] == get2['total'] + 1:
            for data in get3['data']:
                if (data['service'] == post['service']
                    #and data['path'] == post['path']
                    ):
                    doc.write('services_POST: SUCCESS')
                    success_post = True
                    break
            if not success_post:
                doc.write('services_POST: FAILED')
                doc.write('\n\nservices_POST: posted data does not correspond')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
        #if anything else wrong, failure
        else:
            doc.write('services_POST: FAILED')
            doc.write('\n\nservices_POST: something went wrong')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
    #If post not successful, failure
    else:
        doc.write('services_POST: FAILED')
        doc.write('\n\nservices_POST: post failed')
        doc.write('\nPost:\n')
        doc.write(pp.pformat(post1))
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get3))
            
    
    #Check for two successful requests to have the same result
    if get4['success'] and get5['success']:
        if get4 == get5:
            #doc.write('the results are the same:\n'
            #pp.pprint(get1)
            doc.write('services_name_GET: SUCCESS')
            success_get2 = True
        else:
            doc.write('services_name_GET: FAILED')
            doc.write('\n\nservices_name_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get4))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get5))
    else:
        doc.write('services_name_GET: FAILED')
        doc.write('\n\nservices_name_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get4))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get5))
    
    
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get5 == get6:
            doc.write('services_name_uoms_name_PUT: FAILED')
            doc.write('\n\nservices_name_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(put1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get5))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get6))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (get6['data']['service'] == put['service'] 
                and get6['data']['dbname'] == put['dbname']
                and get6['data']['host'] == put['host']
                and get6['data']['user'] == put['user']
                and get6['data']['password'] == put['password']
                and get6['data']['port'] == put['port']
                ):
                doc.write('services_name_PUT: SUCCESS')
                success_put = True
            else:
                doc.write('services_name_PUT: FAILED')
                doc.write('\n\nservices_name_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get5))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get6))
    #If post not successful, failure
    else:
        doc.write('services_name_PUT: FAILED')
        doc.write('\n\nservices_name_PUT: the request has not been successful')
        doc.write('\nPut:\n')            
        doc.write(pp.pformat(put1)) 
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get5))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get6))
            
            
            
    #Checks for the DELETE to be successful by comparing two GETs
    if delete1['success']:
        #If gets before and after are the same, failure
        if get6 == get7:
            doc.write('services_name_DELETE: FAILED')
            doc.write('\n\nservices_name_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(delete1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get6))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get7))
        #For the success, second get should be void
        else:
            if get7['success'] == False:
                #doc.write('the delete is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_DELETE: SUCCESS')
                success_delete = True
            else:
                doc.write('services_name_DELETE: FAILED')
                doc.write('\n\nservices_name_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get6))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get7))
    #If post not successful, failure
    else:
        doc.write('services_name_DELETE: FAILED')
        doc.write('\n\nservices_name_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(delete1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get6))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get7))
        
            
    #Checks for the POST to be successful by comparing two GETs
    if post2['success']:
        doc.write('services_name_operations_insertobservation_POST: SUCCESS')
        success_insertob = True
    else:
        doc.write('\n\nservices_name_operations_insertobservation_POST: post failed')
        doc.write('\nPost:\n')
        doc.write(pp.pformat(post2))
        doc.write('services_name_operations_insertobservation_POST: FAILED')
        
    
    result = {
        'services_GET' : success_get1,
        'services_POST' : success_post,
        'services_name_GET' : success_get2,
        'services_name_PUT' : success_put,
        'services_name_DELETE' : success_delete,
        'services_name_operations_insertobservation_POST' : success_insertob
        }
        
    return result
