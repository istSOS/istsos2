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
from walib import procedure, resource, utils, databaseManager, configManager
from walib.resource import waResourceService
import sys, os, shutil, errno
from walib.resource import waResourceConfigurator, waResourceService
import traceback
import urllib

class waUoms(waResourceService):
    """class to handle SOS unit of measure objects, support GET and POST method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.uoms = urllib.unquote(self.pathinfo[-1]) if not self.pathinfo[-1]=="uoms" else None

    def executeGet(self):
    
        if self.service == "default":
            raise Exception("uoms operation can not be done for default service instance.")
            
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
                
            if self.uoms:                 
                sql = """ 
                SELECT 
                  name_uom as name, 
                  COALESCE(desc_uom,'') as description, 
                  array_to_string(array_agg(name_prc), ',') as procedures 
                FROM 
                  %s.uoms 
                LEFT JOIN (
                  SELECT id_uom_fk, name_prc 
                  FROM %s.proc_obs,%s.procedures 
                  WHERE id_prc=id_prc_fk 
                ) AS b 
                ON id_uom = id_uom_fk """ % ((self.service,)*3)
                sql += """WHERE name_uom = %s
                GROUP BY name_uom, desc_uom
                ORDER BY 1"""
                par = (self.uoms,)
                res = servicedb.select(sql,par)
                data = []
                if len(res)>0:
                    for i in range(0,len(res)):
                        procs = []
                        if res[i]['procedures']:
                            procs = res[i]['procedures'].split(",")
                        data.append(
                            {
                                "name": res[i]['name'],
                                "description" : res[i]['description'],
                                "procedures" : procs
                            }
                        )
                    self.setMessage("Unit of measures of service <%s> successfully retrived" % self.service)
                else:
                    self.setMessage("There are not yet any unit of measures in the %s database" % self.service)
                self.setData(data)
            else:     
                sql = """ 
                SELECT 
                  name_uom as name, 
                  COALESCE(desc_uom,'') as description, 
                  array_to_string(array_agg(name_prc), ',') as procedures 
                FROM 
                  %s.uoms 
                LEFT JOIN (
                  SELECT id_uom_fk, name_prc 
                  FROM %s.proc_obs,%s.procedures 
                  WHERE id_prc=id_prc_fk 
                ) AS b 
                ON id_uom = id_uom_fk 
                GROUP BY name_uom, desc_uom
                ORDER BY 1""" % ((self.service,)*3)
                
                res = servicedb.select(sql)
                data = []
                if len(res)>0:
                    for i in range(0,len(res)):
                        procs = []
                        if res[i]['procedures']:
                            procs = res[i]['procedures'].split(",")
                        data.append(
                            {
                                "name": res[i]['name'],
                                "description" : res[i]['description'],
                                "procedures" : procs
                            }
                        )
                    self.setMessage("Unit of measures of service <%s> successfully retrived" % self.service)
                else:
                    self.setMessage("There are not yet any unit of measures in the %s database" % self.service)
                self.setData(data)
            
    def executePost(self):
        """
        Method for executing a POST requests that create a new SOS observed property
                  
        """
        if self.service == "default":
            raise Exception("uoms operation can not be done for default service instance.")
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])            
            sql = "INSERT INTO %s.uoms(name_uom, desc_uom)" % self.service
            sql += " VALUES (%s, %s);"
            par = (self.json['name'],self.json['description'])
            servicedb.execute(sql,par)
            self.setMessage("")
            
    def executePut(self):
        """
        Method for executing a POST requests that create a new SOS observed property
        """
        if self.service == "default":
            raise Exception("observedproperties operation can not be done for default service instance.")
        elif self.uoms == None:
            raise Exception("destination observedproperty is not specified.")
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
            sql = "SELECT id_uom FROM %s.uoms " % self.service
            sql +=  "WHERE  name_uom = %s"
            par = (self.uoms,)
            row = servicedb.select(sql, par)
            if not row:
                raise Exception("Original Unit of measure '%s' does not exist." % self.uoms)
            oid = row[0]["id_uom"] 
            sql = "UPDATE %s.uoms " % self.service
            sql += "SET name_uom = %s, desc_uom=%s"
            sql += " WHERE id_uom = %s"
            par = (str(self.json['name']),self.json['description'],oid)
            servicedb.execute(sql,par)
            self.setMessage("Update successfull")
        
        
    def executeDelete(self):
        """
        Method for executing a DELETE requests that remove an existing SOS observed property
                  
        """
        if self.service == "default":
            raise Exception("uoms operation can not be done for default service instance.")
        elif self.uoms == None:
            raise Exception("destination Unit of measure has to be specified.")
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
            sql = """
                SELECT id_uom, COALESCE(procCount,0) as counter
                FROM 
                  %s.uoms
                LEFT JOIN (
                  SELECT id_uom_fk, count(id_uom_fk) as procCount
                  FROM %s.proc_obs
                  GROUP BY id_uom_fk
                ) AS b 
                ON id_uom = id_uom_fk """ %((self.service,)*2)
            sql += "WHERE name_uom = %s"
            par = (self.uoms,)
            row = servicedb.select(sql, par)
            if not row:
                raise Exception("'%s' Unit of measure does not exist." % self.uoms)
            oid = row[0]["id_uom"]
            counter = row[0]["counter"]
            if counter > 0:
                raise Exception("There are %s procedures connected with '%s' Unit of measure" % (counter,self.uoms))
            sql = "DELETE FROM %s.uoms " % self.service
            sql += " WHERE id_uom = %s;"
            par = (oid,)
            servicedb.execute(sql,par)
            self.setMessage("Unit of measure is deleted")
        
