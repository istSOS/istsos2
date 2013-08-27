# -*- coding: utf-8 -*-

import lib.requests as requests

def DELETE(fname, address):
    
    #print fname + ', DELETE'
    
    res = requests.delete(
        address,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    return res.json
    
def services_name_uoms_name_DELETE(sname, uname):
    
    fname = '/istsos/services/{name}/uoms/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/uoms/' + uname
    
    result = DELETE(fname, address)
    return result
    
def services_name_DELETE(sname):
    
    fname = '/istsos/services/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname
    
    result = DELETE(fname, address)
    return result
    
def services_name_procedures_name_DELETE(sname, pname):
    
    fname = '/istsos/services/{name}/procedures/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures/' + pname
    
    result = DELETE(fname, address)
    return result
    
def operations_log_DELETE():

    fname = '/istsos/operations/log'
    address = 'http://localhost/istsos/wa/istsos/operations/log'
    
    result = DELETE(fname, address)
    return result
    
def services_name_offerings_name_DELETE(sname, oname):
    
    fname = '/istsos/services/{name}/offerings/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname
    
    result = DELETE(fname, address)
    return result
    
def services_name_offerings_name_procedures_name_DELETE(sname, oname, pname):
    
    fname = '/istsos/services/{name}/offerings/{name}/procedures/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname + '/procedures/' + pname
    
    result = DELETE(fname, address)
    return result    
    
def services_name_observedproperties_name_DELETE(sname, oname):
    
    fname = '/istsos/services/{name}/observedproperties/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/observedproperties/' + oname
    
    result = DELETE(fname, address)
    return result
    
def services_name_dataqualities_code_DELETE(sname, qualcode):
    
    fname = '/istsos/services/{name}/dataqualities/{code}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/dataqualities/' + qualcode
    
    result = DELETE(fname, address)
    return result
    
def services_name_configsections_DELETE(sname):
    
    fname = '/istsos/services/{name/default}/configsections'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections'
    
    result = DELETE(fname, address)
    return result
    
def services_name_configsections_getobservation_DELETE(sname):
    
    fname = '/istsos/services/{name/default}/configsections/getobservation'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/getobservation'
    
    result = DELETE(fname, address)
    return result
    
def services_name_configsections_identification_DELETE(sname):
    
    fname = '/istsos/services/{name/default}/configsections/identification'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/identification'
    
    result = DELETE(fname, address)
    return result
    
def services_name_configsections_geo_DELETE(sname):
    
    fname = '/istsos/services/{name/default}/configsections/geo'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/geo'
    
    result = DELETE(fname, address)
    return result
    
def services_name_configsections_serviceurl_DELETE(sname):
    
    fname = '/istsos/services/{name/default}/configsections/serviceurl'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/serviceurl'
    
    result = DELETE(fname, address)
    return result
    
def services_name_configsections_provider_DELETE(sname):
    
    fname = '/istsos/services/{name/default}/configsections/provider'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/provider'
    
    result = DELETE(fname, address)
    return result