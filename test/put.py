# -*- coding: utf-8 -*-

import json
import lib.requests as requests

def PUT(fname, sput, address):
    
    #print fname + ', PUT'
    
    res = requests.put(
        address,
        data=json.dumps(sput),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
    
    return res.json
    
def services_name_uoms_name_PUT(sname, uname, put):
    
    fname = '/istsos/services/{name}/uoms/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/uoms/' + uname
    
    result = PUT(fname, put, address)
    return result
    
def services_name_PUT(put, sname):
    
    fname = '/istsos/services/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname
    
    result = PUT(fname, put, address)
    return result
    
def services_name_procedures_name_PUT(sname, pname, put):
    
    fname = '/istsos/services/{name}/procedures/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures/' + pname
    
    result = PUT(fname, put, address)
    return result
    
def operations_initialization_PUT(put):
    
    fname = '/istsos/operations/initialization'
    address = 'http://localhost/istsos/wa/istsos/operations/initialization'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_offerings_name_PUT(sname, oname, put):
    
    fname = '/istsos/services/{name}/offerings/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname
    
    result = PUT(fname, put, address)
    return result
    
def services_name_observedproperties_name_PUT(sname, oname, put):
    
    fname = '/istsos/services/{name}/observedproperties/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/observedproperties/' + oname
    
    result = PUT(fname, put, address)
    return result
    
def services_name_dataqualities_code_PUT(sname, put, qualcode):
    
    fname = '/istsos/services/{name}/dataqualities/{code}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/dataqualities/' + qualcode
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_getobservation_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections/getobservation'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/getobservation'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_identification_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections/identification'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/identification'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_geo_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections/geo'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/geo'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_connection_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections/connection'    
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/connection'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_serviceurl_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections/serviceurl'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/serviceurl'
    
    result = PUT(fname, put, address)
    return result
    
def services_name_configsections_provider_PUT(sname, put):
    
    fname = '/istsos/services/{name/default}/configsections/provider'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/provider'
    
    result = PUT(fname, put, address)
    return result