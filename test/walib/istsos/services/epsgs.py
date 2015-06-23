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
import time
import pprint

    
def test_epsgs(doc):
    #services_name_epsgs_GET(sname)
    
    doc.write('\n\n-----------------EPSGS------------------------------')
    
    pp = pprint.PrettyPrinter(indent=2)    
    sname = 'test'
    success = False
    
    get1 = tget.services_name_epsgs_GET(sname)
    time.sleep(1)
    get2 = tget.services_name_epsgs_GET(sname)
    
    #Checks if all the requests were successful
    if get1['success'] and get2['success']:
        #Checks if all the requests got the same result
        if get1 == get2:
            doc.write('services_name_epsgs_GET: SUCCESS')
            success = True
        #If the results are not all the same, we got a failure
        else:
            doc.write('services_name_epsgs_GET: FAILED')
            doc.write('\n\nservices_name_epsgs_GET: the results are not all the same')
            doc.write('\nFirst get:\n')            
            doc.write(pp.pformat(get1))
            doc.write('\nSecond get:\n')            
            doc.write(pp.pformat(get2))
    #If the requests weren't all successful, we got a failure
    else:
        doc.write('services_name_epsgs_GET: FAILED')
        doc.write('\n\nservices_name_epsgs_GET: the requests have not been successful')
        doc.write('\nFirst get:\n')            
        doc.write(pp.pformat(get1))
        doc.write('\nSecond get:\n')            
        doc.write(pp.pformat(get2))
        
        
        
        
    result = {'services_name_epsgs_GET' : success}
    return result
