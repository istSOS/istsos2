# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
from walib import databaseManager, utils
from walib.istsos.services.procedures.procedures import waProcedures
from walib.resource import waResourceService

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

        waProcedures.executePost(self)
        if not self.response['success'] == True:
            self.procedurename = self.json["system"]
            self.executeDelete()
            raise Exception("Error in registering %s" %(self.json["system"]))


    def executeDelete(self):
        if self.procedurename==None:
            raise Exception("Delete action without url procedure name not supported")

        #==================================
        # delete the procedure
        #==================================
        #print >> sys.stderr, "Deleting procedure.."
        waProcedures.executeDelete(self)
        #print >> sys.stderr, " > success: %s"  % self.response['success']
        if self.response['success'] == True:
            #==================================
            # remove the virtual files and folders
            #==================================
            procedureFolder = os.path.join(self.servicepath, "virtual", self.procedurename)
            if os.path.exists(procedureFolder):
                shutil.rmtree(procedureFolder)
        else:
            raise Exception("deleting procedure error!")

    def executeGet(self):
        if self.procedurename==None:
            raise Exception("GET action without url procedure name not supported")
        #==================================
        # get the procedure
        #==================================
        waProcedures.executeGet(self)

    def executePut(self):
        if self.procedurename==None:
            raise Exception("GET action without url procedure name not supported")
        #==================================
        # update the procedure
        #==================================
        waProcedures.executePut(self)

"""
{
        "system_id": "uniqueid1",
        "system": "Q_TEST",
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
                    "role": "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
                    "interval": ["12","65"]
                }
            }
        ]
    }
"""



class waGetlist(waResourceService):
    """
    Class to execute istsos/services/{serviceName}/virtualprocedures/operations/getlist
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
            proceduresList = utils.getProcedureNamesList(servicedb,self.servicename,observationType='virtual')
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


