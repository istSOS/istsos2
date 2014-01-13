# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
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

from walib import procedure, utils, databaseManager
from walib.resource import waResourceService
import lib.requests as requests
import os
import sys

class waProcedures(waResourceService):
    """class to handle SOS service objects, support GET and POST method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.servicename = self.pathinfo[2]
        if not self.pathinfo[-1]=="procedures" and len(self.pathinfo)>4:
            self.procedurename = self.pathinfo[4]
        else:
            self.procedurename = None
    
    def executePost(self,db=True):
        """
        Method for executing a POST requests that create a new SOS procedure
                      
        @note: This method creates:
            1. Create a new procedure sending an XML to the istsos service
        
        The POST must be in Json format:
                
        >>> {
                "system_id": "P_TRE3",
                "system": "P_TRE4",
                "description": "ciao",
                "keywords": "uno,due,tre",
                "identification": [],
                "classification": [
                    {
                        "name": "System Type",
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType",
                        "value": "insitu-fixed-point"
                    },
                    {
                        "name": "Sensor Type",
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType",
                        "value": "bukket"
                    }
                ],
                "characteristics": "",
                "contacts": [],
                "documentation": [],
                "location": {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": ["123","456"]
                    },
                    "crs": {
                        "type": "name",
                        "properties": {"name": "EPSG:21781"}
                    },
                    "properties": {"name": "LUGANO"}
                },
                "interfaces": "",
                "inputs": [],
                "history": [],
                "capabilities": [
                    {
                        "name": "Memory Capacity",
                        "description": "",
                        "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:memoryCapacity",
                        "uom": "Byte",
                        "value": "131"
                    },
                    {
                        "name": "Sampling time resolution",
                        "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:samplingTimeResolution",
                        "uom": "iso8601",
                        "value": "PT10M"
                    },
                    {
                        "name": "Acquisition time resolution",
                        "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:acquisitionTimeResolution",
                        "uom": "iso8601",
                        "value": "PT1H"
                    }
                ],
                "outputs": [
                    {
                        "name": "Time",
                        "definition": "urn:ogc:def:dataType:x-istsos:1.0:time",
                        "uom": "iso8601",
                        "description": "",
                        "constraint": {
                            "role": "urn:x-ogc:def:classifiers:x-istsos:1.0:dataAvailability",
                            "min": "",
                            "max": "",
                            "interval": [123,456],
                            "valuelist": ""
                        }
                    },
                    {
                        "name": "Conductivity",
                        "definition": "urn:x-ogc:def:phenomenon:x-istsos:1.0:conductivity",
                        "uom": "Pressure",
                        "description": "foo bar",
                        "constraint": {
                            "role": "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0",
                            "interval": ["12","65"]
                        }
                    }
                ]
            }
        """
        #verify no service name in url
        if not self.procedurename==None:
            raise Exception("POST action with url procedure name not supported")
        
        proc = procedure.Procedure(self.serviceconf)
        proc.loadDICT(self.json)
        smlstring = proc.toRegisterSensor(indent=False)
        
        response = requests.post(
            self.serviceconf.serviceurl["url"], 
            data=smlstring,
            headers={"Content-type": "text/xml"}, 
            prefetch=True
        )
        
        try:
            response.raise_for_status() # raise exception if som comunication error occured            
            if response.text.find("AssignedSensorId")>0:
                self.setMessage("%s" % response.text)
            else:
                self.setException("Register sensor failed - Communication: %s - Response: %s" 
                                    %(response.status_code, response.text))
        except Exception as e:
            self.setException("Register sensor failed - Communication: %s %s - Response: %s" 
                                    %(response.status_code, e, response.text))
        
        
    def executeDelete(self):
        """
        Method for executing a DELETE requests that erase a SOS procedure
                          
            @note: This method delete:
                1. the given procedure
            
        """
        if self.procedurename==None:
            raise Exception("DELETE action without url procedure name not supported")
        
        try:
            servicedb = databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
            )
            
            #DELETE from database in transaction
            sql  = "DELETE from %s.procedures" % self.service
            sql += " WHERE name_prc = %s"
            params = (self.procedurename,)
            servicedb.executeInTransaction(sql,params)
            
            #DELETE sensorML
            procedureMLpath = os.path.join(self.sensormlpath,self.procedurename+".xml")
            os.remove(procedureMLpath)
            
           #COMMIT transaction
            servicedb.commitTransaction()
            self.setMessage("Procedure '%s' successfully deleted" % self.procedurename)
        except Exception as e:
            self.setException("%s" %e)
        
    
    def executePut(self):
        """
        Method for executing a PUT requests that update a SOS sensorML procedure
                          
            @note: This method replace old sensorML with the new one, note that 
                    database objectes are not updated. To update entirely a procedure
                    consider to delete and recreate it.
                1. ...
            
            The Put must be in Json format:
                    
            >>> {
                    ...
                } 
        """
        
        proc = procedure.Procedure()
        proc.loadDICT(self.json)
        
        '''if proc.data['system'] == self.procedurename:
            
            smlstring = proc.toXML()
            f = open(os.path.join(self.sensormlpath,self.json["system"]+".xml"), 'w')
            f.write(smlstring)
            f.close()
            self.setMessage("SensorML successfully updated")
            
        else:'''
            
        
        smlstring = proc.toXML()
        f = open(os.path.join(self.sensormlpath,self.procedurename+".xml"), 'w')
        f.write(smlstring)
        f.close()
        self.setMessage("SensorML successfully updated")            
        
        if proc.data['system'] != self.procedurename:
            
            #rename procedure in transaction
            servicedb = databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
            )
            
            sql  = "UPDATE %s.procedures" % self.service
            sql += " SET name_prc = %s WHERE name_prc= %s"
            params = (self.json["system"],self.procedurename)
            servicedb.executeInTransaction(sql,params)
            
            #rename sensorML file
            os.rename(os.path.join(self.sensormlpath,self.procedurename+".xml"),
                      os.path.join(self.sensormlpath,self.json["system"]+".xml"))
            
            #commit transaction
            servicedb.commitTransaction()
            self.setMessage("Procedure '%s' successfully renamed to '%s'" %(self.procedurename,str(self.json["system"])))
        
    def executeGet(self):
        """
        Method for executing a GET requests that rename a SOS service
        
        {
            "message": "Sensor Description secessfully loaded",
            "total": 1,
            "data": {
                "inputs": [],
                "description": "",
                "classification": [
                    {
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType",
                        "name": "System Type",
                        "value": "insitu-fixed-point"
                    },
                    {
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0:sensorType",
                        "name": "Sensor Type",
                        "value": "temperature"
                    }
                ],
                "characteristics": "",
                "interfaces": "",
                "keywords": "",
                "contacts": [],
                "assignedSensorId": "ec08e1f51ab879f4e1796f3c187daff6",
                "documentation": [],
                "system": "DEMO_1",
                "capabilities": [],
                "identification": [],
                "location": {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            "8.88",
                            "45.45"
                        ]
                    },
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "4326"
                        }
                    },
                    "type": "Feature",
                    "properties": {
                        "name": "lugano"
                    }
                },
                "outputs": [
                    {
                        "definition": "urn:ogc:def:parameter:x-istsos::time:iso8601",
                        "constraint": {
                            "max": "",
                            "interval": [
                                "2007-11-03T14:00:00+01:00",
                                "2011-12-07T18:00:00+01:00"
                            ],
                            "role": "",
                            "valuelist": "",
                            "min": ""
                        },
                        "name": "Time",
                        "uom": "",
                        "description": ""
                    },
                    {
                        "definition": "urn:ogc:def:parameter:x-istsos::meteo:air:temperature",
                        "constraint": {
                            "max": "",
                            "interval": "",
                            "role": "",
                            "valuelist": "",
                            "min": ""
                        },
                        "name": "meteo-air-temperature",
                        "uom": "deg",
                        "description": ""
                    }
                ],
                "system_id": "DEMO_1",
                "history": []
            },
            "success": true
        }
        """
        
        import lib.requests as requests
        res = requests.get(
            self.serviceconf.serviceurl["url"], 
            params={
                "request": "DescribeSensor",
                "procedure": self.procedurename,
                "outputFormat": "text/xml;subtype=\"sensorML/1.0.1\"",
                "service": "SOS",
                "version": "1.0.0"
            }
        )

        smlobj = procedure.Procedure()
        try:
            smlobj.loadXML(res.content)
        except Exception as e:
            raise Exception("Error loading DescribeSensor of '%s': %s" % (self.procedurename,e))
        
        # Searching for the assignedSensorId from the database
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port']
        )
        sql  = "SELECT assignedid_prc FROM %s.procedures " %((self.service,))
        sql  += " WHERE name_prc = %s"
        rows = servicedb.select(sql,(self.procedurename,))
        if rows:
            ret = {
                'assignedSensorId': rows[0]["assignedid_prc"]
            }
            ret.update(smlobj.data) # merging dictionaries
            self.setData(ret)
            self.setMessage("Sensor Description successfully loaded")
        else:
            self.setException("Unable to find the procedure's assignedSensorId")
        
        

class waGetlist(waResourceService):
    """
    Class to execute istsos/services/{serviceName}/procedures/operations/getlist
    """
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.servicename = self.pathinfo[2]
        
    def executeGet(self):
        if self.servicename == "default":
            raise Exception("getlist operation can not be done for default service instance.")
        else:
            data = []
            servicedb = databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
            )
            proceduresList = utils.getProcedureNamesList(servicedb,self.servicename)
            for proc in proceduresList:
                elem = {}
                elem.update(proc)
                #elem["name"] = proc["name"]
                ops = utils.getObservedPropertiesFromProcedure(servicedb,self.servicename,proc["name"])
                if ops != None:
                    elem["observedproperties"] = [ {"name" : op["name"], "uom" : op["uom"]  } for op in ops ]
                else:
                    elem["observedproperties"] = []
                offs = utils.getOfferingsFromProcedure(servicedb,self.servicename,proc["name"])
                if offs != None:
                    elem["offerings"] = [ off["name"] for off in offs ]
                else:
                    elem["offerings"] = []
                data.append(elem)
            
            self.setData(data)
            self.setMessage("Procedures of service <%s> successfully retrived" % self.servicename)
            

class waGetGeoJson(waResourceService):
    """
    Class to execute istsos/services/{serviceName}/procedures/operations/geojson/{epsg}
    """
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        print >> sys.stderr, "\n\nENVIRON: %s" % pp.pprint(self.serviceconf.get("geo")['istsosepsg'])
        if self.waEnviron['parameters'] and self.waEnviron['parameters']['epsg']:
            self.epsg = self.waEnviron['parameters']['epsg'][0]
        else:
            self.epsg = self.serviceconf.get("geo")['istsosepsg']
        
    def executeGet(self):
        if self.service == "default":
            raise Exception("getlist operation can not be done for default service instance.")
        else:
            try:
                data = {
                    "type": "FeatureCollection",
                    "features": []
                }
                servicedb = databaseManager.PgDB(self.serviceconf.connection['user'],
                                                self.serviceconf.connection['password'],
                                                self.serviceconf.connection['dbname'],
                                                self.serviceconf.connection['host'],
                                                self.serviceconf.connection['port']
                )
                proceduresList = utils.getProcedureNamesList(servicedb,self.service)
                for proc in proceduresList:
                    elem = {}
                    elem.update(proc)
                    #elem["name"] = proc["name"]
                    ops = utils.getObservedPropertiesFromProcedure(servicedb,self.service,proc["name"])
                    if ops != None:
                        elem["observedproperties"] = [ {"name" : op["name"], "uom" : op["uom"]  } for op in ops ]
                    else:
                        elem["observedproperties"] = []
                    offs = utils.getOfferingsFromProcedure(servicedb,self.service,proc["name"])
                    if offs != None:
                        elem["offerings"] = [ off["name"] for off in offs ]
                    else:
                        elem["offerings"] = []
                        
                     
                    geom = utils.getGeoJSONFromProcedure(servicedb, self.service,proc["name"], self.epsg)
                    if geom == None:
                        continue
                    
                    data["features"].append({
                        "type": "Feature",
                        "geometry": geom,
                        "properties": elem
                    })
                
                self.setData(data)
            except Exception as e:
                self.setMessage("%s" % e)
                
            
    
    def setData(self,data):
        """ Set data in response """
        self.response = data
        
