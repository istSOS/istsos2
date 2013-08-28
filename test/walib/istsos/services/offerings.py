# -*- coding: utf-8 -*-

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)
import pprint
import time

    
def test_offerings(doc):
    #services_name_offerings_GET(sname)
    #services_name_offerings_POST(sname, post)
    #services_name_offerings_name_GET(sname, oname)
    #services_name_offerings_name_PUT(sname, oname, put)
    #services_name_offerings_name_DELETE(sname, oname)
    #services_name_offerings_name_procedures_GET(sname, oname)
    #services_name_offerings_name_procedures_operations_memberlist_GET(sname, oname)
    #services_name_offerings_name_procedures_operations_nonmemberlist_GET(sname, oname)
    #services_name_offerings_operations_getlist_GET(sname)
    #services_name_offerings_name_procedures_name_POST(sname, post)
    #services_name_offerings_name_procedures_name_DELETE(sname)
    
    doc.write('\n-----------------OFFERINGS-----------------------\n')
    
    pp = pprint.PrettyPrinter(indent=2)
    
    sname = 'test'
    oname = 'test'
    pname = 'test'
    delname = 'test_post'
    
    post = {
        "description": "test_post", 
        "expiration": "", 
        "active": "on", 
        #"procedures": 4, 
        #"id": 1, 
        "name": "test"
        }
        
    postproc = [{
        "offering": "test_post",
        "procedure": "test"
                }]
        
    put = {
        "description": "updated description", 
        "expiration": "", 
        #"active": True, 
        #"procedures": 0, 
        #"id": 14, 
        "name": "test_post"}        
        
    success_get1 = False
    success_post = False
    success_get2 = False
    success_put = False
    success_delete = False
    success_get3 = False
    success_getmem = False
    success_getnmem = False
    success_getlist = False
    success_postprog = False
    success_delprog = False
    
    
    get1 = tget.services_name_offerings_GET(sname)
    time.sleep(1)
    get2 = tget.services_name_offerings_GET(sname)
    post1 = tpost.services_name_offerings_POST(sname, post)
    get3 = tget.services_name_offerings_GET(sname)
    
    get4 = tget.services_name_offerings_name_GET(sname, oname)
    time.sleep(1)
    get5 = tget.services_name_offerings_name_GET(sname, oname)
    put1 = tput.services_name_offerings_name_PUT(sname, oname, put)
    get6 = tget.services_name_offerings_name_GET(sname, oname)
    
    post2 = tpost.services_name_offerings_name_procedures_name_POST(sname, oname, postproc)
    
    delete2 = tdelete.services_name_offerings_name_procedures_name_DELETE(sname, oname, pname)
    
    delete1 = tdelete.services_name_offerings_name_DELETE(sname, delname)
    
    get7 = tget.services_name_offerings_name_GET(sname, oname)
    get8 = tget.services_name_offerings_GET(sname)
    
    get9 = tget.services_name_offerings_name_procedures_GET(sname, oname)
    time.sleep(1)
    get10 = tget.services_name_offerings_name_procedures_GET(sname, oname)
    
    get11 = tget.services_name_offerings_name_procedures_operations_memberlist_GET(sname, oname)
    time.sleep(1)
    get12 = tget.services_name_offerings_name_procedures_operations_memberlist_GET(sname, oname)
    
    get13 = tget.services_name_offerings_name_procedures_operations_nonmemberlist_GET(sname, oname)
    time.sleep(1)
    get14 = tget.services_name_offerings_name_procedures_operations_nonmemberlist_GET(sname, oname)
    
    get15 = tget.services_name_offerings_operations_getlist_GET(sname)
    time.sleep(1)
    get16 = tget.services_name_offerings_operations_getlist_GET(sname)
    
    
    
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            doc.write('services_name_offerings_GET: SUCCESS')
            success_get1 = True
        else:
            doc.write('services_name_offerings_GET: FAILED')
            doc.write('\n\nservices_name_offerings_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
    else:
        doc.write('services_name_offerings_GET: FAILED')
        doc.write('\n\nservices_name_offerings_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get2))
    
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            doc.write('services_name_offerings_POST: FAILED')
            doc.write('\n\nservices_name_offerings_POST: the data has not changed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        #If second get has same or less entries than first, failure
        elif get3['total'] <= get2['total']:
            doc.write('services_name_offerings_POST: FAILED')
            doc.write('\n\nservices_name_offerings_POST: post failed or deleted another entry')
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
                    and data['expiration'] == post['expiration']
                    #and data['active'] == post['active']
                    #and data['procedures'] == post['procedures']
                    #and data['id'] == post['id']
                    ):
                    #pp.pprint(get3)   
                    #pp.pprint(post1)
                    doc.write('services_name_offerings_POST: SUCCESS')
                    success_post = True
                    break
            if not success_post:
                doc.write('services_name_offerings_POST: FAILED')
                doc.write('\n\nservices_name_offerings_POST: posted data does not correspond')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
        #if anything else wrong, failure
        else:
            doc.write('services_name_offerings_POST: FAILED')
            doc.write('\n\nservices_name_offerings_POST: something went wrong')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
    #If post not successful, failure
    else:
        doc.write('services_name_offerings_POST: FAILED')
        doc.write('\n\nservices_name_offerings_POST: post failed')
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
            doc.write('services_name_offerings_name_GET: SUCCESS')
            success_get2 = True
        else:
            doc.write('services_name_offerings_name_GET: FAILED')
            doc.write('\n\nservices_name_offerings_name_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get4))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get5))
    else:
        doc.write('services_name_offerings_name_GET: FAILED')
        doc.write('\n\nservices_name_offerings_name_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get4))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get5))
    
    
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get5 == get6:
            doc.write('services_name_offerings_name_PUT: FAILED')
            doc.write('\n\nservices_name_offerings_name_PUT: maybe you re-wrote existing data')
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
                if (data['description'] == put['description'] 
                    and data['name'] == put['name']
                    and data['expiration'] == put['expiration']
                    #and data['active'] == put['active']
                    #and data['procedures'] == put['procedures']
                    #and data['id'] == put['id']
                    ):
                    doc.write('services_name_offerings_name_PUT: SUCCESS')
                    success_put = True
                    break
            if not success_put:
                doc.write('services_name_offerings_name_PUT: FAILED')
                doc.write('\n\nservices_name_offerings_name_PUT: updated data does not correspond')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get5))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get6))
    #If post not successful, failure
    else:
        doc.write('services_name_offerings_name_PUTT: FAILED')
        doc.write('\n\nservices_name_offerings_name_PUT: the request has not been successful')
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
            doc.write('services_name_offerings_name_DELETE: FAILED')
            doc.write('\n\nservices_name_offerings_name_DELETE: the results remained the same')
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
                doc.write('services_name_offerings_name_DELETE: SUCCESS')
                success_delete = True
            else:
                doc.write('services_name_offerings_name_DELETE: FAILED')
                doc.write('\n\nservices_name_offerings_name_DELETE: the element has not been deleted')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get6))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get7))
    #If post not successful, failure
    else:
        doc.write('services_name_offerings_name_DELETE: FAILED')
        doc.write('\n\nservices_name_offerings_name_DELETE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(delete1))     
        doc.write('\nGet, before:\n')
        doc.write(pp.pformat(get6))
        doc.write('\nGet, after:\n')
        doc.write(pp.pformat(get7))
            
    
    
    #Check for two successful requests to have the same result
    if get9['success'] and get10['success']:
        if get9 == get10:
            doc.write('services_name_offerings_name_procedures_GET: SUCCESS')
            success_get3 = True
        else:
            doc.write('services_name_offerings_name_procedures_GET: FAILED')
            doc.write('\n\nservices_name_offerings_name_procedures_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get9))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get10))
    else:
        doc.write('services_name_offerings_name_procedures_GET: FAILED')
        doc.write('\n\nservices_name_offerings_name_procedures_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get9))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get10))
        
        
    #Check for two successful requests to have the same result
    if get11['success'] and get12['success']:
        if get11 == get12:
            doc.write('services_name_offerings_name_procedures_operations_memberlist_GET: SUCCESS')
            success_getmem = True
        else:
            doc.write('services_name_offerings_name_procedures_operations_memberlist_GET: FAILED')
            doc.write('\n\nservices_name_offerings_name_procedures_operations_memberlist_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get11))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get12))
    else:
        doc.write('services_name_offerings_name_procedures_operations_memberlist_GET: FAILED')
        doc.write('\n\nservices_name_offerings_name_procedures_operations_memberlist_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get11))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get12))
        
        
    #Check for two successful requests to have the same result
    if get13['success'] and get14['success']:
        if get13 == get14:
            doc.write('services_name_offerings_name_procedures_operations_nonmemberlist_GET: SUCCESS')
            success_getnmem = True
        else:
            doc.write('services_name_offerings_name_procedures_operations_nonmemberlist_GET: FAILED')
            doc.write('\n\nservices_name_offerings_name_procedures_operations_nonmemberlist_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get13))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get14))
            
    else:
        doc.write('services_name_offerings_name_procedures_operations_nonmemberlist_GET: FAILED')
        doc.write('\n\nservices_name_offerings_name_procedures_operations_nonmemberlist_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get13))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get14))
        
        
        
  #Check for two successful requests to have the same result
    if get15['success'] and get16['success']:
        if get15 == get16:
            doc.write('services_name_offerings_name_operations_getlist_GET: SUCCESS')
            success_getlist = True
        else:
            doc.write('services_name_offerings_name_operations_getlist_GET: FAILED')
            doc.write('\n\nservices_name_offerings_name_operations_getlist_GET: the results are not all the same')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get15))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get16))
            
    else:
        doc.write('services_name_offerings_name_operations_getlist_GET: FAILED')
        doc.write('\n\nservices_name_offerings_name_operations_getlist_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')
        doc.write(pp.pformat(get15))
        doc.write('\nSecond get:\n')
        doc.write(pp.pformat(get16))
        
        
   
    #Checks for the POST to be successful by comparing two GETs
    if post2['success']:
        doc.write('services_name_offerings_name_procedures_name_POST: SUCCESS')
        success_postprog= True
    #If post not successful, failure
    else:
        doc.write('services_name_offerings_name_procedures_name_POST: FAILED')
        doc.write('\n\nservices_name_offerings_name_procedures_name_POST: post failed')
        doc.write('\nPost:\n')
        doc.write(pp.pformat(post2))
             
        
       
    #Checks for the DELETE to be successful by comparing two GETs
    if delete2['success']:
        doc.write('services_name_offerings_name_procedures_name_DELETE: SUCCESS')
        success_delprog = True
    #If post not successful, failure
    else:
        doc.write('services_name_offerings_name_procedures_name_DELETE: FAILED')       
        doc.write('\n\nservices_name_offerings_name_procedures_name_DELETEE: the request has not been successful')
        doc.write('\nDelete:\n')            
        doc.write(pp.pformat(delete2))
       
    
        
    result = {
        'services_name_offerings_GET' : success_get1,
        'services_name_offerings_POST' : success_post,
        'services_name_offerings_name_GET' : success_get2,
        'services_name_offerings_name_PUT' : success_put,
        'services_name_offerings_name_DELETE' : success_delete,
        'services_name_offerings_name_procedures_GET' : success_get3,
        'services_name_offerings_name_procedures_operations_memberlist_GET' : success_getmem,
        'services_name_offerings_name_procedures_operations_nonmemberlist_GET' : success_getnmem,
        'services_name_offerings_operations_getlist_GET' : success_getlist,
        'services_name_offerings_name_procedures_name_POST' : success_postprog,
        'services_name_offerings_name_procedures_name_DELETE' : success_delprog
        }
            
    return result