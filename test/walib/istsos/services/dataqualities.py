# -*- coding: utf-8 -*-

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)
import pprint
import time

    
def test_dataqualities(doc):
    #services_name_dataqualities_GET(sname)
    #services_name_dataqualities_POST(sname, post)
    #services_name_dataqualities_code_GET(sname, qualcode)
    #services_name_dataqualities_code_PUT(sname, put, qualcode)
    #services_name_dataqualities_code_DELETE(sname, qualcode)
    
    doc.write('\nDATAQUALITIES\n-------------\n')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    qualcode = '42'
    post = {
        "code": 42, 
        "name": "the answer", 
        "description": "Answer to the Ultimate Question of Life, the Universe, and Everything"}
        
    put = {
        "code": 42, 
        "name": "the answer", 
        "description": "answer to the life, updated"}        
        
    success_get1 = False
    success_post = False
    success_get2 = False
    success_put = False
    success_delete = False
    
    get1 = tget.services_name_dataqualities_GET(sname)
    time.sleep(1)
    get2 = tget.services_name_dataqualities_GET(sname)
    post1 = tpost.services_name_dataqualities_POST(sname, post)
    get3 = tget.services_name_dataqualities_GET(sname)
    
    get4 = tget.services_name_dataqualities_code_GET(sname, qualcode)
    time.sleep(1)
    get5 = tget.services_name_dataqualities_code_GET(sname, qualcode)
    put1 = tput.services_name_dataqualities_code_PUT(sname, put, qualcode)
    get6 = tget.services_name_dataqualities_code_GET(sname, qualcode)
    delete1 = tdelete.services_name_dataqualities_code_DELETE(sname, qualcode)
    get7 = tget.services_name_dataqualities_code_GET(sname, qualcode)
    get8 = tget.services_name_dataqualities_GET(sname)
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            success_get1 = True
            doc.write('\n\nservices_name_dataqualities_GET: SUCCESS')
        else:
            doc.write('\n\nservices_name_dataqualities_GET: FAILED')
            doc.write('\nThe results are not consistent\n')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
    else:
        doc.write('\n\nservices_name_dataqualities_GET: FAILED')
        doc.write('\n\nservices_name_dataqualities_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get2))
        
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        #If gets before and after are the same, failure
        if get1 == get3:
            doc.write('\n\nservices_name_dataqualities_POST: FAILED')
            doc.write('\n\nservices_name_dataqualities_POST: the data has not changed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #If second get has same or less entries than first, failure
        elif get3['total'] <= get1['total']:
            doc.write('\n\nservices_name_dataqualities_POST: FAILED')
            doc.write('\n\nservices_name_dataqualities_POST: post failed or deleted another entry')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #If second get has one more entry than first, look for the 
        #inserted value. If found, success, else failure
        elif get3['total'] == get1['total'] + 1:
            for data in get3['data']:
                if (data['name'] == post['name'] 
                    and data['code'] == post['code'] 
                    and data['description'] == post['description']
                    ):
                    #pp.pprint(get3)   
                    #pp.pprint(post1)
                    doc.write('\n\nservices_name_dataqualities_POST: SUCCESS')
                    success_post = True
                    break
            if not success_post:
                doc.write('\n\nservices_name_dataqualities_POST: FAILED')
                doc.write('\n\nservices_name_dataqualities_POST: posted data does not correspond')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
        #if anything else wrong, failure
        else:
            doc.write('\n\nservices_name_dataqualities_POST: FAILED')
            doc.write('\n\nservices_name_dataqualities_POST: something went wrong')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
    #If post not successful, failure
    else:
        doc.write('\n\nservices_name_dataqualities_POST: FAILED')
        doc.write('\n\nservices_name_dataqualities_POST: post failed')
        doc.write('\nPost:\n')
        doc.write(pp.pformat(post1))
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get2))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get3))
    
    #Check for two successful requests to have the same result
    if get4['success'] and get5['success']:
        if get4 == get5:
            #print 'the results are the same:\n'
            #pp.pprint(get1)
            doc.write('\n\nservices_name_dataqualities_code_GET: SUCCESS')
            success_get2 = True
        else:
            doc.write('\n\nservices_name_dataqualities_code_GET: FAILED')
            doc.write('\n\nservices_name_dataqualities_code_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get4))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get5))
    else:
        doc.write('\n\nservices_name_dataqualities_code_GET: FAILED')
        doc.write('\n\nservices_name_dataqualities_code_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get4))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get5))
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get5 == get6:
            doc.write('\n\nservices_name_dataqualities_code_PUT: FAILED')
            doc.write('\n\nservices_name_dataqualities_code_PUT: maybe you re-wrote existing data')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(put1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get5))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get6))
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if (get6['data'][0]['code'] == put['code'] 
                and get6['data'][0]['name'] == put['name'] 
                and get6['data'][0]['description'] == put['description']
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                doc.write('\n\nservices_name_dataqualities_code_PUT: SUCCESS')
                success_put = True
            else:
                doc.write('\n\nservices_name_dataqualities_code_PUT: FAILED')
                doc.write('\n\nservices_name_dataqualities_code_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get5))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get6))
    #If post not successful, failure
    else:
        doc.write('\n\nservices_name_dataqualities_code_PUT: FAILED')
        doc.write('\n\nservices_name_dataqualities_code_PUT: the request has not been successful')
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
            doc.write('\n\nservices_name_dataqualities_code_DELETE: FAILED')
            doc.write('\n\nservices_name_dataqualities_code_DELETE: the results remained the same')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(delete1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get6))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get7))
        #For the success, second get should be void
        else:
            if get7['total'] == get6['total'] - 1 and get8 == get1:
                #print 'the delete is successful:\n'
                #pp.pprint(get6)
                doc.write('\n\nservices_name_dataqualities_code_DELETE: FAILED')
                success_delete = True
            else:
                doc.write('\n\nservices_name_dataqualities_code_DELETE: FAILED')
                doc.write('\n\nservices_name_dataqualities_code_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get6))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get7))
    #If post not successful, failure
    else:
        doc.write('\n\nservices_name_dataqualities_code_DELETE: FAILED')
        doc.write('\n\nservices_name_dataqualities_code_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(delete1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get6))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get7))
            
            
            
    result = {
        'services_name_dataqualities_GET' : success_get1,
        'services_name_dataqualities_POST' : success_post,
        'services_name_dataqualities_code_GET' : success_get2,
        'services_name_dataqualities_code_PUT' : success_put,
        'services_name_dataqualities_code_DELETE' : success_delete
        }
        
    return result