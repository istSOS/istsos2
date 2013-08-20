# -*- coding: utf-8 -*-

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)
import pprint
import time
    
    
def test_operations(doc, v):
    #operations_status_GET()
    #operations_log_GET()
    #operations_log_DELETE()
    #operations_about_GET()
    #operations_validatedb_POST(post_db)
    #operations_initialization_GET()
    #operations_initialization_PUT(put)
    #operations_getobservation_offerings_name_procedures_GET(sname, oname, pname, oprop, start, end)
    
    print '\n-----------------OPERATIONS----------------------\n'
    
    if v:
        doc.write('\n\n-----------------OPERATIONS-------------------------') 
    
    pp = pprint.PrettyPrinter(indent=2)   
    
    sname = 'test'
    oname = 'temporary'
    pname = 'test'
    oprop = 'test'
    start = '2013-01-01T00:10:00.000000+0100'
    end = '2013-01-05T00:00:00.000000+0100'
    
    post_db = {
        "user" : "postgres",
        "password" : "postgres",
        "dbname" : "istsos",
        "host" : "localhost",
        "port" : 5432
    }
        
    put = {"level": 42}        
        
    success_get1 = False
    success_get2 = False
    success_get3 = False
    success_get4 = False
    success_post = False
    success_put = False
    success_delete = False
    success_getobs = False
    
    get1 = tget.operations_status_GET()
    time.sleep(1)
    get2 = tget.operations_status_GET()
    
    get3 = tget.operations_log_GET()
    time.sleep(1)
    get4 = tget.operations_log_GET()
    delete1 = tdelete.operations_log_DELETE()
    get5 = tget.operations_log_GET()
    
    get6 = tget.operations_about_GET()
    time.sleep(1)
    get7 = tget.operations_about_GET()
    
    post1 = tpost.operations_validatedb_POST(post_db)
    
    get8 = tget.operations_initialization_GET()
    time.sleep(1)
    get9 = tget.operations_initialization_GET()
    put1 = tput.operations_initialization_PUT(put)
    get10 = tget.operations_initialization_GET()
    
    get11 = tget.operations_getobservation_offerings_name_procedures_GET(sname, oname, pname, oprop, start, end)
    time.sleep(1)
    get12 = tget.operations_getobservation_offerings_name_procedures_GET(sname, oname, pname, oprop, start, end)

    
    #Check for two successful requests to have the same result
    if get1['success'] and get2['success']:
        if get1 == get2:
            print 'operations_status_GET: SUCCESS'
            success_get1 = True
        else:
            if v:
                doc.write('\n\noperations_status_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get1))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get2))
            print 'operations_status_GET: FAILED'
    else:
        if v:
            doc.write('\n\noperations_status_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get2))
        print 'operations_status_GET: FAILED'
        
    
    #Check for two successful requests to have the same result
    if get3['success'] and get4['success']:
        if get3 == get4:
            print 'operations_log_GET: SUCCESS'
            success_get2 = True
        else:
            if v:
                doc.write('\n\noperations_log_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get3))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get4))
            print 'operations_log_GET: FAILED'
    else:
        if v:
            doc.write('\n\noperations_log_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get3))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get4))
        print 'operations_log_GET: FAILED'
        
        
    #Checks for the DELETE to be successful by comparing two GETs
    if delete1['success']:
        #If gets before and after are the same, failure
        if get4 == get5:
            if v:
                doc.write('\n\noperations_log_DELETE: the results remained the same')
                doc.write('\nDelete:\n')            
                doc.write(pp.pformat(delete1))     
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get4))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get5))
            print 'operations_log_DELETE: FAILED'
        #For the success, second get should be void
        else:
           if not get5['success']:
                print 'operations_log_DELETE: SUCCESS'
                success_delete = True
           else:
               if v:
                   doc.write('\n\noperations_log_DELETE: the element has not been deleted')
                   doc.write('\nDelete:\n')            
                   doc.write(pp.pformat(delete1))     
                   doc.write('\nGet, before:\n')
                   doc.write(pp.pformat(get4))
                   doc.write('\nGet, after:\n')
                   doc.write(pp.pformat(get5))
               print 'operations_log_DELETE: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\noperations_log_DELETE: the request has not been successful')
            doc.write('\nDelete:\n')            
            doc.write(pp.pformat(delete1))     
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get4))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get5))
        print 'operations_log_DELETEE: FAILED'
            
            
    #Check for two successful requests to have the same result
    if get6['success'] and get7['success']:
        if get6 == get7:
            print 'operations_about_GET: SUCCESS'
            success_get3 = True
        else:
            if v:
                doc.write('\n\noperations_about_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get6))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get7))
            print 'operations_about_GET: FAILED'
    else:
        if v:
            doc.write('\n\noperations_about_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get6))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get7))
        print 'operations_about_GET: FAILED'
    
     
    #Checks for the POST to be successful by comparing two GETs
    if post1['success']:
        print 'operations_validatedb_POST: SUCCESS'
        success_post = True  
    else:
        if v:
            doc.write('\n\noperations_validatedb_POST: post failed')
            doc.write('\nPost:\n')
            doc.write(pp.pformat(post1))
        print 'operations_validatedb_POST: FAILED'        
        
    
    #Check for two successful requests to have the same result
    if get8['success'] and get9['success']:
        if get8 == get9:
            print 'operations_initialization_GET: SUCCESS'
            success_get4 = True
        else:
            if v:
                doc.write('\n\noperations_initialization_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get8))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get9))
            print 'operations_initialization_GET: FAILED'
    else:
        if v:
            doc.write('\n\noperations_initialization_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get8))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get9))
        print 'operations_initialization_GET: FAILED'    
    
    
    
    #Checks for the PUT to be successful by comparing two GETs
    if put1['success']:
        #If gets before and after are the same, failure
        if get9 == get10:
            if v:
                doc.write('\n\noperations_initialization_PUT: maybe you re-wrote existing data')
                doc.write('\nPut:\n')            
                doc.write(pp.pformat(put1)) 
                doc.write('\nGet, before:\n')
                doc.write(pp.pformat(get9))
                doc.write('\nGet, after:\n')
                doc.write(pp.pformat(get10))
            print 'operations_initialization_PUT: FAILED'
        #For the success, second get should be the same as first
        #apart from the modicifation done with put
        else:
            if get10['data']['level'] == put['level']:
                #print 'the update is successful:\n'
                #pp.pprint(get6)
                print 'operations_initialization_PUT: SUCCESS'
                success_put = True
            else:
                if v:
                    doc.write('\n\noperations_initialization_PUT: updated data does not correspond')
                    doc.write('\nPut:\n')            
                    doc.write(pp.pformat(put1)) 
                    doc.write('\nGet, before:\n')
                    doc.write(pp.pformat(get9))
                    doc.write('\nGet, after:\n')
                    doc.write(pp.pformat(get10))
                print 'operations_initialization_PUT: FAILED'
    #If post not successful, failure
    else:
        if v:
            doc.write('\n\noperations_initialization_PUT: the request has not been successful')
            doc.write('\nPut:\n')            
            doc.write(pp.pformat(put1)) 
            doc.write('\nGet, before:\n')
            doc.write(pp.pformat(get9))
            doc.write('\nGet, after:\n')
            doc.write(pp.pformat(get10))
        print 'operations_initialization_PUT: FAILED'
            
    
    #Check for two successful requests to have the same result
    if get11['success'] and get12['success']:
        if get11 == get12:
            print 'operations_getobservation_offerings_name_procedures_GET: SUCCESS'
            success_getobs = True
        else:
            if v:
                doc.write('\n\noperations_getobservation_offerings_name_procedures_GET: the results are not all the same')
                doc.write('\nFirst get:\n')
                doc.write(pp.pformat(get11))
                doc.write('\nSecond get:\n')
                doc.write(pp.pformat(get12))
            print 'operations_getobservation_offerings_name_procedures_GET: FAILED'
    else:
        if v:
            doc.write('\n\noperations_getobservation_offerings_name_procedures_GET: the requests have not been successful')
            doc.write('\nFirst get:\n')
            doc.write(pp.pformat(get11))
            doc.write('\nSecond get:\n')
            doc.write(pp.pformat(get12))
        print 'operations_getobservation_offerings_name_procedures_GET: FAILED'
        
        
    result = {
        'operations_status_GET' : success_get1,
        'operations_log_GET' : success_get2,
        'operations_about_GET' : success_get3,
        'operations_initialization_GET' : success_get4,
        'operations_validatedb_POST' : success_post,
        'operations_initialization_PUT' : success_put,
        'operations_log_DELETE' : success_delete,
        'operations_getobservation_offerings_name_procedures_GET' : success_getobs
        }
        
    return result