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
import sys, os

from istsoslib import sosException
from lib.etree import et
import uuid

class RegisterSensorResponse:
    #Register sensor object
    #self.assignedObservationId
    def __init__(self,filter,pgdb):

        #-----------------------------
        # transaction: insert procedure in DB
        #-----------------------------

        #--check if proc_name exist
        prc_name=None
        sqlId  = "SELECT name_prc FROM %s.procedures" %(filter.sosConfig.schema)
        sqlId += " WHERE name_prc=%s"
        params = (str(filter.procedure),)
        try:
            prc_name = pgdb.select(sqlId,params)
        except:
            raise Exception("SQL: %s"%(pgdb.mogrify(sqlId,params)))
        if prc_name:
            raise Exception("Procedure '%s' already exist, consider to change the name" %(prc_name))

        #--get id_foi or create it if it does not exist yet
        sqlId  = "SELECT id_foi FROM %s.foi" %(filter.sosConfig.schema)
        sqlId += " WHERE name_foi=%s"
        params=(str(filter.foiName),)
        try:
            id_foi= pgdb.select(sqlId,params)[0]["id_foi"]
        except:
            sqlId  = "SELECT id_fty FROM %s.feature_type" %(filter.sosConfig.schema)
            sqlId += " WHERE name_fty=%s"
            params = (str(filter.foiType),)
            try:
                id_fty= pgdb.select(sqlId,params)[0]["id_fty"]
            except:
                sqlIns  = "INSERT INTO %s.feature_type (name_fty)" %(filter.sosConfig.schema)
                sqlIns += " VALUES (%s) RETURNING id_fty"
                params = (str(filter.foiType),)
                try:
                    id_fty= pgdb.executeInTransaction(sqlIns,params)[0]["id_fty"]
                except:
                    raise Exception("SQL: %s"%(sqlIns))

            sqlIns  = "INSERT INTO %s.foi (name_foi,desc_foi,geom_foi,id_fty_fk)" %(filter.sosConfig.schema)
            sqlIns += " VALUES (%s,%s,st_transform(ST_GeomFromGML(%s),%s),%s) RETURNING id_foi"
            params = (str(filter.foiName),str(filter.foiDesc),str(filter.foiGML.strip()),int(filter.sosConfig.istsosepsg),int(id_fty))
            try:
                id_foi = pgdb.executeInTransaction(sqlIns,params)[0]["id_foi"]
                com=True
            except:
                raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))

#==============================================================================
#         #--get id_tru or create it if it does not exist yet
#         sqlId  = "SELECT id_tru FROM %s.time_res_unit" %(filter.sosConfig.schema)
#         sqlId += " WHERE name_tru=%s"
#         params = (filter.time_res_unit,)
#         try:
#             id_tru = pgdb.select(sqlId,params)[0]["id_tru"]
#         except:
#             sqlIns  = "INSERT INTO %s.time_res_unit (name_tru)" %(filter.sosConfig.schema)
#             sqlIns += " VALUES (%s) RETURNING id_tru"
#             params = (str(filter.time_res_unit),)
#             try:
#                 id_tru = pgdb.executeInTransaction(sqlIns,params)[0]["id_tru"]
#                 com=True
#             except:
#                 raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))
#==============================================================================

        #--get a list of observed properties id (id_opr) and check if
        # the fileds of the <Result> data record description
        # are found in the components listed in the <observedProperty>
        # or create them if they do not exist yet
        opr_ids=[]
        for index, par in enumerate(filter.parameters):
            #--insitu-fixed-point (this is the default if no system type defined in XML request)
            if filter.systemType=='insitu-fixed-point' or filter.systemType == None or filter.systemType =="virtual":
                oty = 'virtual' if filter.systemType =="virtual" else 'insitu-fixed-point'
                if not par.split(":")[-1]=="iso8601":
                    if par in filter.oprDef:
                        i = filter.oprDef.index(par)
                        oprDef = par
                        oprName = filter.names[i]
                        #oprDesc = filter.oprDesc[i]
                    else:
                        raise Exception("Field %s not found in Components %s"%(par,filter.oprDef))
                    sqlId  = "SELECT id_opr FROM %s.observed_properties" %(filter.sosConfig.schema)
                    sqlId += " WHERE def_opr=%s"
                    params = (str(oprDef),)
                    try:
                        id_opr = pgdb.select(sqlId,params)[0]["id_opr"]
                        opr_ids.append(id_opr)
                    except:
                        sqlIns  = "INSERT INTO %s.observed_properties (name_opr,def_opr)" %(filter.sosConfig.schema)
                        sqlIns += " VALUES (%s,%s) RETURNING id_opr"
                        params = (str(oprName),str(oprDef))
                        #sqlIns  = "INSERT INTO %s.observed_properties (name_opr,desc_opr,def_opr)" %(filter.sosConfig.schema)
                        #sqlIns += " VALUES (%s,%s,%s) RETURNING id_opr"
                        #params = (str(oprName),str(oprDesc),str(oprDef))
                        try:
                            id_opr = pgdb.executeInTransaction(sqlIns,params)[0]["id_opr"]
                            com=True
                            opr_ids.append(id_opr)
                        except:
                            raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))
            #--virtual

            #--insitu-mobile-point
            elif filter.systemType=='insitu-mobile-point':
                oty = 'insitu-mobile-point'
                if not (par.split(":")[-1] in filter.sosConfig.parGeom["x"] or par.split(":")[-1] in filter.sosConfig.parGeom["y"]
                   or par.split(":")[-1] in filter.sosConfig.parGeom["z"] or par.split(":")[-1]=="iso8601"):
                    if par in filter.oprDef:
                        i = filter.oprDef.index(par)
                        oprDef = par
                        oprName = filter.names[i]
                        #oprDesc = filter.oprDesc[i]
                    else:
                        raise Exception("Field %s not found in Components %s"%(par,filter.oprDef))
                    sqlId  = "SELECT id_opr FROM %s.observed_properties" %(filter.sosConfig.schema)
                    sqlId += " WHERE def_opr=%s"
                    params = (str(oprDef),)
                    try:
                        id_opr = pgdb.select(sqlId,params)[0]["id_opr"]
                        opr_ids.append(id_opr)
                    except:
                        sqlIns  = "INSERT INTO %s.observed_properties (name_opr,def_opr)" %(filter.sosConfig.schema)
                        sqlIns += " VALUES (%s,%s) RETURNING id_opr"
                        params = (str(oprName),str(oprDef))
                        try:
                            id_opr = pgdb.executeInTransaction(sqlIns,params)[0]["id_opr"]
                            com=True
                            opr_ids.append(id_opr)
                        except:
                            raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))
            else:
                raise Exception("Error: observation type not supported")

        #-- get id_oty or create it if it does not exist yet
        sqlId  = "SELECT id_oty FROM %s.obs_type" %(filter.sosConfig.schema)
        sqlId += " WHERE name_oty=%s"
        params = (str(oty),)
        try:
            id_oty = pgdb.select(sqlId,params)[0]["id_oty"]
        except:
            sqlIns  = "INSERT INTO %s.obs_type (name_oty,desc_oty)" %(filter.sosConfig.schema)
            sqlIns += " VALUES (%s,%s) RETURNING id_oty"
            params = (str(oty),None)
            try:
                id_oty = pgdb.executeInTransaction(sqlIns,params)[0]["id_oty"]
                com=True
            except:
                raise Exception("SQL: %s"%(sqlIns))

        #--get id_uom or create it if it does not exist yet
        uom_ids=[]
        #for uom in filter.uoms:
        for i, uom in enumerate(filter.uoms):
            par = filter.parameters[i]
            if oty=='insitu-fixed-point' or oty=='virtual':
                if not par.split(":")[-1]=="iso8601":
                    sqlId  = "SELECT id_uom FROM %s.uoms" %(filter.sosConfig.schema)
                    sqlId += " WHERE name_uom=%s"
                    params = (uom,)
                    try:
                        id_uom = pgdb.select(sqlId,params)[0]["id_uom"]
                        uom_ids.append(id_uom)
                    except:
                        sqlIns  = "INSERT INTO %s.uoms (name_uom,desc_uom)" %(filter.sosConfig.schema)
                        sqlIns += " VALUES (%s,%s) RETURNING id_uom"
                        params = (uom,None)
                        try:
                            id_uom = pgdb.executeInTransaction(sqlIns,params)[0]["id_uom"]
                            com=True
                            uom_ids.append(id_uom)
                        except:
                            raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))
            elif oty == 'insitu-mobile-point':
                if not (par.split(":")[-1] in filter.sosConfig.parGeom["x"] or par.split(":")[-1] in filter.sosConfig.parGeom["y"]
                   or par.split(":")[-1] in filter.sosConfig.parGeom["z"] or par.split(":")[-1]=="iso8601") :
                    sqlId  = "SELECT id_uom FROM %s.uoms" %(filter.sosConfig.schema)
                    sqlId += " WHERE name_uom=%s"
                    params = (uom,)
                    try:
                        id_uom = pgdb.select(sqlId,params)[0]["id_uom"]
                        uom_ids.append(id_uom)
                    except:
                        sqlIns  = "INSERT INTO %s.uoms (name_uom,desc_uom)" %(filter.sosConfig.schema)
                        sqlIns += " VALUES (%s,%s) RETURNING id_uom"
                        params = (uom,None)
                        try:
                            id_uom = pgdb.executeInTransaction(sqlIns,params)[0]["id_uom"]
                            com=True
                            uom_ids.append(id_uom)
                        except:
                            raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))

            else:
                raise Exception("Error: observation type not supported")

        #--get temporary id_off or create it if it does not exist yet
        sqlId  = "SELECT id_off FROM %s.offerings WHERE" %(filter.sosConfig.schema)
        sqlId += " name_off='temporary'"
        try:
            id_off = pgdb.select(sqlId)[0]["id_off"]
        except:
            sqlIns ="INSERT INTO %s.offerings (name_off,desc_off) VALUES" %(filter.sosConfig.schema)
            sqlIns += " ('temporary','temporary offering to hold self-registered procedures/sensors waiting for service adimistration acceptance') RETURNING id_off"
            try:
                id_off = pgdb.executeInTransaction(sqlIns)[0]["id_off"]
                com=True
            except:
                raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns)))

        #--insert procedure
        sqlIns  = "INSERT INTO %s.procedures (id_foi_fk, id_oty_fk, " %(filter.sosConfig.schema)
        sqlIns  += "name_prc, desc_prc, "
        sqlIns  += "stime_prc, etime_prc, "
        sqlIns  += "time_res_prc, time_acq_prc, assignedid_prc)"

        sqlIns += " VALUES (%s, %s, %s, "
        sqlIns += "%s, "
        params = [id_foi,id_oty,str(filter.procedure), str(filter.proc_desc)]
        if not filter.beginPosition=='NULL':
            sqlIns += "%s::TIMESTAMPTZ , %s::TIMESTAMPTZ, "
            params.extend([str(filter.beginPosition),str(filter.beginPosition)])
        else:
            sqlIns += "%s , %s, "
            params.extend([None,None])
        sqlIns += " %s, %s, %s )" #(select(md5(current_timestamp::text))))" >> removed because of conflicts with pgpool replication
        params.append(filter.time_sam_val)
        params.append(filter.time_acq_val)
        # Creating unique id python side avoiding pgpool replication conflict (GSOC 2015)
        params.append(str(uuid.uuid1()).replace("-",""))
        sqlIns += " RETURNING id_prc, assignedid_prc"
        params = tuple([None if x=='NULL' else x for x in params])
        try:
            ret_prc = pgdb.executeInTransaction(sqlIns,params)[0]
            com=True
        except:
            raise Exception("SQL: %s"%(pgdb.mogrify(sqlIns,params)))

        #--link proc_obs
        sqlIns  = "INSERT INTO %s.proc_obs (id_prc_fk, id_uom_fk, id_opr_fk, constr_pro) VALUES " % (
            filter.sosConfig.schema
        )

        params=[]

        #print >> sys.stderr, "opr_ids: %s" % opr_ids
        #print >> sys.stderr, "ret_prc: %s" % ret_prc
        #print >> sys.stderr, "uom_ids: %s" % uom_ids
        #print >> sys.stderr, "opr_ids: %s" % opr_ids
        #print >> sys.stderr, "filter.constr: %s" % filter.constr

        for i in range(len(opr_ids)):
            params.append((
                ret_prc["id_prc"],
                uom_ids[i],
                opr_ids[i],
                filter.constr[i]
            ))
        sqlIns += ",".join(["%s"]*len(params))
        sqlIns += " RETURNING id_pro"
        try:
            res = pgdb.executeInTransaction(sqlIns,params)
            com=True
        except:
            raise Exception("SQL: %s" %(pgdb.mogrify(sqlIns,params)))

        #--link off_prc
        sqlIns  = "INSERT INTO %s.off_proc (id_off_fk, id_prc_fk)" %(filter.sosConfig.schema)
        sqlIns  += " VALUES (%s,%s) RETURNING id_off_prc"
        params = (id_off, ret_prc["id_prc"])
        try:
            res = pgdb.executeInTransaction(sqlIns,params)
            com=True
        except:
            raise Exception("SQL: %s" %(pgdb.mogrify(sqlIns,params)))

        self.assignedSensorId = filter.sosConfig.urn["sensor"]+ret_prc["assignedid_prc"]

        #----------------------------------------
        # create SensorML for inserted procedure
        #----------------------------------------

        f = open(os.path.join(filter.sosConfig.sensorMLpath,filter.procedure + ".xml"), 'w')

        ns = {
            'xsi': "http://www.w3.org/2001/XMLSchema-instance" ,
            'sml': "http://www.opengis.net/sensorML/1.0.1",
            'swe': "http://www.opengis.net/swe/1.0.1",
            'xlink': "http://www.w3.org/1999/xlink",
            'gml': 'http://www.opengis.net/gml'
        }

        #---map namespaces---
        try:
            register_namespace = et.register_namespace
            for key in ns:
                register_namespace(key,ns[key])
        except AttributeError:
            try:
                et._namespace_map.update(ns)
                for key in ns:
                    et._namespace_map[ns[key]] = key
            except AttributeError:
                try:
                    from xml.etree.ElementTree import _namespace_map
                except ImportError:
                    try:
                        from elementtree.ElementTree import _namespace_map
                    except ImportError:
                        print >> sys.stderr, ("Failed to import ElementTree from any known place")
                for key in ns:
                    _namespace_map[ns[key]] = key

        tree = et.ElementTree(filter.xmlSensorDescription)
        tree.write(f, encoding="UTF-8")

        #-----------------------------------------------------------
        # create virtual procedure folder if system type is virtual
        #-----------------------------------------------------------
        if oty == "virtual":
            procedureFolder = os.path.join(filter.sosConfig.virtual_processes_folder, filter.procedure)
            if not os.path.exists(procedureFolder):
                os.makedirs(procedureFolder)


        """
        xml_pre = ""<SensorML xmlns:sml="http://www.opengis.net/sensorML/1.0.1"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:swe="http://www.opengis.net/swe/1.0.1"
            xmlns:gml="http://www.opengis.net/gml"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            xmlns:dlm="http://www.ist.supsi.ch/dataloggerMD/1.0"
            xsi:schemaLocation="http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd"
            version="1.0.1">
            <member xlink:arcrole="urn:ogc:def:process:OGC:detector">""

        #xml_ascii = filter.xmlSensorDescription.toxml().encode('ascii','ignore')

        xml_ascii = filter.xmlSensorDescription

        xml_post = "  </member>\n</SensorML>"
        """

        #Register the transactional operation in Log table
        if filter.sosConfig.transactional_log in ['True','true',1]:
            sqlLog  = "INSERT INTO %s.tran_log (operation_trl,procedure_trl)" %(filter.sosConfig.schema)
            sqlLog  += " VALUES ('RegisterSensor',%s)"
            params = (str(filter.procedure),)
            try:
                pgdb.executeInTransaction(sqlLog,params)
                com=True
            except:
                raise Exception("SQL: %s" %(pgdb.mogrify(sqlLog,params)))

        if com==True:
            pgdb.commitTransaction()

        #f.write(xml_pre + xml_ascii + xml_post)
        f.close()




