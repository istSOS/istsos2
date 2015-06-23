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

    
def test_uoms(doc):
    #services_name_uoms_GET(sname)
    #services_name_uoms_POST(sname, post)    
    #services_name_uoms_name_GET(sname, uname)
    #services_name_uoms_name_PUT(sname, uname, put)
    #services_name_uoms_name_DELETE(sname, uname)
    
    doc.write('\n-----------------UOMS----------------------------\n')
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    uname = 'test'
    putname = 'test_post'
    
    post = {
        "procedures": [], 
        "name": "test_post", 
        "description": "lorem ipsum dolor"
        }
        
    put = {
        "procedures": [], 
        "name": "test_post", 
        "description": "modified input"
        }        
        
    success_get1 = False
    success_post = False
    success_get2 = False
    success_put = False
    success_delete = False
    
    get1 = tget.services_name_uoms_GET(sname)
    time.sleep(1)
    get2 = tget.services_name_uoms_GET(sname)
    post1 = tpost.services_name_uoms_POST(sname, post)
    get3 = tget.services_name_uoms_GET(sname)
    
    get4 = tget.services_name_uoms_name_GET(sname, putname)
    time.sleep(1)
    get5 = tget.services_name_uoms_name_GET(sname, putname)
    put1 = tput.services_name_uoms_name_PUT(sname, putname, put)
    get6 = tget.services_name_uoms_name_GET(sname, putname)    
    delete1 = tdelete.services_name_uoms_name_DELETE(sname, putname)
    get7 = tget.services_name_uoms_name_GET(sname, putname)
    get8 = tget.services_name_uoms_GET(sname)
    
    
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            doc.write('services_name_uoms_GET: SUCCESS')
            success_get1 = True
        else:
            doc.write('services_name_uoms_GET: FAILED')
            doc.write('\n\nservices_name_uoms_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
    else:
        doc.write('services_name_uoms_GET: FAILED')
        doc.write('\n\nservices_name_uoms_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get2))
    
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            doc.write('services_name_uoms_POST: FAILED')
            doc.write('\n\nservices_name_uoms_POST: the data has not changed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #If second get has same or less entries than first, failure
        elif get3['total'] <= get2['total']:
            doc.write('services_name_uoms_POST: FAILED')
            doc.write('\n\nservices_name_uoms_POST: post failed or deleted another entry')
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
                if (data['name'] == post['name']
                    and data['description'] == post['description']
                    and data['procedures'] == post['procedures']
                    ):
                    doc.write('services_name_uoms_POST: SUCCESS')
                    success_post = True
                    break
            if not success_post:
                doc.write('services_name_uoms_POST: FAILED')
                doc.write('\n\nservices_name_uoms_POST: posted data does not correspond')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
        #if anything else wrong, failure
        else:
            doc.write('services_name_uoms_POST: FAILED')
            doc.write('\n\nservices_name_uoms_POST: something went wrong')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
    #If post not successful, failure
    else:
        doc.write('services_name_uoms_POST: FAILED')
        doc.write('\n\nservices_name_uoms_POST: post failed')
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
            doc.write('services_name_uoms_name_GET: SUCCESS')
            success_get2 = True
        else:
            doc.write('services_name_uoms_name_GET: FAILED')
            doc.write('\n\nservices_name_uoms_name_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get4))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get5))
    else:
        doc.write('services_name_uoms_name_GET: FAILED')
        doc.write('\n\nservices_name_uoms_name_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get4))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get5))

    
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get5 == get6:
            doc.write('services_name_uoms_name_PUT: FAILED')
            doc.write('\n\nservices_name_uoms_name_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(put1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get5))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get6))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            for data in get6['data']:
                if (data['name'] == put['name'] 
                    and data['description'] == put['description']
                    #and get6['data'][0]['procedures'] == put['procedures']
                ):
                    doc.write('services_name_uoms_name_PUT: SUCCESS')
                    success_put = True
            if not success_put:
                doc.write('services_name_uoms_name_PUT: FAILED')
                doc.write('\n\nservices_name_uoms_name_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get5))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get6))
    #If post not successful, failure
    else:
        doc.write('services_name_uoms_name_PUT: FAILED')
        doc.write('\n\nservices_name_uoms_name_PUT: the request has not been successful')
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
            doc.write('services_name_uoms_name_DELETE: FAILED')
            doc.write('\n\nservices_name_uoms_name_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(delete1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get6))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get7))
        #For the success, second get should be void
        else:
            if get7['total'] == get6['total'] - 1 and get8 == get1:
                #doc.write('the delete is successful:\n'
                #pp.pprint(get6)
                doc.write('services_name_uoms_name_DELETE: SUCCESS')
                success_delete = True
            else:
                doc.write('services_name_uoms_name_DELETE: FAILED')
                doc.write('\n\nservices_name_uoms_name_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get6))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get7))
    #If post not successful, failure
    else:
        doc.write('services_name_uoms_name_DELETE: FAILED')
        doc.write('\n\nservices_name_uoms_name_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(delete1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get6))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get7))
            
            
    result = {
        'services_name_uoms_GET' : success_get1,
        'services_name_uoms_POST' : success_post,
        'services_name_uoms_name_GET' : success_get2,
        'services_name_uoms_name_PUT' : success_put,
        'services_name_uoms_name_DELETE' : success_delete
        }
        
    return result
