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

import json
import requests as requests

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
        print(str(e))

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
    
def services_name_procedures_name_ratingcurve_POST(sname, pname, post):
    
    fname = '/istsos/services/{name}/procedures/{name}/ratingcurve'
    address = 'http://localhost/istsos/wa/istsos/services/' + sname + '/procedures/' + pname + '/ratingcurve'
    
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
