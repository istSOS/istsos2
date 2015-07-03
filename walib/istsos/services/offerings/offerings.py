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
from walib import resource, utils, databaseManager, configManager
from walib.resource import waResourceService
import sys, os
from lib import isodate

class waOfferings(waResourceService):
    """class to handle SOS offerings objects, support GET, POST, PUT and DELETE method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        
        
    def executePost(self,db=True):
        """
        Method for executing a POST requests that initialize a new SOS service
                      
        @note: This method creates a new istSOS offering
        
        The POST must be in Json format with mandatory offering key:
                
        >>> {
                "offering" : "meteorology", 
                "description" : "meteo information"
                "expiration" : "2012-12-30T12:00"
                "active" : "sos_db"
            } 
        """
        servicedb = databaseManager.PgDB(
                        self.serviceconf.connection["user"],
                        self.serviceconf.connection["password"],
                        self.serviceconf.connection["dbname"],
                        self.serviceconf.connection["host"],
                        self.serviceconf.connection["port"]
                        )
        
        #insert new offering in db
        try:
            sql  = "INSERT INTO %s.offerings" % self.service
            sql += " (name_off,desc_off,expiration_off,active_off)"
            sql += " VALUES (%s, %s, %s, %s)"
        
            name = self.json["name"]
            try:
                desc = self.json["description"]
            except:
                desc = None
            try:
                exp = isodate.parse_datetime(self.json["expiration"])
            except:
                exp = None
            try:
                act = self.json["active"]
            except:
                act = False
            
            pars = (name,desc,exp,act)
            
            servicedb.execute(sql,pars)
            self.setMessage("new offering successfully added")            
            
        except Exception as e:
            self.setException("Error in adding new offering: %s" % e)
        

    def executeDelete(self):
        """
        Method for executing a DELETE requests that erase a SOS offering
                          
            @note: This method delete the offering (temporary offering cannot be deleted!)
                
            
            The POST must be in Json format with mandatory service key
                    
            >>> {
                    "service" : "service_name"
                } 
        """
        if self.service == "default":
            raise Exception("offerings DELETE operation can not be done for 'default' service instance.")
            
        
        try:
        
            self.offering = self.pathinfo[(self.pathinfo.index("offerings")+1)]
            
            if self.offering == 'temporary':
                raise Exception("'temporary' offerings cannot be deleted")
            
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection["user"],
                self.serviceconf.connection["password"],
                self.serviceconf.connection["dbname"],
                self.serviceconf.connection["host"],
                self.serviceconf.connection["port"]
            )
                        
            sql  = "DELETE FROM %s.offerings" % self.service
            sql += " WHERE name_off=%s"
            params = (self.offering,)
        
            servicedb.execute(sql,params)
            self.setMessage("offering '%s' successfully deleted")            
            
        except Exception as e:
            self.setException("Error in deleting offering: %s" % e)
        
        
    def executePut(self):
        """
        Method for executing a PUT requests that rename a SOS service
                          
            @note: This method renames:
                1. create a new service folder, 
                2. copy content from old to new service configuration file
                3. rename the databse schema
                4. delete old service files
            
            The POST must be in Json format with mandatory service key
                    
            >>> {
                    "service" : "service_name"
                } 
        """
        
        if self.service == "default":
            raise Exception("offerings PUT operation can not be done for 'default' service instance.")
            
        try:                
            self.offering = self.pathinfo[(self.pathinfo.index("offerings")+1)]
            
            if self.offering == 'temporary' and self.offering != self.json["name"]:
                raise Exception("'temporary' offering name cannot be updated")
                    
            servicedb = databaseManager.PgDB(
                            self.serviceconf.connection["user"],
                            self.serviceconf.connection["password"],
                            self.serviceconf.connection["dbname"],
                            self.serviceconf.connection["host"],
                            self.serviceconf.connection["port"]
                            )
        
            sql  = "UPDATE %s.offerings" % self.service
            sql += " SET name_off = %s, desc_off = %s, expiration_off = %s , active_off = %s "
            sql += " WHERE name_off = %s"
        
            name = self.json["name"]
            desc = self.json["description"]
            
            try:
                exp = isodate.parse_datetime(self.json["expiration"])
            except:
                exp = None
            try:
                act = True if (self.json.has_key("active") and self.json["active"]=='on') else False
            except:
                act = False
            
            pars = (name,desc,exp,act,self.offering)
            
            servicedb.execute(sql,pars)
            self.setMessage("offering successfully updated")
            
        except Exception as e:
            self.setException("Error in updating an offering: %s" % e)
        
    def executeGet(self):
        """
        Method for executing a GET requests that return a list of offerings details
                          
            
            The data is returned in this format:
                    
            >>> {
                    "total": 1,
                    "success": true,
                    "message": "Offerings details data loaded correctly",
                    "data": [
                        {
                            "name": "temporary",
                            "description": "descrizione 1",
                            "procedures": 31,
                            "expiration": "31.01.2012",
                            "active": true
                        },{...}
                    ]
                }
        """
        if self.service == "default":
            raise Exception("offerings operation can not be done for 'default' service instance.")
        else:
            self.setData(utils.getOfferingDetailsList(
                databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
                ),self.service))
            if self.response['total']>0:
                self.setMessage("Offerings of service \"%s\" successfully retrived" % self.service)
            else:
                self.setMessage("There aren't Offerings for service \"%s\"" % self.service)

class waGetlist(waResourceService):
    """
    class to handle SOS offerings objects, support only GET method
    """
        
    def executeGet(self):
        
        if self.service == "default":
            raise Exception("offerings operation can not be done for 'default' service instance.")
        else:
            self.setData(utils.getOfferingNamesList(
                databaseManager.PgDB(self.serviceconf.connection['user'],
                                            self.serviceconf.connection['password'],
                                            self.serviceconf.connection['dbname'],
                                            self.serviceconf.connection['host'],
                                            self.serviceconf.connection['port']
                ),self.service))
            if self.response['total']>0:
                self.setMessage("Offerings names of service \"%s\" successfully retrived" % self.service)
            else:
                self.setMessage("There aren't Offerings for service \"%s\"" % self.service)
            
        
