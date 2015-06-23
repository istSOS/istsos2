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

import json, pprint
import lib.requests as requests


def run():
    
    pp = pprint.PrettyPrinter(indent=2)   
    
    


def operations_status_GET(pp):
    print "operations/status, GET \n"
     
    res = requests.get(
        'http://localhost/istsos/wa/istsos/operations/status',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def operations_log_GET(pp):
    print "operations/log, GET"
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/operations/log',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def operations_log_DELETE(pp):
    print "operations/log, DELETE"
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/operations/log',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def operations_about_GET(pp):
    print "operations/about, GET"
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/operations/about',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def operations_validatedb_POST(pp):
    print "operations/validatedb, POST"
    
    put = { #not the right object implementation
        "title": "IST Sensor Observation Service 200000",
        "abstract": "hydro-meteorological monitoring network",
        "keywords": "SOS,IST,SUPSI",
        "fees": "NONE",
        "accessconstrains": "NONE",
        "authority":" x-istsos",
        "urnversion": "1.0"
    }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/operations/validatedb',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def operations_initialization_GET(pp):
    print "operations/initialization, GET"
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/operations/initialization',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def operations_initialization_PUT(pp):
    print "operations/initialization, PUT"
    
    put = {"level": "2"}
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/operations/initialization',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_GET(pp):
    print "services, GET"
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_POST(pp):
    print "services, POST"
    
    post = {
        "path": "gneeeeeeek",
        "service": "pippo"
    }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_GET(pp):
    print "services/{name}, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_PUT(pp):
    print "services/{name}, PUT"
    
    dbname = "pippo"
    
    put = {
        "service": "gianni", 
        "dbname": "istsos", 
        "host": "localhost", 
        "user": "postgres", 
        "password": "postgres", 
        "port": "5432"
    }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname,
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_DELETE(pp):
    print "services/{name}, DELETE"
    
    dbname = "test_update"
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_GET(pp):
    print "services/{name}/configsections, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_PUT(pp):
    print "services/{name}/configsections, PUT"
    
    dbname = "demo"
    
    put = {
        "getobservation": {
            "default": True, 
            "maxgoperiod": "200", 
            "aggregatenodataqi": "-100", 
            "defaultqi": "100", 
            "aggregatenodata": "-999.9"
            }, 
        "urn": {
            "process": "urn:ogc:def:process:x-istsos:1.0:", 
            "property": "urn:ogc:def:property:x-istsos:1.0:", 
            "offering": "urn:ogc:def:offering:x-istsos:1.0:", 
            "default": True, 
            "sensor": "urn:ogc:def:sensor:x-istsos:1.0:", 
            "phenomena": "urn:ogc:def:phenomenon:x-istsos:1.0:", 
            "feature": "urn:ogc:def:feature:x-istsos:1.0:", 
            "sensorType": "urn:ogc:def:sensorType:x-istsos:1.0:", 
            "dataType": "urn:ogc:def:dataType:x-istsos:1.0:", 
            "role": "urn:role:x-istsos:1.0:", 
            "refsystem": "urn:ogc:crs:EPSG:", 
            "time": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "keywords": "urn:ogc:def:keywords:x-istsos:1.0:", 
            "identifier": "urn:ogc:def:identifier:x-istsos:1.0:", 
            "parameter": "urn:ogc:def:parameter:x-istsos:1.0:", 
            "procedure": "urn:ogc:def:procedure:x-istsos:1.0:"
            }, 
        "connection": {
            "default": True, 
            "dbname": "istsos", 
            "host": "localhost", 
            "user": "postgres", 
            "password": "postgres", 
            "port": "5432"
            }, 
        "identification": {
            "title": "IST Sensor Observation Service 1", 
            "default": False, 
            "abstract": "hydro-meteorological monitoring network", 
            "urnversion": "1.0", 
            "authority": "x-istsos", 
            "fees": "NONE", 
            "keywords": "SOS,IST,SUPSI", 
            "accessconstrains": "NONE"
            }, 
        "serviceurl": {
            "default": True, 
            "url": "http://localhost/istsos/pippo"
            }, 
        "provider": {
            "contactcountry": "Switzerland", 
            "providername": "Istituto Scienze della Terra", 
            "default": True, 
            "contactposition": "Data manager", 
            "contactvoice": "+41586666200", 
            "contactadminarea": "Canton Ticino", 
            "contactemail": "geoservice@supsi.ch", 
            "contactdeliverypoint": "Campus Trevano", 
            "contactname": "Team Geomatica", 
            "contactpostalcode": "6952", 
            "contactcity": "Canobbio", 
            "providersite": "http://www.supsi.ch/ist", 
            "contactfax": "+41586666209"
            }, 
        "geo": {
            "zaxisname": "altitude", 
            "default": True, 
            "xaxisname": "easting", 
            "yaxisname": "northing", 
            "allowedepsg": "4326,3857", 
            "istsosepsg": "21781"
            }
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_DELETE(pp):
    print "services/{name}/configsections, DELETE" #shouldn't work with default as {name}
    
    dbname = 'default'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
    
def services_name_configsections_getobservation_GET(pp):
    print "services/{name}/configsections/getobservation, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/getobservation',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_getobservation_PUT(pp):
    print "services/{name}/configsections/getobservation, PUT"
    
    dbname = "demo"
    
    put = {
        "default": False, 
        "maxgoperiod": "200", 
        "aggregatenodataqi": "-100", 
        "defaultqi": "100", 
        "aggregatenodata": "-999.9"
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/getobservation',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_getobservation_DELETE(pp):
    print "services/{name}/configsections/getobservation, DELETE" #shouldn't work with default as {name}
    
    dbname = 'default'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/getobservation',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def services_name_configsections_identification_GET(pp):
    print "services/{name}/configsections/identification, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/identification',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_identification_PUT(pp):
    print "services/{name}/configsections/identification, PUT"
    
    dbname = "demo"
    
    put = {
        "title": "IST Sensor Observation Service 1", 
        "default": False, 
        "abstract": "hydro-meteorological monitoring network", 
        "urnversion": "1.0", 
        "authority": "x-istsos", 
        "fees": "NONE", 
        "keywords": "SOS,IST,SUPSI, test", 
        "accessconstrains": "NONE"}
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/identification',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_identification_DELETE(pp):
    print "services/{name}/configsections/identification, DELETE" #shouldn't work with default as {name}
    
    dbname = 'default'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/identification',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def services_name_configsections_geo_GET(pp):
    print "services/{name}/configsections/geo, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/geo',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_geo_PUT(pp):
    print "services/{name}/configsections/geo, PUT"
    
    dbname = "demo"
    
    put = {
        "zaxisname": "altitude", 
        "default": False, 
        "xaxisname": "easting", 
        "yaxisname": "northing", 
        "allowedepsg": "4326,3857", 
        "istsosepsg": "21781"
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/geo',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_geo_DELETE(pp):
    print "services/{name}/configsections/geo, DELETE" #shouldn't work with default as {name}
    
    dbname = 'default'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/geo',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def services_name_configsections_connection_GET(pp):
    print "services/{name}/configsections/connection, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/connection',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_connection_PUT(pp):
    print "services/{name}/configsections/connection, PUT"
    
    dbname = "demo"
    
    put = {
        "default": False, 
        "dbname": "istsos", 
        "host": "localhost", 
        "user": "postgres", 
        "password": "postgres", 
        "port": "5432"
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/connection',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_connection_operations_validatedb_GET(pp):
    print "services/{name}/configsections/connection/operations/validatedb, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/connection/operations/validatedb',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_serviceurl_GET(pp):
    print "services/{name}/configsections/serviceurl, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/serviceurl',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_serviceurl_PUT(pp):
    print "services/{name}/configsections/serviceurl, PUT"
    
    dbname = "demo"
    
    put = {"default": False, "url": "http://localhost/istsos/demo"}
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/serviceurl',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_serviceurl_DELETE(pp):
    print "services/{name}/configsections/serviceurl, DELETE" #shouldn't work with default as {name}
    
    dbname = 'default'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/serviceurl',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def services_name_configsections_provider_GET(pp):
    print "services/{name}/configsections/provider, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/provider',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_configsections_provider_PUT(pp):
    print "services/{name}/configsections/provider, PUT"
    
    dbname = "demo"
    
    put = {
        "contactcountry": "Switzerland", 
        "providername": "South Hampton Institute of Technology", 
        "default": False, 
        "contactposition": "Data manager", 
        "contactvoice": "+41586666200", 
        "contactadminarea": "Canton Ticino", 
        "contactemail": "geoservice@supsi.ch", 
        "contactdeliverypoint": "Campus Trevano", 
        "contactname": "Team Geomatica", 
        "contactpostalcode": "6952", 
        "contactcity": "Canobbio", 
        "providersite": "http://www.supsi.ch/ist", 
        "contactfax": "+41586666209"
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/provider',
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_configsections_provider_DELETE(pp):
    print "services/{name}/configsections/provider, DELETE" #shouldn't work with default as {name}
    
    dbname = 'default'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/configsections/provider',
        prefetch=True
    )
    
    pp.pprint(res.json)
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    print "\n ************************************ \n"
    
def services_name_dataqualities_GET(pp):
    print "services/{name}/dataqualities, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/dataqualities',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_dataqualities_POST(pp):
    print "services/{name}/dataqualities, POST"
    
    dbname = "demo"
    
    post = {
        "code": 42, 
        "name": "the answer", 
        "description": "Answer to the Ultimate Question of Life, the Universe, and Everything"}
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/dataqualities',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_dataqualities_code_GET(pp):
    print "services/{name}/dataqualities/{code}, GET"
    
    dbname = 'demo'
    qualcode = '42'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/dataqualities/' + qualcode,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_dataqualities_code_PUT(pp):
    print "services/{name}/dataqualities/{code}, PUT"
    
    dbname = "demo"
    qualcode = '42'
    
    put = {
        "code": 42, 
        "name": "the answer", 
        "description": "Answer to the Life, the Universe, and Everything"}
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/dataqualities/' + qualcode,
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_dataqualities_code_DELETE(pp):
    print "services/{name}/dataqualities/{code}, DELETE"
    
    dbname = "demo"
    qualcode = '42'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/dataqualities/' + qualcode,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_procedures_POST(pp):
    print "services/{name}/procedures, POST"
    
    dbname = "demo"
    
    post = {
        "inputs": [], 
        "description": "temperature weather station in Usmate Carate", 
        "classification": [
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType", 
            "name": "System Type", 
            "value": "insitu-fixed-point"
            }, 
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType", 
            "name": "Sensor Type", 
            "value": "tipping bucket rain gauge"
            }
        ], 
        "characteristics": "", 
        "interfaces": "", 
        "keywords": "weather,meteorological,IST", 
        "contacts": [], 
        "assignedSensorId": "6ecb65065eccaac8967089df62c81a24", 
        "documentation": [], 
        "system": "PIPPO", 
        "capabilities": [], 
        "identification": [], 
        "location": {
            "geometry": {
                "type": "Point", 
                "coordinates": ["8.96127", "46.02723", "344.1"]
                }, 
            "crs": {
                "type": "name", 
                "properties": {"name": "EPSG:4326"}
                }, 
            "type": "Feature", 
            "properties": {"name": "PIPPO"}
            }, 
        "outputs": [
            {
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "constraint": {
                "max": "", 
                "interval": ["2013-01-01T00:10:00.000000+0100", "2013-02-05T00:00:00.000000+0100"], 
                "role": "", 
                "valuelist": "", 
                "min": ""
                }, 
            "name": "Time", 
            "uom": "", 
            "description": ""
            }, 
            {
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall", 
            "constraint": {
                "max": "", 
                "interval": "", 
                "role": "", 
                "valuelist": "", 
                "min": ""
                }, 
            "name": "air-rainfall", 
            "uom": "mm", 
            "description": ""
            }
        ], 
        "system_id": "PIPPO", 
        "history": []
        }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/procedures',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_procedures_name_GET(pp):
    print "services/{name}/procedures/{name}, GET"
    
    dbname = 'demo'
    pname = 'PIPPO'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/procedures/' + pname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_procedures_name_PUT(pp):
    print "services/{name}/procedures/{name}, PUT"
    
    dbname = "demo"
    pname = 'PIPPO'
    
    put = {
        "inputs": [], 
        "description": "temperature weather station in Usmate Carate", 
        "classification": [
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType", 
            "name": "System Type", 
            "value": "insitu-fixed-point"
            }, 
            {
            "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType", 
            "name": "Sensor Type", 
            "value": "tipping bucket rain gauge"
            }
        ], 
        "characteristics": "", 
        "interfaces": "", 
        "keywords": "weather,meteorological,IST, test", 
        "contacts": [], 
        "assignedSensorId": "6ecb65065eccaac8967089df62c81a24", 
        "documentation": [], 
        "system": "PIPPO", 
        "capabilities": [], 
        "identification": [], 
        "location": {
            "geometry": {
                "type": "Point", 
                "coordinates": ["8.96127", "46.02723", "344.1"]
                }, 
            "crs": {
                "type": "name", 
                "properties": {"name": "EPSG:4326"}
                }, 
            "type": "Feature", 
            "properties": {"name": "PIPPO"}
            }, 
        "outputs": [
            {
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "constraint": {
                "max": "", 
                "interval": ["2013-01-01T00:10:00.000000+0100", "2013-02-05T00:00:00.000000+0100"], 
                "role": "", 
                "valuelist": "", 
                "min": ""
                }, 
            "name": "Time", 
            "uom": "", 
            "description": ""
            }, 
            {
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall", 
            "constraint": {
                "max": "", 
                "interval": "", 
                "role": "", 
                "valuelist": "", 
                "min": ""
                }, 
            "name": "air-rainfall", 
            "uom": "mm", 
            "description": ""
            }
        ], 
        "system_id": "PIPPO", 
        "history": []
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/procedures/' + pname,
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_procedures_name_DELETE(pp):
    print "services/{name}/procedures/{name}, DELETE"
    
    dbname = "demo"
    pname = 'PIPPO'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/procedures/' + pname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_procedures_operations_getlist_GET(pp):
    print "services/{name}/procedures/operations/getlist, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/procedures/operations/getlist',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_offerings_GET(pp):
    print "services/{name}/offerings, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_offerings_POST(pp):
    print "services/{name}/offerings, POST"
    
    dbname = 'demo'
    
    post = {
        "description": "temporary offering to hold self-registered procedures/sensors waiting for service adimistration acceptance", 
        "expiration": "", 
        "active": True, 
        "procedures": 4, 
        "id": 1, 
        "name": "piripicchio"
        }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_offerings_name_GET(pp):
    print "services/{name}/offerings/{name}, GET"
    
    dbname = 'demo'
    oname = 'piripicchio'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/' + oname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_offerings_name_PUT(pp):
    print "services/{name}/offerings/{name}, PUT"
    
    dbname = "demo"
    oname = 'piripicchio'
    
    put = {
        "description": "blablabla", 
        "expiration": "", 
        "active": True, 
        "procedures": 0, 
        "id": 2, 
        "name": "piripicchio"}
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/' + oname,
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_offerings_name_DELETE(pp):
    print "services/{name}/offerings/{name}, DELETE"
    
    dbname = "demo"
    oname = 'piripicchio'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/' + oname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_offerings_name_procedures_GET(pp):
    print "services/{name}/offerings/{name}/procedures, GET"
    
    dbname = 'demo'
    oname = 'temporary'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/' + oname + '/procedures',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_offerings_name_procedures_operations_memberlist_GET(pp):
    print "services/{name}/offerings/{name}/procedures/operations/membelist, GET"
    
    dbname = 'demo'
    oname = 'temporary'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/' + oname + '/procedures/operations/memberlist',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_offerings_name_procedures_operations_nonmemberlist_GET(pp):
    print "services/{name}/offerings/{name}/procedures/operations/nonmemberlist, GET"
    
    dbname = 'demo'
    oname = 'temporary'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/' + oname + '/procedures/operations/nonmemberlist',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
    
def services_name_offerings_operations_getlist_GET(pp):
    print "services/{name}/offerings/operations/getlist, GET"
    
    dbname = 'demo'
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/offerings/operations/getlist',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_operations_getobservation_offerings_name_procedures_GET(pp):
    print "services/{name}/operations/getobservation/offerings/{name}/procedures/..., GET"
    
    dbname = 'demo'
    oname = 'temporary'
    pname = 'BELLINZONA'
    obprop = 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature'
    start = '2013-01-01T00:10:00.000000+0100'
    end = '2013-01-05T00:00:00.000000+0100'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/operations/getobservation/offerings/' + oname + '/procedures/' + pname + '/observedproperties/' + obprop + '/eventtime/' + start + '/' + end,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_operations_insertobservation_POST(pp):
    print "services/{name}/operations/insertobservation, POST"
    
    dbname = 'demo'    
    
    post = {
    "name": "BELLINZONA", 
    "samplingTime": {
        "duration": "P34DT23H50M", 
        "beginPosition": "2013-01-01T00:10:00.000000+0100", 
        "endPosition": "2013-02-05T00:00:00.000000+0100"
        }, 
    "result": {
        "DataArray": {
            "elementCount": "3", 
            "values": [
                ["2013-01-01T00:20:00.000000+0100", "20", "100"], 
                ["2013-01-01T00:30:00.000000+0100", "20", "100"], 
                ["2013-01-01T00:40:00.000000+0100", "20", "100"], 
                ["2013-01-01T00:50:00.000000+0100", "20", "100"], 
                ["2013-01-01T01:00:00.000000+0100", "20", "100"]
            ], 
            "field": [
                {
                "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
                "name": "Time"
                }, 
                {
                "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature", 
                "name": "air-temperature", 
                "uom": "\u00b0C"
                }, 
                {"definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex", 
                 "name": "air-temperature:qualityIndex", 
                 "uom": "-"
                 }
            ]
        }
    }, 
    "featureOfInterest": {
        "geom": "<gml:Point srsName='EPSG:21781'><gml:coordinates>722032.159653624286875,118091.771747849488747,176.382462739521088</gml:coordinates></gml:Point>", 
        "name": "urn:ogc:def:feature:x-istsos:1.0:Point:BELLINZONA"
        }, 
    "observedProperty": {
        "component": [
            "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature", 
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex"
            ], 
        "CompositePhenomenon": {
            "dimension": "3", 
            "id": "comp_5", 
            "name": "timeSeriesOfObservations"
            }, 
        "components": [
            "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", 
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature", 
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex"
            ]
        }, 
    "procedure": "urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA"
    }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/operations/insertobservation',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_observedproperties_GET(pp):
    print "services/{name}/observedproperties, GET"
    
    dbname = 'demo'
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/observedproperties',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_observedproperties_POST(pp):
    print "services/{name}/observedproperties, POST"
    
    dbname = 'demo'    
    
    post = {
        "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:LOVEisintheAIR", 
        "procedures": ["P_LUGANO", "LOCARNO"], 
        "name": "LoveIsInTheAir", 
        "description": "liquid precipitation or snow water equivalent"
        }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/observedproperties',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_observedproperties_name_GET(pp):
    print "services/{name}/observedproperties/{name}, GET"
    
    dbname = 'demo'
    oname = 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:LOVEisintheAIR'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/observedproperties/' + oname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_observedproperties_name_PUT(pp):
    print "services/{name}/observedproperties/{name}, PUT"
    
    dbname = "demo"
    oname = 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:LOVEisintheAIR'
    
    put = {
        "definition": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:LoveIsInTheAir", 
        "procedures": [], 
        "name": "LoveIsInTheAir", 
        "description": "liquid precipitation or snow water equivalent"}
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/observedproperties/' + oname,
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_observedproperties_name_DELETE(pp):
    print "services/{name}/observedproperties/{name}, DELETE"
    
    dbname = "demo"
    oname = 'urn:ogc:def:parameter:x-istsos:1.0:meteo:air:LoveIsInTheAir'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/observedproperties/' + oname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_uoms_GET(pp):
    print "services/{nome}/uoms, GET"
    
    dbname = 'demo'    
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/uoms',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_uoms_POST(pp):
    print "services/{nome}/uoms, POST"
    
    dbname = 'demo'
    
    post = {
        "procedures": ["LOCARNO"], 
        "name": "am",
        "description": "Love is in the air"
        }
    
    res = requests.post(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/uoms',
        data=json.dumps(post),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_uoms_name_GET(pp):
    print "services/{name}/uoms/{name}, GET"
    
    dbname = 'demo'
    oname = 'test'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/uoms/' + oname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_uoms_name_PUT(pp):
    print "services/{name}/uoms/{name}, PUT"
    
    dbname = "demo"
    oname = 'am'
    
    put = {
        "procedures": [], 
        "name": "love", 
        "description": "Love is in the air yesss"
        }
    
    res = requests.put(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/uoms/' + oname,
        data=json.dumps(put),
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_uoms_name_DELETE(pp):
    print "services/{name}/uoms/{name}, DELETE"
    
    dbname = "demo"
    oname = 'test'
    
    res = requests.delete(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/uoms/' + oname,
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)
    print "\n ************************************ \n"
    
def services_name_epsgs_GET(pp):
    print "services/{name}/epsgs, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/epsgs',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
    
def services_name_systemtypes_GET(pp):
    print "services/{name}/systemtypes, GET"
    
    dbname = 'demo'
    
    res = requests.get(
        'http://localhost/istsos/wa/istsos/services/' + dbname + '/systemtypes',
        prefetch=True
    )
    
    try:
        res.raise_for_status() # raise exception if som comunication error occured    
    except Exception as e:
        print str(e)
        
    pp.pprint(res.json)   
    
    print "\n ************************************ \n"
