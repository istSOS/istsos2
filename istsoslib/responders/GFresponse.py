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
import psycopg2
import psycopg2.extras
import os
import sys

#import sosConfig
from istsoslib import sosDatabase
#from SOS.config import mimetype
from istsoslib import sosException
from ..utils import escape

class foi:
    """The Feature of interest object

    Attributes:
        name (str): feature of interest name
        type (str): feature of interest type
        desc (str): description of the feature of interest
        procedures (list): ordered list of procedures
        idPrc (list): ordered list of procdures id
        obsType (list): list of observation types
        samplingTime (list): list of eventime elements, one (instant) or two (period) 
        properties (list): list of preperties
        geom (str): the feature of interest geometry as GML
    """
    def __init__(self,filter,pgdb):
        #sys.stderr.write("*****************************************************************")
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
        sql  = f"SELECT id_foi, name_foi, desc_foi, ST_AsGml(ST_Transform(geom_foi,{filter.srsName})) as geom, name_fty"
        sql += " FROM %s.foi, %s.feature_type" %(filter.sosConfig.schema,filter.sosConfig.schema)
        sql += " WHERE id_fty_fk=id_fty AND name_foi=%s" #%(filter.featureOfInterest)
        params = (str(filter.featureOfInterest),)
        try:
            foi = pgdb.select(sql,params)[0]
        except:
            raise sosException.SOSException("InvalidParameterValue","FeatureOfInterestId","FeatureOfInterestId: Feature of Interest '%s' not found."%(filter.featureOfInterest))
        
        self.name=escape(foi["name_foi"])
        self.desc=foi["desc_foi"]
        self.type=foi["name_fty"]
        self.geom=foi["geom"]
        
        #select procedures
        sql  = "SELECT id_prc, name_prc, name_oty "
        sql += "FROM %s.procedures, %s.foi, %s.obs_type " %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sql += "WHERE id_foi_fk=id_foi AND id_oty=id_oty_fk AND name_foi=%s " #%(filter.featureOfInterest)
        sql += "ORDER BY name_prc "
        params = (str(filter.featureOfInterest),)
        try:
            prc = pgdb.select(sql,params)
        except:
            raise Exception("GFresponse, SQL: %s"%(pgdb.mogrify(sql,params)))        
        
        for p in prc:
            self.procedures.append(escape(p["name_prc"]))
            self.obsType.append(p["name_oty"])
            self.idPrc.append(p["id_prc"])
            # select obesrved properties of aa given procedure
            sql = "SELECT name_opr "
            sql += " FROM %s.procedures, %s.proc_obs, %s.observed_properties" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
            sql += " WHERE id_prc=id_prc_fk AND id_opr=id_opr_fk AND name_prc=%s" #%(p["name_prc"])
            sql += " ORDER BY name_opr"
            params = (p["name_prc"],)
            try:
                obs = pgdb.select(sql,params)
            except:
                raise Exception("GFresponse, SQL: %s"%(pgdb.mogrify(sql,params)))    
            obsArr = []
            for o in obs:
                obsArr.append(o['name_opr'])       
            self.properties.append(obsArr)
            
            sql = "SELECT MIN(time_eti) as firstet, MAX(time_eti) as lastet FROM %s.event_time " %(filter.sosConfig.schema)
            sql += "WHERE id_prc_fk = %s GROUP BY id_prc_fk" #% (p["id_prc"])
            params = (p["id_prc"],)
            try:
                samplTime = pgdb.select(sql,params)
            except:
                raise Exception("GFresponse, SQL: %s"%(pgdb.mogrify(sql,params)))    
            samplTimeArr = []
            for st in samplTime:
                samplTimeArr.append([st['firstet'],st['lastet']])
            self.samplingTime.append(samplTimeArr)

        
        
        
        
        
        
        
