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

from walib import procedure, resource, utils, databaseManager, configManager
from walib.resource import waResourceService
import sys, os, shutil, errno
from walib.resource import waResourceConfigurator, waResourceService
import traceback

class waObservedproperties(waResourceService):
    """class to handle SOS service objects, support GET and POST method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        self.observedproperty = self.pathinfo[-1] if not self.pathinfo[-1]=="observedproperties" else None

    def executeGet(self):
        if self.service == "default":
            raise Exception("observedproperties operation can not be done for default service instance.")
        else:
            import json
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
                
            # Loading single observed properties details
            if self.observedproperty:                 
                sql = """ 
                SELECT 
                  name_opr as name, 
                  def_opr as definition, 
                  COALESCE(desc_opr,'') as description, 
                  array_to_string(array_agg(name_prc), ',') as procedures,
                  constr_opr as constraint
                FROM 
                  %s.observed_properties
                LEFT JOIN (
                  SELECT id_opr_fk, name_prc 
                  FROM %s.proc_obs,%s.procedures
                  WHERE id_prc=id_prc_fk
                ) AS b 
                ON id_opr = id_opr_fk """ % ((self.service,)*3)
                sql += """WHERE def_opr = %s
                GROUP BY name_opr, def_opr, desc_opr, constr_opr
                ORDER BY 1""" 
                par = (self.observedproperty,)
                res = servicedb.select(sql,par)
                data = []
                
                if len(res)>0:
                    for i in range(0,len(res)):
                        procs = []
                        if res[i]['procedures']:
                            procs = res[i]['procedures'].split(",")
                        
                        try:
                            constraint = json.loads(res[i]['constraint'])
                        except:
                            constraint = None
                            
                        data.append(
                            {
                                "name": res[i]['name'],
                                "definition": res[i]['definition'],
                                "description" : res[i]['description'],
                                "procedures" : procs,
                                "constraint" : constraint
                            }
                        )
                    self.setMessage("Observed properties of service <%s> successfully retrived" % self.service)
                else:
                    self.setMessage("There are not yet any observed properties in the %s database" % self.service)
                self.setData(data)
            else:
                sql = """ 
                SELECT 
                  name_opr as name, 
                  def_opr as definition, 
                  COALESCE(desc_opr,' ') as description, 
                  array_to_string(array_agg(name_prc), ',') as procedures,
                  constr_opr as constraint
                FROM 
                  %s.observed_properties
                LEFT JOIN (
                  SELECT id_opr_fk, name_prc 
                  FROM %s.proc_obs,%s.procedures
                  WHERE id_prc=id_prc_fk
                ) AS b 
                ON id_opr = id_opr_fk
                GROUP BY name_opr, def_opr, desc_opr, constr_opr
                ORDER BY 1
                """ %((self.service,)*3)
                res = servicedb.select(sql)
                data = []
                if len(res)>0:
                    for i in range(0,len(res)):
                        procs = []
                        if res[i]['procedures']:
                            procs = res[i]['procedures'].split(",")
                            
                        try:
                            constraint = json.loads(res[i]['constraint'])
                        except:
                            constraint = None
                            
                        data.append(
                            {
                                "name": res[i]['name'],
                                "definition": res[i]['definition'],
                                "description" : res[i]['description'],
                                "procedures" : procs,
                                "constraint" : constraint
                            }
                        )
                    self.setMessage("Observed properties of service <%s> successfully retrived" % self.service)
                else:
                    self.setMessage("There are not yet any observed properties in the %s database" % self.service)
                self.setData(data)
            
    
    def executePost(self):
        """
        Method for executing a POST requests that create a new SOS observed property
                  
        """
        if self.service == "default":
            raise Exception("observedproperties operation can not be done for default service instance.")
        else:
            import json
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])        
            
            if self.json['constraint'] == {}:
                sql = "INSERT INTO %s.observed_properties(name_opr, def_opr, desc_opr)" % self.service
                sql += " VALUES (%s, %s, %s);"
                par = (
                    self.json['name'],
                    self.json['definition'],
                    self.json['description']
                )
            else:
                sql = "INSERT INTO %s.observed_properties(name_opr, def_opr, desc_opr, constr_opr)" % self.service
                sql += " VALUES (%s, %s, %s, %s);"
                par = (
                    self.json['name'],
                    self.json['definition'],
                    self.json['description'],
                    json.dumps(self.json['constraint'])
                )


            servicedb.execute(sql,par)
            self.setMessage("")
            
    
    def executePut(self):
        """
        Method for executing a POST requests that create a new SOS observed property
        """
        if self.service == "default":
            raise Exception("observedproperties operation can not be done for default service instance.")
        elif self.observedproperty == None:
            raise Exception("destination observedproperty is not specified.")
        else:
            import json
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
            sql = "SELECT id_opr FROM %s.observed_properties " % self.service
            sql +=  "WHERE  def_opr = %s"
            par = (self.observedproperty,)
            row = servicedb.select(sql, par)
            if not row:
                raise Exception("Original observed property '%s' does not exist." % self.observedproperty)
            oid = row[0]["id_opr"] 
            sql = "UPDATE %s.observed_properties " % self.service
            sql += "SET name_opr = %s, def_opr = %s, desc_opr=%s, constr_opr=%s"
            sql += " WHERE id_opr = %s"
            par = (
                self.json['name'],
                self.json['definition'],
                self.json['description'],
                json.dumps(self.json['constraint']),
                oid
            )
            servicedb.execute(sql,par)
            self.setMessage("Update successfull")
        
        
    def executeDelete(self):
        """
        Method for executing a DELETE requests that remove an existing SOS observed property
                  
        """
        if self.service == "default":
            raise Exception("observedproperties operation can not be done for default service instance.")
        elif self.observedproperty == None:
            raise Exception("destination observedproperty has to be specified.")
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
            sql = """
                SELECT id_opr, COALESCE(procCount,0) as counter
                FROM 
                  %s.observed_properties
                LEFT JOIN (
                  SELECT id_opr_fk, count(id_opr_fk) as procCount
                  FROM %s.proc_obs
                  GROUP BY id_opr_fk
                ) AS b 
                ON id_opr = id_opr_fk """ %((self.service,)*2)
            sql += "WHERE def_opr = %s"
            par = (self.observedproperty,)
            row = servicedb.select(sql, par)
            if not row:
                raise Exception("'%s' observed property does not exist." % self.observedproperty)
            oid = row[0]["id_opr"]
            counter = row[0]["counter"]
            if counter > 0:
                if counter == 1:
                    raise Exception("There is %s procedure connected with '%s' observed property " % (counter,self.observedproperty))
                else:
                    raise Exception("There are %s procedures connected with '%s' observed property " % (counter,self.observedproperty))
            sql = "DELETE FROM %s.observed_properties " % self.service
            sql += " WHERE id_opr = %s;"
            par = (oid,)
            servicedb.execute(sql,par)
            self.setMessage("Observed property is deleted")



