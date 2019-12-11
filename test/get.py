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

import requests as requests

def GET(fname, address):
    
    #print fname + ', GET'
    
    res = requests.get(
        address,
        prefetch=True
    )
            
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print(str(e))
    
    return res.json
    
def services_name_uoms_GET(sname):
    
    fname = '/istsos/services/{name}/uoms'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/uoms'
    
    result = GET(fname, address)
    return result
    
def services_name_uoms_name_GET(sname, uname):
    
    fname = '/istsos/services/{name}/uoms/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/uoms/' + uname
    
    result = GET(fname, address)
    return result
    
def services_name_systemtypes_GET(sname):
    
    fname = '/istsos/services/{name}/systemtypes'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/systemtypes'
    
    result = GET(fname, address)
    return result
    
def services_GET():
    
    fname = '/istsos/services'
    address = 'http://localhost/istsos/wa/istsos/services'
    
    result = GET(fname, address)
    return result
    
def services_name_GET(sname):
    
    fname = '/istsos/services/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname
    
    result = GET(fname, address)
    return result
    
def services_name_procedures_name_GET(sname, pname):
    
    fname = '/istsos/services/{name}/procedures/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures/' + pname
    
    result = GET(fname, address)
    return result
    
def services_name_procedures_operations_getlist_GET(sname):
    
    fname = '/istsos/services/{name}/procedures/operations/getlist'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures/operations/getlist'
    
    result = GET(fname, address)
    return result
    
def services_name_procedures_name_ratingcurve_GET(sname, pname):
    
    fname = '/istsos/services/{name}/procedures/{name}/ratingcurve'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures/' + pname + '/ratingcurve'
    
    result = GET(fname, address)
    return result    
    
def operations_status_GET():
    
    fname = '/istsos/operations/status'
    address = 'http://localhost/istsos/wa/istsos/operations/status'
     
    result = GET(fname, address)
    return result
    
def operations_log_GET():
    
    fname = '/istsos/operations/log'
    address = 'http://localhost/istsos/wa/istsos/operations/log'
    
    result = GET(fname, address)
    return result
    
def operations_about_GET():
    
    fname = '/istsos/operations/aboutg'
    address = 'http://localhost/istsos/wa/istsos/operations/about'
    
    result = GET(fname, address)
    return result
    
def operations_initialization_GET():
    
    fname = '/istsos/operations/initialization'
    address = 'http://localhost/istsos/wa/istsos/operations/initialization'
    
    result = GET(fname, address)
    return result
    
def operations_getobservation_offerings_name_procedures_GET(sname, oname, pname, oprop, start, end):
    
    fname = '/istsos/services/{name}/operations/getobservation/offerings/{name}/procedures/{name}/observedproperties/{name}/eventtime/{begin}/{end}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/operations/getobservation/offerings/' + oname + '/procedures/' + pname + '/observedproperties/' + oprop + '/eventtime/' + start + '/' + end
        
    result = GET(fname, address)
    return result
    
def services_name_offerings_GET(sname):
    
    fname = '/istsos/services/{name}/offerings'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings'
    
    result = GET(fname, address)
    return result
    
def services_name_offerings_name_GET(sname, oname):
    
    fname = '/istsos/services/{name}/offerings/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname
    
    result = GET(fname, address)
    return result
    
def services_name_offerings_name_procedures_GET(sname, oname):
    
    fname = '/istsos/services/{name}/offerings/{name}/procedures'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname + '/procedures'
    
    result = GET(fname, address)
    return result
    
def services_name_offerings_name_procedures_operations_memberlist_GET(sname, oname):
    
    fname = '/istsos/services/{name}/offerings/{name}/procedures/operations/memberslist'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname + '/procedures/operations/memberslist'
    
    result = GET(fname, address)
    return result
    
def services_name_offerings_name_procedures_operations_nonmemberlist_GET(sname, oname):
    
    fname = '/istsos/services/{name}/offerings/{name}/procedures/operations/nonmemberslist'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/' + oname + '/procedures/operations/nonmemberslist'
    
    result = GET(fname, address)
    return result
    
def services_name_offerings_operations_getlist_GET(sname):
    
    fname = '/istsos/services/{name}/offerings/operations/getlist'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/offerings/operations/getlist'
    
    result = GET(fname, address)
    return result
    
def services_name_observedproperties_GET(sname):
    
    fname = '/istsos/services/{name}/observedproperties'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/observedproperties'
    
    result = GET(fname, address)
    return result
    
def services_name_observedproperties_name_GET(sname, oname):
    
    fname = '/istsos/services/{name}/observedproperties/{name}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/observedproperties/' + oname
    
    result = GET(fname, address)
    return result
    
def services_name_epsgs_GET(sname):
    
    fname = '/istsos/services/{name}/epsgs'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/epsgs'
    
    result = GET(fname, address)
    return result
    
def services_name_dataqualities_GET(sname):
    
    fname = '/istsos/services/{name}/dataqualities'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/dataqualities'
    
    result = GET(fname, address)
    return result
    
def services_name_dataqualities_code_GET(sname, qualcode):
    
    fname = '/istsos/services/{name}/dataqualities/{code}'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/dataqualities/' + qualcode
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections'
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_getobservation_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/getobservation'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/getobservation'
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_identification_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/identification'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/identification'
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_geo_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/geo'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/geo'
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_connection_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/connection'    
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/connection'
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_connection_operations_validatedb_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/connection/operations/validatedb'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/connection/operations/validatedb'

    result = GET(fname, address)
    return result
    
def services_name_configsections_serviceurl_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/serviceurl'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/serviceurl'
    
    result = GET(fname, address)
    return result
    
def services_name_configsections_provider_GET(sname):
    
    fname = '/istsos/services/{name/default}/configsections/provider'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/configsections/provider'
    
    result = GET(fname, address)
    return result
