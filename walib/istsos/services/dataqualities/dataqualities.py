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
from walib import databaseManager
from walib.resource import waResourceService
import traceback

class waDataqualities(waResourceService):
    """class to handle SOS unit of data quality objects, support GET and POST method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.dataquality = int(self.pathinfo[-1]) if not self.pathinfo[-1]=="dataqualities" else None

    def executeGet(self):
        """
        Method for executing a GET requests that remove an existing SOS data quality
        
            .. note:: The GET must include code in the URL
            
            >>> http://localhost/istsos/wa/istsos/services/demo/dataqualities/1000
        
        """
        
        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
            
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
                
            if self.dataquality:
                sql = """ 
                SELECT 
                  id_qi as code,
                  name_qi as name, 
                  COALESCE(desc_qi,'') as description
                FROM 
                  %s.quality_index """ % (self.service)
                sql += """WHERE id_qi = %s
                GROUP BY id_qi, name_qi, desc_qi
                ORDER BY 1"""
                par = (self.dataquality,)
                res = servicedb.select(sql,par)
                data = []
                if len(res)>0:
                    for i in range(0,len(res)):
                        procs = []
                        data.append(
                            {
                                "code": res[i]['code'],
                                "name": res[i]['name'],
                                "description" : res[i]['description']
                            }
                        )
                    self.setMessage("Data qualities of service <%s> successfully retrived" % self.service)
                else:
                    self.setMessage("There are not yet any data qualities in the %s database" % self.service)
                self.setData(data)
            else:     
                sql = """ 
                SELECT 
                  id_qi as code,
                  name_qi as name, 
                  COALESCE(desc_qi,'') as description
                FROM 
                  %s.quality_index 
                GROUP BY id_qi, name_qi, desc_qi
                ORDER BY 1""" % (self.service)
                
                res = servicedb.select(sql)
                data = []
                if len(res)>0:
                    for i in range(0,len(res)):
                        procs = []
                        data.append(
                            {
                                "code": res[i]['code'],
                                "name": res[i]['name'],
                                "description" : res[i]['description']
                            }
                        )
                    self.setMessage("Data qualities of service <%s> successfully retrived" % self.service)
                else:
                    self.setMessage("There are not yet any data qualities in the %s database" % self.service)
                self.setData(data)
            
    def executePost(self):
        """
        Method for executing a POST requests that create a new SOS data quality
        
            .. note:: The POST must be in Json format with mandatory code, name and description keys
                
            >>> http://localhost/istsos/wa/istsos/services/demo/dataqualities
                    
            >>> {
                    "code": 100,
                    "name": "raw",
                    "description": "the format is correct"
                }
                  
        """
        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])            
            sql = "INSERT INTO %s.quality_index(id_qi, name_qi, desc_qi)" % self.service
            sql += " VALUES (%s, %s, %s);"
            par = (self.json['code'], self.json['name'],self.json['description'])
            servicedb.execute(sql,par)
            self.setMessage("")
            
    def executePut(self):
        """
        Method for executing a PUT requests that updates an existing SOS data quality
        
            .. note:: The PUT must be in Json format with mandatory name and description keys
            
            >>> http://localhost/istsos/wa/istsos/services/demo/dataqualities/1000
                    
            >>> {
			        "name": "raw",
			        "description": "the format is correct"
		        }
        """
        if self.service == "default":
            raise Exception("observedproperties operation can not be done for default service instance.")
        elif self.dataquality == None:
            raise Exception("destination quality index code is not specified.")
        else:
            #--check if quality index exists
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
            sql = "SELECT id_qi FROM %s.quality_index" % self.service
            sql +=  " WHERE  id_qi = %s"
            par = (self.dataquality,)
            row = servicedb.select(sql, par)
            if not row:
                raise Exception("Quality index '%s' does not exist." % self.dataquality)
            oid = row[0]["id_qi"] 
            sql = "UPDATE %s.quality_index " % self.service
            sql += "SET name_qi = %s, desc_qi=%s"
            sql += " WHERE id_qi = %s"
            par = (self.json['name'],self.json['description'],oid)
            servicedb.execute(sql,par)
            #--update quality index code if provided
            if self.json['code'] and not self.json['code']==self.dataquality:
                sql  = "UPDATE %s.quality_index" % self.service
                sql += " SET id_qi = %s"
                sql += " WHERE id_qi = %s"
                par = (self.json['code'],self.dataquality)
                servicedb.execute(sql,par)
            self.setMessage("Quality Index successfully updated")
        
        
    def executeDelete(self):
        """
        Method for executing a DELETE requests that remove an existing SOS data quality
        
            .. note:: The DELETE must include code in the URL
            
            >>> http://localhost/istsos/wa/istsos/services/demo/dataqualities/1000
        
        """
        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
        elif self.dataquality == None:
            raise Exception("destination quality index code has to be specified.")
        else:
            #--check if quality index exists
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
            sql  = "SELECT id_qi FROM %s.quality_index" %(self.service)
            sql += " WHERE id_qi = %s"
            par = (self.dataquality,)
            row = servicedb.select(sql, par)
            if not row:
                raise Exception("'%s' Quality index code does not exist." % self.dataquality)
            oid = row[0]["id_qi"]
            #--check if quality index is in use
            sql  = "SELECT id_msr FROM %s.measures" %(self.service)
            sql += " WHERE id_qi_fk=%s LIMIT 1"
            use = servicedb.select(sql, (oid,))
            if use:
                raise Exception("'%s' Quality index code is in use." % self.dataquality)
            #--erase quality index code
            sql = "DELETE FROM %s.quality_index " % self.service
            sql += " WHERE id_qi = %s;"
            par = (oid,)
            servicedb.execute(sql,par)
            self.setMessage("Quality index successfully deleted")
            
            
            
            
            
            
            
            
            
            
            
            
        
