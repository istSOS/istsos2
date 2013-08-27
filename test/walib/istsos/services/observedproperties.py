# -*- coding: utf-8 -*-

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)
import pprint
import time

    
def test_observedproperties(doc, v):
    #services_name_observedproperties_GET(sname)
    #services_name_observedproperties_POST(sname, post)
    #services_name_observedproperties_name_GET(sname, oname)
    #services_name_observedproperties_name_PUT(sname, oname, put)
    #services_name_observedproperties_name_DELETE(sname, oname)
    
    print '\n-----------------OBSERVEDPROPERTIES--------------\n'
    
    if v:
        doc.write('\n\n-----------------OBSERVEDPROPERTIES-----------------')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    oname = 'urn:ogc:def:parameter:x-istsos:1.0:test_post'
    
    post = {
        "definition": "urn:ogc:def:parameter:x-istsos:1.0:test_post", 
        #"procedures": [], 
        "constraint": [],
        "name": "test_post", 
        "description": "lorem impsum dolor"
        }
        
    put = {
        "definition": "urn:ogc:def:parameter:x-istsos:1.0:test_post_up", 
        #"procedures": [], 
        "constraint": [],
        "name": "test_post", 
        "description": "updated description"}        
        
    success_get1 = False
    success_post = False
    success_get2 = False
    success_put = False
    success_delete = False
    
    get1 = tget.services_name_observedproperties_GET(sname)
    time.sleep(1)
    get2 = tget.services_name_observedproperties_GET(sname)
    post1 = tpost.services_name_observedproperties_POST(sname, post)
    get3 = tget.services_name_observedproperties_GET(sname)
    
    get4 = tget.services_name_observedproperties_name_GET(sname, oname)
    time.sleep(1)
    get5 = tget.services_name_observedproperties_name_GET(sname, oname)
    put1 = tput.services_name_observedproperties_name_PUT(sname, oname, put)
    get6 = tget.services_name_observedproperties_name_GET(sname, oname + '_up')
    delete1 = tdelete.services_name_observedproperties_name_DELETE(sname, oname + '_up')
    get7 = tget.services_name_observedproperties_name_GET(sname, oname)
    get8 = tget.services_name_observedproperties_GET(sname)
    
    
    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            print 'services_name_observedproperties_GET: SUCCESS'
            success_get1 = True
        else:
            if v:
                doc.write('\n\nservices_name_observedproperties_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get1))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get2))
            print 'services_name_observedproperties_GET: FAILED'
    else:
        if v:
            doc.write('\n\nservices_name_observedproperties_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
        print 'services_name_observedproperties_GET: FAILED'
    
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        #If gets before and after are the same, failure
        if get2 == get3:
            if v:
                doc.write('\n\nservices_name_observedproperties_POST: the data has not changed')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
            print 'services_name_observedproperties_POST: FAILED'
        #If second get has same or less entries than first, failure
        elif get3['total'] <= get2['total']:
            if v:
                doc.write('\n\nservices_name_observedproperties_POST: post failed or deleted another entry')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
            print 'services_name_observedproperties_POST: FAILED'
        #If second get has one more entry than first, look for the 
        #inserted value. If found, success, else failure
        elif get3['total'] == get2['total'] + 1:
            for data in get3['data']:
                if (data['name'] == post['name'] 
                    and data['description'] == post['description'] 
                    and data['definition'] == post['definition']
                    #and data['procedures'] == post['procedures']
                    ):
                    print 'services_name_observedproperties_POST: SUCCESS'
                    success_post = True
                    break
            if not success_post:
                if v:
                    doc.write('\n\nservices_name_observedproperties_POST: posted data does not correspond')
                    doc.write('\nPost:\n')
                    doc.write(pp.pformat(post1))
                    doc.write('\nGet, before:\n')
                    doc.write(pp.pformat(get2))
                    doc.write('\nGet, after:\n')
                    doc.write(pp.pformat(get3))
                print 'services_name_observedproperties_POST: FAILED'
        #if anything else wrong, failure
        else:
            if v:
                doc.write('\n\nservices_name_observedproperties_POST: something went wrong')
                doc.write('\nPost:\n')
                doc.write(pp.pformat(post1))
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get2))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get3))
            print 'services_name_observedproperties_POST: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\nservices_name_observedproperties_POST: post failed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get2))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get3))
        print 'services_name_observedproperties_POST: FAILED'
            
    
    #Check for two successful requests to have the same result
    if get4['success'] and get5['success']:
        if get4 == get5:
            #print 'the results are the same:\n'
            #pp.pprint(get1)
            print 'services_name_observedproperties_name_GET: SUCCESS'
            success_get2 = True
        else:
            if v:
                doc.write('\n\nservices_name_observedproperties_name_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get4))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get5))
            print 'services_name_observedproperties_name_GET: FAILED'
    else:
        if v:
            doc.write('\n\nservices_name_observedproperties_name_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get4))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get5))
        print 'services_name_observedproperties_name_GET: FAILED'
    
    
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get5 == get6:
            if v:
                doc.write('\n\nservices_name_observedproperties_name_PUT: maybe you re-wrote existing data')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get5))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get6))
            print 'services_name_observedproperties_name_PUT: FAILED'
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if len(get6['data']) > 0 and (get6['data'][0]['definition'] == put['definition'] 
                and get6['data'][0]['name'] == put['name'] 
                and get6['data'][0]['description'] == put['description']
                #and get6['data'][0]['procedures'] == put['procedures']                
                ):
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                print 'services_name_observedproperties_name_PUT: SUCCESS'
                success_put = True
            else:
                if v:
                    doc.write('\n\nservices_name_observedproperties_name_PUT: updated data does not correspond')
                    doc.write('\nPut:\n')            
                    doc.write(pp.pformat(put1)) 
                    doc.write('\nGet, before:\n')
                    doc.write(pp.pformat(get5))
                    doc.write('\nGet, after:\n')
                    doc.write(pp.pformat(get6))
                print 'services_name_observedproperties_name_PUT: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\nservices_name_observedproperties_name_PUT: the request has not been successful')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(put1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get5))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get6))
        print 'services_name_observedproperties_name_PUT: FAILED'
            
            
            
    #Checks for the DELETE to be successful by comparing two GETs
    if delete1['success']:
        #If gets before and after are the same, failure
        if get6 == get7:
            if v:
                doc.write('\n\nservices_name_observedproperties_name_DELETE: the results remained the same')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get6))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get7))
            print 'services_name_observedproperties_name_DELETE: FAILED'
        #For the success, second get should be void
        else:
            if get7['total'] == get6['total'] - 1 and get8 == get1:
                #print 'the delete is successful:\n'
                #pp.pprint(get6)
                print 'services_name_observedproperties_name_DELETE: SUCCESS'
                success_delete = True
            else:
                if v:
                    doc.write('\n\nservices_name_observedproperties_name_DELETE: the element has not been deleted')
                    doc.write('\nDelete:\n')            
                    doc.write(pp.pformat(delete1))     
                    doc.write('\nGet, before:\n')
                    doc.write(pp.pformat(get6))
                    doc.write('\nGet, after:\n')
                    doc.write(pp.pformat(get7))
                print 'services_name_observedproperties_name_DELETE: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\nservices_name_observedproperties_name_DELETE: the request has not been successful')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(delete1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get6))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get7))
        print 'services_name_observedproperties_name_DELETE: FAILED'
            
            
    result = {
        'services_name_observedproperties_GET' : success_get1,
        'services_name_observedproperties_POST' : success_post,
        'services_name_observedproperties_name_GET' : success_get2,
        'services_name_observedproperties_name_PUT' : success_put,
        'services_name_observedproperties_name_DELETE' : success_delete
        }
        
    return result