# -*- coding: utf-8 -*-

import json
import lib.requests as requests

def POST(fname, spost, address):
    
    #print  fname + ', POST'
    
    res = requests.post(
        address,
        data=json.dumps(spost),
        prefetch=True
    )
             
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)

    return res.json
    
def services_name_uoms_POST(sname, post):
    
    fname = '/istsos/services/{name}/uoms'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/uoms'
    
    result = POST(fname, post, address)
    return result
    
def services_POST(post):
    
    fname = '/istsos/services'
    address = 'http://localhost/istsos/wa/istsos/services'
    
    result = POST(fname, post, address)
    return result
    
def services_name_operations_insertobservation_POST(sname, post):
    
    fname = '/istsos/services/{name}/operations/insertobservation'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/operations/insertobservation'

    result = POST(fname, post, address)
    return result
    
def services_name_procedures_POST(sname, post):
    
    fname = '/istsos/services/{name}/procedures'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures'
    
    result = POST(fname, post, address)
    return result
    
def operations_validatedb_POST(post):
    
    fname = '/istsos/operations/validatedb'
    address = 'http://localhost/istsos/wa/istsos/operations/validatedb'
    
    result = POST(fname, post, address)
    return result
    
def services_name_offerings_POST(sname, post):
    
    fname = '/istsos/services/{name}/offerings'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings'
    
    result = POST(fname, post, address)
    return result
    
def services_name_offerings_name_procedures_name_POST(sname, oname, post):
    
    fname = '/istsos/services/{name}/offerings/{name}/procedures/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname + '/procedures'
    
    result = POST(fname, post, address)
    return result
    
def services_name_observedproperties_POST(sname, post):
    
    fname = '/istsos/services/{name}/observedproperties'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/observedproperties'
    
    result = POST(fname, post, address)
    return result
    
def services_name_dataqualities_POST(sname, post):
    
    fname = '/istsos/services/{name}/dataqualities'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/dataqualities'
    
    result = POST(fname, post, address)
    return result