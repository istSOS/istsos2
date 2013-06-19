# -*- coding: utf-8 -*-
# istsos Istituto Scienze della Terra Sensor Observation Service
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


#import psycopg2 # @TODO the right library
#import psycopg2.extras
#import os
import sys, pprint #for debug only

#import sosConfig
#from istsoslib import sosDatabase
from istsoslib import sosException
#import mx.DateTime.ISO
from lib import isodate as iso

from datetime import datetime

now = datetime.now()

class InsertObservationResponse:
    #self.assignedObservationId
    def __init__(self,filter,pgdb):
                
        #--get procedure information
        #============================================
        sql  = "SELECT id_prc, name_prc, name_oty, name_foi, stime_prc, etime_prc from %s.procedures,%s.obs_type,%s.foi" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sql += " WHERE id_oty=id_oty_fk AND id_foi=id_foi_fk AND assignedid_prc=%s"
        params = (filter.assignedSensorId,)
        try:
            prc = pgdb.select(sql,params)[0]
        except:
            raise sosException.SOSException(3,"assignedSensorId '%s' is invalid! SQL: %s" %(filter.assignedSensorId,pgdb.mogrify(sql,params)))
        
        print >> sys.stderr, "==PROC INFO=========="
        print >> sys.stderr, pprint.pprint(prc)
                
        #--check requested procedure name exists
        #=============================================
        if not prc["name_prc"]==filter.procedure:
            raise sosException.SOSException(3,"procedure '%s' not associated with provided assignedSensorId!" %(filter.procedure))
        
        #--check requested  foi name exists
        #=============================================
        if not filter.foiName == prc["name_foi"]:
            raise sosException.SOSException(3,"featureOfInterest '%s' not associated with provided assignedSensorId" %(filter.foiName))
        
        #--check provided samplingTime and upadate 
        #  begin/end time procedure if necessary  
        # (samplingTime=period or istant of provided 
        #  observations defined by samplingTime filter)
        #=============================================
        if filter.samplingTime:
            stime = filter.samplingTime.split("/")
            #
            if len(stime)==2: # is a TimePeriod
                start = iso.parse_datetime(stime[0])
                end  = iso.parse_datetime(stime[1])
            elif len(stime)==1: # is a TimeInstant
                start = end = iso.parse_datetime(stime[0])
            else:
                raise sosException.SOSException(3," filter samplingTime error! given '%s'" %(filter.samplingTime))

            if start>end:
                raise sosException.SOSException(3," endPosition (%s) must be after beginPosition (%s)" %(end,start))
            
            #-- check samplingTime
            #==========================================
            # verify procedure begin/end exist
            #-----------------------------------
            if not (prc["stime_prc"].__class__.__name__ == "NoneType" and prc["etime_prc"].__class__.__name__ == "NoneType"):
                
                # check eventTime interval and update begin/end position when force flas is active
                #----------------------------------------------------------------------------------
                if filter.forceInsert:
                    #-- verify interval limits
                    '''if not (end>=prc["stime_prc"] and start<=prc["etime_prc"]):
                        raise sosException.SOSException(3,"observation eventTime (%s-%s) must overlap procedure samplingTime (%s-%s)" %(start,end,prc["stime_prc"],prc["etime_prc"]))
                    else:'''
                    #-- update begin time of procedure
                    if start<prc["stime_prc"]:
                        sql  = "UPDATE %s.procedures" %(filter.sosConfig.schema)
                        sql += " SET stime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s" 
                        params = (stime[0],prc["id_prc"])
                        try:
                            a = pgdb.executeInTransaction(sql,params)
                            com=True
                            print >> sys.stderr, "==FORCE FLAG ON: begin time of procedure updated=========="
                        except:
                            raise sosException.SOSException(3,"SQL: %s" %(pgdb.mogrify(sql,params)))
                    
                    #-- update end time of procedure
                    if end>prc["etime_prc"]:
                        sql  = "UPDATE %s.procedures" %(filter.sosConfig.schema)
                        sql += " SET etime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s" 
                        params = (stime[1],prc["id_prc"])
                        try:
                            b = pgdb.executeInTransaction(sql,params)
                            com=True   
                            print >> sys.stderr, "==FORCE FLAG ON: end time of procedure updated=========="
                        except Exception as err:
                            raise sosException.SOSException(3,"SQL: %s - %s" %(pgdb.mogrify(sql,params), err.pgerror))

                # check eventTime interval and update begin/end position when force flag is off
                #----------------------------------------------------------------------------------                            
                else:
                    sql  = "SELECT max(time_eti) as max_time_eti from %s.event_time" %(filter.sosConfig.schema)
                    sql += " WHERE id_prc_fk = %s group by id_prc_fk" 
                    params = (prc["id_prc"],)
                    try:
                        lastMsr = pgdb.select(sql,params)[0]["max_time_eti"]
                    except:
                        lastMsr = None
                    
                    if lastMsr!=None:
                        #-- verify begin observation is minor/equal then end time procedure and later then last observation
                        if not (end>=prc["etime_prc"] and start<=prc["etime_prc"] and start>=lastMsr):
                            raise sosException.SOSException(3,"begin observation (%s) must be between last observation (%s) and end procedure (%s); end observation (%s) must be after end procedure (%s)" %(start,lastMsr,prc["etime_prc"],end,prc["etime_prc"]))
                    else:
                        #-- verify begin observation is minor/equal then end time procedure and later then first observation
                        if not (end>=prc["etime_prc"] and start<=prc["etime_prc"] and start>=prc["stime_prc"]) :
                            raise sosException.SOSException(3,"begin observation (%s) must be between start procedure (%s) and end procedure (%s); end observation (%s) must be after end procedure (%s)" %(start,prc["stime_prc"],prc["etime_prc"],end,prc["etime_prc"]))
                        
                    #-- update end time of procedure
                    sql  = "UPDATE %s.procedures" %(filter.sosConfig.schema)
                    sql += " SET etime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s" 
                    params = (str(stime[1]),int(prc["id_prc"]))
                    try:
                        b = pgdb.executeInTransaction(sql,params)
                        com=True
                        print >> sys.stderr, "==FORCE FLAG OFF: end time of procedure updated=========="
                    except Exception as err:
                        raise sosException.SOSException(3,"SQL: %s - %s" %(pgdb.mogrify(sql,params), err.pgerror))
            
            else:
                sql  = "UPDATE %s.procedures" %(filter.sosConfig.schema)
                sql += " SET stime_prc=%s::TIMESTAMPTZ, etime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s" 
                params = (str(stime[0]),str(stime[1]),int(prc["id_prc"]))
                try:
                    b = pgdb.executeInTransaction(sql,params)
                    com=True
                    print >> sys.stderr, "==stime & etime NULL: start & end time of procedure updated=========="
                except:
                    raise sosException.SOSException(3,"SQL: %s" %(pgdb.mogrify(sql,params)))
            
        #  check data definition and uom (compare registered 
        #  observed properties with provided observations)
        #==================================================
        # get values for provided data: UOM, NAME, URN, ID
        #--------------------------------------------------
        sql  = "SELECT id_pro, id_opr, def_opr, name_uom, constr_opr, constr_pro FROM %s.observed_properties, %s.proc_obs, %s.uoms" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sql += " WHERE id_uom_fk=id_uom AND id_opr_fk=id_opr AND id_prc_fk=%s" 
        params = (prc["id_prc"],)
        try:
            opr = pgdb.select(sql,params)
            print >> sys.stderr, "==OPR INFO=========="
            print >> sys.stderr, pprint.pprint(opr)
        except Exception as err:
            raise sosException.SOSException(3,"SQL2: %s -%s" %(pgdb.mogrify(sql,params), err.pgerror))
            
        #---- get list of available ObservedProperty, unit of measure, property id for this procedure -----
        oprNames=[]
        oprUoms=[]
        oprIds=[] #to be removed ????
        proIds=[]
        oprCon=[]
        proCon=[]
        for row in opr:
            oprNames.append(row["def_opr"])
            oprUoms.append(row["name_uom"])
            oprIds.append(row["id_opr"])
            
            try:
                cos = row["constr_opr"].split(":")
            except:
                if row["constr_opr"] in [None,'']:
                    cos = [None,None]
                else:
                    raise sosException.SOSException(3,"observed property constrain '%s' malformatted" %(row["constr_opr"]))
            oprCon.append({'mode': cos[0], 'val': cos[1].strip()})
            
            proIds.append(row["id_pro"])
            
            try:
                cos = row["constr_pro"].split(":")
            except:
                if row["constr_pro"] in [None,'']:
                    cos = [None,None]
                else:
                    raise sosException.SOSException(3,"procedure specific constrain '%s' malformatted" %(row["constr_pro"]))
            proCon.append({'mode': cos[0], 'val': cos[1].strip()})
        
        #---- get ordered list of observed properties in data----
        dataKeys = [ key for key in filter.data.keys() ] 
        #dataNames = dataKeys
        ### dataNames = [ key.split(":")[-1] for key in filter.data.keys() ]
        
        #----- get ordered list of unit of measures provided with data-------
        dataUoms = []
        for key in filter.data.keys():
            if "uom" in filter.data[key].keys():
                dataUoms.append(filter.data[key]["uom"])
            else:
                dataUoms.append('None')
                
        #------------------------------------------------------------------  
        # verify that all the properties observed by this procedure
        # are provided with the correct data definition and uom  
        #------------------------------------------------------------------   
        for i,opr in enumerate(oprNames):
            try: 
                k = dataKeys.index(opr)
            except:
                raise sosException.SOSException(3,"parameter '%s' not observed by RegisteredSensor %s - %s" %(opr,oprNames,dataKeys))
            #if not str(dataUoms[k])==str(oprUoms[i]):
            if not dataUoms[k]==oprUoms[i]:
                raise sosException.SOSException(3,"parameter '%s' not observed with provided unit of measure" %(opr))
        
        #---------------------------------------------------------------    
        # verify if time and coordinates are passed as data parameters
        # and create the parameters list and parameters ID
        #--------------------------------------------------------------  
        xobs=None
        yobs=None
        zobs=None
        tpar=None
        pars=[]
        parsId=[]
        parsConsObs=[]
        parsConsPro=[]
        # urn of different parameters
        for i, dn in enumerate(dataKeys):
            if dn.split(":")[-1] in filter.sosConfig.parGeom["x"]:
                xobs = dataKeys[i]
            elif dn.split(":")[-1] in filter.sosConfig.parGeom["y"]:
                yobs = dataKeys[i]
            elif dn.split(":")[-1] in filter.sosConfig.parGeom["z"]:
                zobs = dataKeys[i]
            elif dn.find("iso8601")>=0:
                tpar = dataKeys[i]
            else:
                if not dn.split(":")[-1] == "qualityIndex":
                    #pars.append(dataKeys[i])
                    pars.append(dn)
                    try:
                        print >> sys.stderr, "==PARS=========="
                        print >> sys.stderr, pprint.pprint(proIds)
                        print >> sys.stderr, "-------------------"
                        print >> sys.stderr, pprint.pprint(oprCon)
                        print >> sys.stderr, "-------------------"
                        print >> sys.stderr, pprint.pprint(proCon)
                        #parsId.append(proIds[oprNames.index(dataKeys[i])])
                        parsId.append(proIds[oprNames.index(dn)])
                        parsConsObs.append(oprCon[oprNames.index(dn)])
                        parsConsPro.append(proCon[oprNames.index(dn)])
                    except:
                        raise sosException.SOSException(3,"parameter %s not observed by this sensor %s - %s" %(dn,pars,oprNames))
         
        #----------------------------------------------------------------------------------
        # set default quality index if not provided
        #----------------------------------------------------------------------------------
        for par in pars:
            try:
                kqi = dataKeys.index(par+":qualityIndex")
            except:
                filter.data[par+":qualityIndex"]={"vals":[filter.sosConfig.default_qi]*len(filter.data[par]["vals"])}
                    
        #---------------------------------------------------------------        
        # verify that mobile sensors provide coordinates as X,Y,Z
        #---------------------------------------------------------------
        if (xobs==False and yobs==False and zobs==False) and prc["name_oty"] == "insitu-mobile-point":
            raise sosException.SOSException(3,"Mobile sensors require x,y,z parameters")
        
        #---------------------------------------------------------------
        # verify that time parameter is provided
        #---------------------------------------------------------------
        if not tpar:
            raise sosException.SOSException(3,"parameter 'time:iso8601' is required for InsertObservation")
        
        #---------------------------------------------------------------
        # verify that eventime are in provided samplingTime
        #---------------------------------------------------------------
        if not iso.parse_datetime(max(filter.data[tpar]["vals"]))<= end and iso.parse_datetime(min(filter.data[tpar]["vals"]))>= start:
            print >> sys.stderr, "maxvals=%s,end=%s,minval=%s,start=%s============" %(max(filter.data[tpar]["vals"], end, min(filter.data[tpar]["vals"]), start))
            raise sosException.SOSException(3,"provided data are not included in provided <samplingTime> period")
        
        #======================        
        #-- insert observation
        #======================
        # delete existing observations if force flag is active
        #------------------------------------------------------
        if filter.forceInsert:
            sql  = "DELETE FROM %s.event_time" %(filter.sosConfig.schema)
            sql += " WHERE id_prc_fk=%s AND time_eti>=%s::TIMESTAMPTZ AND time_eti<=%s::TIMESTAMPTZ" 
            params = (prc["id_prc"],stime[0],stime[1])
            try:
                b = pgdb.executeInTransaction(sql,params)
                com=True
            except:
                raise sosException.SOSException(3,"SQL: %s" %(pgdb.mogrify(sql,params)))
        
        #----------------------------------------
        # CASE I: observations list is void
        #----------------------------------------
        if len(filter.data[tpar]["vals"])==0:
            self.assignedId = ""
            
        #----------------------------------------
        # CASE I: observations list contains data
        #----------------------------------------

        elif len(filter.data[tpar]["vals"])>0:
            #--------------------
            # insert event times
            #--------------------            
            params = []
            ids_eti = []
            sql  = "INSERT INTO %s.event_time (id_prc_fk,time_eti)" %(filter.sosConfig.schema)
            sql += " VALUES (%s,%s::TIMESTAMPTZ) RETURNING id_eti" 
            for val in filter.data[tpar]["vals"]:
                try:
                    ids_eti.append(pgdb.executeInTransaction(sql,(prc["id_prc"],val))[0]['id_eti'])
                    com=True
                except Exception as e:
                    raise e
            
            #--------------------
            print >> sys.stderr, "insert par values============"
            print >> sys.stderr, len(ids_eti)
            #--insert par values
            #--------------------     
            
            #TODO
            
            for i, par in enumerate(pars):
                params = []
                ids_msr = []
                sql = "INSERT INTO %s.measures (id_pro_fk, id_eti_fk,id_qi_fk,val_msr) VALUES" %(filter.sosConfig.schema)
                sql += " (%s,%s,%s,%s) RETURNING id_msr"
                #hasvalues = False
                for ii,id_et in enumerate(ids_eti):
                    if not filter.data[par]["vals"][ii] in ['NULL',u'NULL',None,-999,"-999",u"-999",filter.sosConfig.aggregate_nodata]:
                        
                        # quality check level I (gross error) 200
                        #------------------------------------------
                        if filter.sosConfig.correct_qi:
                            if parsConsObs[i]['mode']==u'max':
                                if float(filter.data[par]["vals"][ii]) <= float(parsConsObs[i]['val']):
                                    pqi = int(filter.sosConfig.correct_qi)
                            elif parsConsObs[i]['mode']==u'min':
                                if float(filter.data[par]["vals"][ii]) >= float(parsConsObs[i]['val']):
                                    pqi = int(filter.sosConfig.correct_qi)
                            elif parsConsObs[i]['mode']==u'interval':
                                l = parsConsObs[i]['val'].split(" ")
                                if float(l[0]) <= float(filter.data[par]["vals"][ii]) <= float(l[1]):
                                    pqi = int(filter.sosConfig.correct_qi)
                            elif parsConsObs[i]['mode']==u'valueList':
                                if float(filter.data[par]["vals"][ii]) in [float(p) for p in parsConsObs[i]['val'].split("")]:
                                    pqi = int(filter.sosConfig.correct_qi)
                        
                        # quality check level II (statistical range) 300
                        #-------------------------------------------
                        if filter.sosConfig.stat_qi:
                            if parsConsPro[i]['mode']=='max':
                                if float(filter.data[par]["vals"][ii]) <= float(parsConsPro[i]['val']):
                                    pqi = int(filter.sosConfig.stat_qi)
                            elif parsConsPro[i]['mode']=='min':
                                if float(filter.data[par]["vals"][ii]) >= float(parsConsPro[i]['val']):
                                    pqi = int(filter.sosConfig.stat_qi)
                            elif parsConsPro[i]['mode']=='interval':
                                l = parsConsPro[i]['val'].split(" ")
                                if float(l[0]) <= float(filter.data[par]["vals"][ii]) <= float(l[1]):
                                    pqi = int(filter.sosConfig.stat_qi)
                            elif parsConsPro[i]['mode']=='valueList':
                                if float(filter.data[par]["vals"][ii]) in [float(p) for p in parsConsPro[i]['val'].split("")]:
                                    pqi = int(filter.sosConfig.stat_qi) 
                                    
                        # insert observation
                        #-------------------------------------------     
                        #print >> sys.stderr, "insert par values============"
                        #print >> sys.stderr, "%s %s %s %s" % (parsConsPro[i],parsConsObs[i],pqi,float(filter.data[par]["vals"][ii]))
                        #-------------------------------------------
                        params = (int(parsId[i]),int(id_et),pqi,float(filter.data[par]["vals"][ii]))
                        try:
                            nid_msr = pgdb.executeInTransaction(sql,params)
                            ids_msr.append(str(nid_msr[0]['id_msr']))
                        except Exception as e:
                            com=False
                            raise e
                            raise sosException.SOSException(3,"L: %s - %s - %s - %s") %(int(parsId[i]),int(id_et),pqi,float(filter.data[par]["vals"][ii]))
            
            #-------------------------------------
            #--insert position values if required 
            #-------------------------------------
            if prc["name_oty"] == "insitu-mobile-point":
                xparspl = xobs.split(":")
                epsg = xparspl[xparspl.index("EPSG")+1]
                params = []
                sql = "INSERT INTO %s.positions (id_qi_fk, id_eti_fk,geom_pos) VALUES" %(filter.sosConfig.schema)
                sql += "(%s,%s,ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s, %s), %s), %s))"
                
                for i,id_et in enumerate(ids_eti):
                    params = (filter.sosConfig.default_qi,id_et,filter.data[xobs]["vals"][i],filter.data[yobs]["vals"][i],filter.data[zobs]["vals"][i],epsg,filter.sosConfig.istsosepsg)
                    try:
                        ids_pos = pgdb.executeInTransaction(sql,params)
                        com=True
                    except Exception as a:
                        com=False
                        raise sosException.SOSException(3,"%s\nSQL: %s" %(a,pgdb.mogrify(sql,params)))
            
            # register assigned IDs of measures
            self.assignedId = "@".join([str(p) for p in ids_eti])
            # commit executed operations                
        
         #Register the transactional operation in Log table 
        if filter.sosConfig.transactional_log in ['True','true',1]:
            sqlLog  = "INSERT INTO %s.tran_log" %(filter.sosConfig.schema)
            sqlLog  += " (operation_trl,procedure_trl,begin_trl,end_trl,count,stime_prc,etime_prc)"
            sqlLog  += " VALUES ('InsertObservation', %s, %s::TIMESTAMPTZ, %s::TIMESTAMPTZ, %s, %s::TIMESTAMPTZ , %s::TIMESTAMPTZ)" 
            params = (str(filter.procedure),start,end,len(ids_eti),prc["stime_prc"],prc["etime_prc"])
            try:
                pgdb.executeInTransaction(sqlLog,params)
                com=True
            except:
                raise sosException.SOSException(1,"SQL: %s" %(pgdb.mogrify(sqlLog,params)))
        
        print >> sys.stderr, "Committing: %s" % com
        if com==True:
            pgdb.commitTransaction()
            
