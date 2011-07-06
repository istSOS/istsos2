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

import sosConfig
from istSOS import sosDatabase
from istSOS import sosException
#from mx import DateTime
import mx.DateTime.ISO
import isodate as iso

def get_name_from_urn(stringa,urnName):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1:
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise sosException.SOSException(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name 

def get_urn_from_name(name,urnName):
    return sosConfig.urn[urnName] + name

class RegisterSensorResponse:
    #Register sensor object
    #self.assignedObservationId
    def __init__(self,filter,pgdb):
        
        #-----------------------------
        # trnsaction: insert procedure in DB
        #-----------------------------
                
        #--check if proc_name exist
        prc_name=None
        sqlId = "SELECT name_prc FROM %s.procedures WHERE name_prc='%s'" %(sosConfig.schema,filter.procedure)
        try:
            prc_name = pgdb.select(sqlId)[0]["name_prc"]
        except:
            pass
        
        if prc_name:
            raise sosException.SOSException(1,"Procedure '%s' already exist, consider to change the name"%(prc_name))
        
        #--get id_foi
        sqlId = "SELECT id_foi FROM %s.foi WHERE name_foi='%s'" %(sosConfig.schema,filter.foiName)
        try:
            id_foi= pgdb.select(sqlId)[0]["id_foi"]
        except:
            sqlId = "SELECT id_fty FROM %s.feature_type WHERE name_fty='%s'" %(sosConfig.schema,filter.foiType)
            try:
                id_fty= pgdb.select(sqlId)[0]["id_fty"]
            except:
                sqlIns ="INSERT INTO %s.feature_type (name_fty) VALUES ('%s') RETURNING id_fty" %(sosConfig.schema,filter.foiType)
                try:
                    id_fty= pgdb.executeInThread(sqlIns)[0]["id_fty"]
                except:
                    raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
            sqlIns  = "INSERT INTO %s.foi (name_foi,desc_foi,geom_foi,id_fty_fk)" %(sosConfig.schema)
            sqlIns += " VALUES ('%s','%s',st_transform(st_geomfromewkt('SRID=%s;%s'),%s),%s) RETURNING id_foi" %(filter.foiName,filter.foiDesc,filter.foiSRS,filter.foiWKT,sosConfig.istSOSepsg,id_fty)
            try:
                id_foi = pgdb.executeInThread(sqlIns)[0]["id_foi"]
                com=True
            except:
                raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        #--get id_tru
        sqlId = "SELECT id_tru FROM %s.time_res_unit WHERE name_tru='%s'" %(sosConfig.schema,filter.time_res_unit)
        try:
            id_tru = pgdb.select(sqlId)[0]["id_tru"]
        except:
            sqlIns ="INSERT INTO %s.time_res_unit (name_tru) VALUES ('%s') RETURNING id_tru" %(sosConfig.schema,filter.time_res_unit)
            try:
                id_tru = pgdb.executeInThread(sqlIns)[0]["id_tru"]
                com=True
            except:
                raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        #--get id_opr
        opr_ids=[]
        for par in filter.parameters:
            
            if not par.split(":")[-1]=="iso8601" and not (par.split(":")[-1] in sosConfig.parGeom["x"]) and not (par.split(":")[-1] in sosConfig.parGeom["y"]) and not (par.split(":")[-1] in sosConfig.parGeom["z"]):
                if par in filter.oprName:
                    i = filter.oprName.index(par)
                    oprName = par
                    oprDesc = filter.oprDesc[i]
                else:
                    oprName = par
                    oprDesc = "NULL"
                
                sqlId = "SELECT id_opr FROM %s.observed_properties WHERE name_opr='%s'" %(sosConfig.schema,oprName)
                try:
                    id_opr = pgdb.select(sqlId)[0]["id_opr"]
                    opr_ids.append(id_opr)
                except:
                    sqlIns ="INSERT INTO %s.observed_properties (name_opr,desc_opr) VALUES ('%s','%s') RETURNING id_opr" %(sosConfig.schema,oprName,oprDesc)
                    try:
                        id_opr = pgdb.executeInThread(sqlIns)[0]["id_opr"]
                        com=True
                        opr_ids.append(id_opr)
                    except:
                        raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        #-- get id_oty
        for par in filter.parameters:
            if par.split(":")[-1] in sosConfig.parGeom["x"] or par.split(":")[-1] in sosConfig.parGeom["y"] or par.split(":")[-1] in sosConfig.parGeom["z"]:
                obs_type = "mobilepoint"
                break
            else:
                obs_type = "fixpoint"
        
        sqlId = "SELECT id_oty FROM %s.obs_type WHERE name_oty='%s'" %(sosConfig.schema,obs_type)
        try:
            id_oty = pgdb.select(sqlId)[0]["id_oty"]
        except:
            sqlIns ="INSERT INTO %s.obs_type (name_oty) VALUES ('%s') RETURNING id_oty" %(sosConfig.schema,obs_type)
            try:
                id_oty = pgdb.executeInThread(sqlIns)[0]["id_oty"]
                com=True
            except:
                raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        #--get id_uom
        uom_ids=[]
        #for uom in filter.uoms:
        for i, uom in enumerate(filter.uoms):
            par = filter.parameters[i]
            if not par.split(":")[-1]=="iso8601" and not (par.split(":")[-1] in sosConfig.parGeom["x"]) and not (par.split(":")[-1] in sosConfig.parGeom["y"]) and not (par.split(":")[-1] in sosConfig.parGeom["z"]):
                sqlId = "SELECT id_uom FROM %s.uoms WHERE name_uom='%s'" %(sosConfig.schema,uom)
                try:
                    id_uom = pgdb.select(sqlId)[0]["id_uom"]
                    uom_ids.append(id_uom)
                except:
                    sqlIns ="INSERT INTO %s.uoms (name_uom,desc_uom) VALUES ('%s',NULL) RETURNING id_uom" %(sosConfig.schema,uom)
                    try:
                        id_uom = pgdb.executeInThread(sqlIns)[0]["id_uom"]
                        com=True
                        uom_ids.append(id_uom)
                    except:
                        raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
                
        #--get id_off
        sqlId = "SELECT id_off FROM %s.offerings WHERE name_off='temporary'" %(sosConfig.schema)
        try:
            id_off = pgdb.select(sqlId)[0]["id_off"]
        except:
            sqlIns ="INSERT INTO %s.offerings (name_off,desc_off) VALUES" %(sosConfig.schema)
            sqlIns += " ('temporary','temporary offering to hold self-registered procedures/sensors waiting for service adimistration acceptance') RETURNING id_off"
            try:
                id_off = pgdb.executeInThread(sqlIns)[0]["id_off"]
                com=True
            except:
                raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
           
        #--insert procedure
        sqlIns  = "INSERT INTO %s.procedures (id_foi_fk, id_oty_fk, id_tru_fk, " %(sosConfig.schema)
        sqlIns  += "name_prc, desc_prc, "
        sqlIns  += "stime_prc, etime_prc, "
        sqlIns  += "time_res_prc, assignedid_prc)" 

        #sqlIns += " VALUES (%s, %s, %s, '%s', NULL, now()::timestamptz, now()::timestamptz, %s,(select(md5(current_timestamp::text)))) RETURNING id_prc, assignedid_prc" %(id_foi,id_oty,id_tru,filter.procedure,filter.time_res_val)
        sqlIns += " VALUES (%s, %s, %s, " %(id_foi,id_oty,id_tru)
        sqlIns += "'%s', '%s', " %(filter.procedure, filter.proc_desc)
        if not filter.beginPosition=='NULL':
            sqlIns += "'%s'::TIMESTAMPTZ , '%s'::TIMESTAMPTZ, "  %(filter.beginPosition,filter.beginPosition)
        else:
            sqlIns += "NULL , NULL, "
        sqlIns += " %s, (select(md5(current_timestamp::text))))" %(filter.time_res_val)
        sqlIns += " RETURNING id_prc, assignedid_prc" 
        try:
            ret_prc = pgdb.executeInThread(sqlIns)[0]
            com=True
        except:
            raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        #--link proc_obs
        sqlIns  = "INSERT INTO %s.proc_obs (id_prc_fk, id_uom_fk, id_opr_fk) VALUES " %(sosConfig.schema)
        sqlVal=[]
        for i in range(len(opr_ids)):
            sqlVal.append(" (%s, %s, %s)" %(ret_prc["id_prc"],uom_ids[i],opr_ids[i]))
        sqlIns += ",".join(sqlVal)
        sqlIns += " RETURNING id_pro"
        try:
            res = pgdb.executeInThread(sqlIns)
            com=True
        except:
            raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        #--link off_prc
        sqlIns  = "INSERT INTO %s.off_proc (id_off_fk, id_prc_fk) VALUES (%s,%s) RETURNING id_off_prc" %(sosConfig.schema,id_off,ret_prc["id_prc"])
        try:
            res = pgdb.executeInThread(sqlIns)
            com=True
        except:
            raise sosException.SOSException(1,"SQL: %s"%(sqlIns))
        
        self.assignedSensorId = sosConfig.urn["sensor"]+ret_prc["assignedid_prc"]
        
        #----------------------------------------
        # create SensorML for inserted procedure
        #----------------------------------------
        
        f = open(sosConfig.sensorMLpath + filter.procedure + ".xml", 'w')
        
        xml_pre = """<SensorML xmlns:sml="http://www.opengis.net/sensorML/1.0.1"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:swe="http://www.opengis.net/swe/1.0.1"
          xmlns:gml="http://www.opengis.net/gml"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          xmlns:dlm="http://www.ist.supsi.ch/dataloggerMD/1.0"
          xsi:schemaLocation="http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd"
          version="1.0.1">
  <member xlink:arcrole="urn:ogc:def:process:OGC:detector">"""
 
        xml_ascii = filter.xmlSensorDescription.toxml().encode('ascii','ignore')
        
        xml_post = "  </member>\n</SensorML>"
        if com==True:
            pgdb.commitThread()
        f.write(xml_pre + xml_ascii + xml_post)
        f.close()
        
        
        
        
