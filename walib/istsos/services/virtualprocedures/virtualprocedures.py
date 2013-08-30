# -*- coding: utf-8 -*-

from walib import databaseManager
from walib.istsos.services.procedures.procedures import waProcedures

import os, sys
import shutil

# istsos/services/test/virtualprocedures/Q_TEST
class waVirtualProcedures(waProcedures):
    
    def __init__(self,waEnviron):
        super(waProcedures, self).__init__(waEnviron)
        self.servicename = self.pathinfo[2]
        if not self.pathinfo[-1]=="virtualprocedures" and len(self.pathinfo)>4:
            self.procedurename = self.pathinfo[4]
        else:
            self.procedurename = None
            
    def executePost(self):
        if not self.procedurename==None:
            raise Exception("POST action with url procedure name not supported")
        
        #==================================
        # create the procedure as fixed
        #==================================
        for cl in self.json["classification"]:
            if cl["name"] == "System Type":
                cl["value"] = "insitu-fixed-point"
        
        waProcedures.executePost(self)
        if self.response['success'] == True:            
            #==================================
            # make it virtual
            #==================================
            servicedb = databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
            )            
            sql  = "UPDATE %s.procedures " %(self.servicename)
            sql  += " SET id_oty_fk = 3 WHERE name_prc = %s"
            #print >> sys.stderr, "sql: %s" %(sql)
            try:
                servicedb.execute(sql,(self.json["system"],))
                #chenge the sml replace("insitu-fixed-point","virtual")
                sensorml = os.path.join(self.servicepath, "sml", self.json["system"]+".xml")
                print >> sys.stderr, "sensorml: %s" %(sensorml)
                with open(sensorml, 'r') as content_file:
                    content = content_file.read()
                    print >> sys.stderr, "content: %s" %(content)
                if content.find("insitu-fixed-point")>0:
                    print >> sys.stderr, "FIND!!!"
                    content = content.replace("insitu-fixed-point","virtual")
                else:
                    print >> sys.stderr, "content: %s" %(content)
                with open(sensorml, 'w') as content_file:
                    print >> sys.stderr, "content: %s" %(content)
                    content_file.write(content)
                #=====================================
                # create the virtual procedure folder
                #=====================================      
                procedureFolder = os.path.join(self.servicepath, "virtual", self.procedurename)
                if not os.path.exists(procedureFolder):
                    os.makedirs(procedureFolder)
            except Exception as e:
                servicedb.mogrify(sql,(self.json["system"],))
                self.procedurename = self.json["system"]
                waProcedures.executeDelete(self)
                raise Exception("Error in registering %s: %s" %(self.json["system"],e))
                
                
            
    def executeDelete(self):
        if self.procedurename==None:
            raise Exception("POST action without url procedure name not supported")
        
        #==================================
        # delete the procedure
        #==================================
        waProcedures.executeDelete(self)
        if self.response['success'] == True:
                #==================================
                # remove the virtual files and folders
                #==================================
                procedureFolder = os.path.join(self.servicepath, "/virtual/", self.procedurename)
                if os.path.exists(procedureFolder):
                    shutil.rmtree(procedureFolder)
            
    def executeGet(self):
        if self.procedurename==None:
            raise Exception("POST action without url procedure name not supported")
        #==================================
        # delete the procedure
        #==================================
        waProcedures.executeGet(self)
        
        
 
"""
{
        "system_id": "P_TRE3",
        "system": "P_TRE4",
        "description": "ciao",
        "keywords": "uno,due,tre",
        "identification": [],
        "classification": [
            {
                "name": "System Type",
                "definition": "urn:ogc:def:classifier:x-istsos:1.0:systemType",
                "value": "virtual"
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
        "capabilities": [],
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
                "name": "Discharge",
                "definition": "urn:x-ogc:def:phenomenon:x-istsos:1.0:discharge",
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