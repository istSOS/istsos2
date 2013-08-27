# -*- coding: utf-8 -*-

import test.get as tget #GET(fname, address)
import test.post as tpost #POST(fname, spost, address)
import test.put as tput #PUT(fname, sput, address)
import test.delete as tdelete #DELETE(fname, address)
import time
import pprint

   
def test_systemtypes(doc, v):
    #services_name_systemtypes_GET(sname)
    
    print '\n-----------------SYSTEMTYPES---------------------\n'
    print '\nRequest services_name_systemtypes_GET is not implemented\n'
    
#    if v:
#        doc.write('\n\n-----------------SYSTEMTYPES------------------------')
#    
#    pp = pprint.PrettyPrinter(indent=2)    
#    sname = 'test'
#    success = False
#    
#    get1 = tget.services_name_systemtypes_GET(sname)
#    time.sleep(1)
#    get2 = tget.services_name_systemtypes_GET(sname)
#    
#    
#    #Checks if all the requests were successful
#    if get1['success'] and get2['success']:
#        #Checks if all the requests got the same result
#        if get1 == get2:
#            print 'services_name_systemtypes_GET: SUCCESS'
#            success = True
#        #If the results are not all the same, we got a failure
#        else:
#            if v:
#                doc.write('\n\nservices_name_systemtypes_GET: the results are not all the same')
#                doc.write('\nFirst get:\n')            
#                doc.write(pp.pformat(get1))
#                doc.write('\nSecond get:\n')            
#                doc.write(pp.pformat(get2))
#            print 'services_name_systemtypes_GET: FAILED'
#    #If the requests weren't all successful, we got a failure
#    else:
#        if v:
#            doc.write('\n\nservices_name_systemtypes_GET: the requests have not been successful')
#            doc.write('\nFirst get:\n')            
#            doc.write(pp.pformat(get1))
#            doc.write('\nSecond get:\n')            
#            doc.write(pp.pformat(get2))
#        print 'services_name_systemtypes_GET: FAILED'
#        
#    result = {'services_name_systemtypes_GET' : success}
#    return result