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
from walib import utils, databaseManager
from walib.resource import waResourceService

class waProcedures(waResourceService):
    """class to handle SOS procedures objects in related to an offering, support GET and POST method"""
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.offering = self.pathinfo[(self.pathinfo.index("offerings")+1)]
    
    def executePost(self):
        """
        Method for executing a POST requests that initialize a new SOS service
                      
        @note: This method creates a new istSOS offering
        
        The POST must be in Json format with mandatory offering key:
                
        >>> [
                {
                    "offerings": "meteo",
                    "procedure": "RAIN_SENSOR_2"
                },{
                    "offerings": "meteo",
                    "procedure": "RAIN_SENSOR_1"
                }
            ] 
        """
        # Preparing select for extracting the offering id
        sqlIdOff = "(SELECT id_off FROM %s.offerings" % self.service
        sqlIdOff += " WHERE name_off = %(name_off)s)"
        
        # Preparing select for extracting the procedure id
        sqlIdPrc = "(SELECT id_prc FROM %s.procedures" % self.service
        sqlIdPrc += " WHERE name_prc = %(name_prc)s)"
        
        sql  = "INSERT INTO %s.off_proc (id_off_fk,id_prc_fk) " % self.service
        sql += """VALUES (%s, %s)""" % (sqlIdOff,sqlIdPrc)
        
        pars = ()
        for j in self.json:
            pars = pars + (
                {
                    "name_off": j["offering"],
                    "name_prc": j["procedure"]
                },
            )
        databaseManager.PgDB(
            self.serviceconf.connection["user"],
            self.serviceconf.connection["password"],
            self.serviceconf.connection["dbname"],
            self.serviceconf.connection["host"],
            self.serviceconf.connection["port"]
        ).insertMany(sql,pars)
        
        self.setMessage("new offering successfully added")
    
    def executeDelete(self):
        """
        Method for executing a DELETE requests remove an offering procedure member
        """
        
        self.procedure = self.pathinfo[(self.pathinfo.index("procedures")+1)]
        
        # Preparing select for extracting the offering id
        sqlIdOff = "(SELECT id_off FROM %s.offerings" % self.service
        sqlIdOff += " WHERE name_off = %s)"
        
        # Preparing select for extracting the procedure id
        sqlIdPrc = "(SELECT id_prc FROM %s.procedures" % self.service
        sqlIdPrc += " WHERE name_prc = %s)"
        
        sql  = "DELETE FROM %s.off_proc " % self.service
        sql += "WHERE id_off_fk = %s AND id_prc_fk = %s" % (sqlIdOff,sqlIdPrc)
        
        pars = (self.offering, self.procedure)
        
        databaseManager.PgDB(
            self.serviceconf.connection["user"],
            self.serviceconf.connection["password"],
            self.serviceconf.connection["dbname"],
            self.serviceconf.connection["host"],
            self.serviceconf.connection["port"]
        ).execute(sql,pars)
        
        self.setMessage("Offering member successfully removed")
        
        
        

class waMemberslist(waProcedures):
    """
    class to handle SOS offerings objects, support only GET method
    """
    def executeGet(self):
        if self.service == "default":
            raise Exception("offerings operation can not be done for 'default' service instance.")
        else:
            dbm = databaseManager.PgDB(self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port']
            )
            data = []
            procs = utils.getProcedureNamesList(dbm,self.service,self.offering)
            for proc in procs:
                elem = {}
                elem["name"] = proc["name"]
                ops = utils.getObservedPropertiesFromProcedure(dbm,self.service,proc["name"])
                if ops != None:
                    elem["observedproperties"] = [ {"name": op["name"], "uom": op["uom"], "def": op["def"]} for op in ops ]
                else:
                    elem["observedproperties"] = []
                offs = utils.getOfferingsFromProcedure(dbm,self.service,proc["name"])
                if offs != None:
                    elem["offerings"] = [ off["name"] for off in offs ]
                else:
                    elem["offerings"] = []
                data.append(elem)
            self.setData(data)
            self.setMessage("Offerings names of service <%s> successfully retrived" % self.service)
            
class waNonmemberslist(waProcedures):
    """
    class to handle SOS offerings objects, support only GET method
    """
    def executeGet(self):
        if self.service == "default":
            raise Exception("offerings operation can not be done for 'default' service instance.")
        else:            
            sql  = """
                SELECT 	id_prc, name_prc, desc_prc 
                FROM 	%s.procedures
                WHERE 	NOT EXISTS
	                (
	                SELECT 	id_prc_fk
	                FROM 	%s.off_proc, %s.offerings""" %((self.service,)*3)
            sql += """ 
	                WHERE	id_off = id_off_fk
	                AND	id_prc_fk = id_prc
	                AND	name_off = %s
	                )
                ORDER BY 
	                name_prc;"""
                
            rows = databaseManager.PgDB(self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port']
            ).select(sql,(self.offering,))
            
            if rows:
                self.setMessage("Non members procedures list of service %s, offering %s successfully retrived" % (self.service,self.offering))
                self.setData( [
                    {
                        "id": row["id_prc"], 
                        "name": row["name_prc"], 
                        "description": row["desc_prc"]
                    } for row in rows
                ])
            else:
                self.setData([])
                self.setMessage("Non members procedures list of service %s, offering %s is empty" % (self.service,self.offering))
            
               
        
