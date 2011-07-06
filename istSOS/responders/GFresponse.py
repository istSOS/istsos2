# istSOS Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
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


import psycopg2 # @TODO the right library
import psycopg2.extras
import os
import sys

import sosConfig
from istSOS import sosDatabase
#from SOS.config import mimetype
from istSOS import sosException
#from mx import DateTime
import mx.DateTime.ISO
           
class foi:
    def __init__(self,filter,pgdb):
        sys.stderr.write("*****************************************************************33")
        self.name=filter.featureOfInterest
        self.type=""
        self.desc=""
        self.procedures=[]
        self.idPrc=[]
        self.obsType=[]
        self.samplingTime=[]
        self.properties=[]
        self.geom=""
        
        #select foi
        sql  = "SELECT id_foi, name_foi, desc_foi, ST_AsGml(ST_Transform(geom_foi,%s)) as geom, name_fty" %(filter.srsName)
        sql += " FROM %s.foi, %s.feature_type" %(sosConfig.schema,sosConfig.schema)
        sql += " WHERE id_fty_fk=id_fty AND name_foi='%s'" %(filter.featureOfInterest)
        
        try:
            foi = pgdb.select(sql)[0]
        except:
            raise sosException.SOSException(3,"GFresponse: Feature of Interest '%s' not found."%(filter.featureOfInterest))
        
        self.name=foi["name_foi"]
        self.desc=foi["desc_foi"]
        self.type=foi["name_fty"]
        self.geom=foi["geom"]
        
        #select procedures
        sql  = "SELECT id_prc, name_prc, name_oty "
        sql += "FROM %s.procedures, %s.foi, %s.obs_type " %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
        sql += "WHERE id_foi_fk=id_foi AND id_oty=id_oty_fk AND name_foi='%s' " %(filter.featureOfInterest)
        sql += "ORDER BY name_prc " 
        
        try:
            prc = pgdb.select(sql)
        except:
            raise sosException.SOSException(3,"GFresponse, SQL: %s"%(sql))        
        
        for p in prc:
            self.procedures.append(p["name_prc"])
            self.obsType.append(p["name_oty"])
            self.idPrc.append(p["id_prc"])
            # select obesrved properties of aa given procedure
            sql = "SELECT name_opr "
            sql += " FROM %s.procedures, %s.proc_obs, %s.observed_properties" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
            sql += " WHERE id_prc=id_prc_fk AND id_opr=id_opr_fk AND name_prc='%s'" %(p["name_prc"])
            sql += " ORDER BY name_opr" 
            try:
                obs = pgdb.select(sql)
            except:
                raise sosException.SOSException(3,"GFresponse, SQL: %s"%(sql))    
            obsArr = []
            for o in obs:
                obsArr.append(o['name_opr'])       
            self.properties.append(obsArr)
            
            sql = "SELECT MIN(time_eti) as firstet, MAX(time_eti) as lastet FROM %s.event_time " %(sosConfig.schema)
            sql += "WHERE id_prc_fk = %s GROUP BY id_prc_fk" % (p["id_prc"])
            try:
                samplTime = pgdb.select(sql)
            except:
                raise sosException.SOSException(3,"GFresponse, SQL: %s"%(sql))    
            samplTimeArr = []
            for st in samplTime:
                samplTimeArr.append([st['firstet'],st['lastet']])
            self.samplingTime.append(samplTimeArr)
            
        
        
        
        
        
        
        
