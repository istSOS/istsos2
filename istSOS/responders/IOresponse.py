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
#import mx.DateTime.ISO
import isodate as iso

import logging
from datetime import datetime

#=============================
# set LOG FILE 
# !!! deve stare nel config non qui !!!
#=============================
try:
    logPath = sosConfig.logPath
except:
    logPath = "/tmp/"
now = datetime.now()

defaultQI = 100
#=============================
log = logging.getLogger('insertObservation')
hdlr = logging.FileHandler(logPath+'istsos.log')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] > %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)
#=============================

def get_name_from_urn(stringa,urnName):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1 and not name=="iso8601":
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise sosException.SOSException(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name 

def get_urn_from_name(name,urnName):
    return sosConfig.urn[urnName] + name

class InsertObservationResponse:
    #self.assignedObservationId
    def __init__(self,filter,pgdb):
        
        #-----logging----------
        log.info("\n\nIOresponse: %s" % filter.procedure)
        logTxt = "*************************************************************\n"
        logTxt += "              InsertObservationResponse\n"
        logTxt += "*************************************************************\n"
        #----------------------
        
        #--get procedure information
        #============================================
        sql  = "SELECT id_prc, name_prc, name_oty, name_foi, stime_prc, etime_prc from %s.procedures,%s.obs_type,%s.foi" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
        ##sql += " WHERE id_oty=id_oty_fk AND id_foi=id_foi_fk AND assignedid_prc='%s'" %(get_name_from_urn(filter.assignedSensorId,"sensor"))
        sql += " WHERE id_oty=id_oty_fk AND id_foi=id_foi_fk AND assignedid_prc='%s'" %(filter.assignedSensorId)
        try:
            prc = pgdb.select(sql)[0]
        except:
            raise sosException.SOSException(3,"assignedSensorId '%s' is invalid! SQL: %s" %(filter.assignedSensorId,sql))
                
        #--check requested procedure name exists
        #=============================================
        if not prc["name_prc"]==filter.procedure:
            raise sosException.SOSException(3,"procedure '%s' not associated with provided assignedSensorId" %(filter.procedure))
        
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
                logTxt += " - Updating stime_prc & etime_prc are null"
                # check eventTime interval and update begin/end position when force flas is active
                #----------------------------------------------------------------------------------
                if filter.forceInsert:
                    #-- verify interval limits
                    '''if not (end>=prc["stime_prc"] and start<=prc["etime_prc"]):
                        raise sosException.SOSException(3,"observation eventTime (%s-%s) must overlap procedure samplingTime (%s-%s)" %(start,end,prc["stime_prc"],prc["etime_prc"]))
                    else:'''
                    #-- update begin time of procedure
                    if start<prc["stime_prc"]:
                        sql = "UPDATE %s.procedures SET stime_prc='%s'::TIMESTAMPTZ WHERE id_prc=%s" %(sosConfig.schema,stime[0],prc["id_prc"])
                        try:
                            a = pgdb.executeInThread(sql)
                            com=True
                            logTxt += " stime_prc updated to %s" % stime[0]
                        except:
                            raise sosException.SOSException(3,"SQL: %s" %(sql))
                    #-- update end time of procedure
                    if end>prc["etime_prc"]:
                        sql = "UPDATE %s.procedures SET etime_prc='%s'::TIMESTAMPTZ WHERE id_prc=%s" %(sosConfig.schema,stime[1],prc["id_prc"])
                        try:
                            b = pgdb.executeInThread(sql)
                            com=True
                            logTxt += " etime_prc updated to %s" % stime[1]
                        except Exception as err:
                            raise sosException.SOSException(3,"SQL: %s - %s" %(sql, err.pgerror))

                # check eventTime interval and update begin/end position when force flag is off
                #----------------------------------------------------------------------------------                            
                else:
                    sql  = "SELECT max(time_eti) as max_time_eti from %s.event_time where id_prc_fk = %s group by id_prc_fk" %(sosConfig.schema,prc["id_prc"])
                    try:
                        lastMsr = pgdb.select(sql)[0]["max_time_eti"]
                    except:
                        lastMsr = None
                    
                    if lastMsr!=None:
                        #-- verify begin observation is minor/equal then end time procedure and later then last observation
                                        
                        log.info("\nCheckin dates:")
                        log.info('end %s>=%s etime_prc-> %s'% (end,prc["etime_prc"], (end>=prc["etime_prc"])) )
                        log.info('start %s>=%s etime_prc-> %s'% (start,prc["etime_prc"], (start<=prc["etime_prc"])))
                        log.info('start %s>=%s lastMsr -> %s'% (start,lastMsr,(start>=lastMsr)))
                                           
                        if not (end>=prc["etime_prc"] and start<=prc["etime_prc"] and start>=lastMsr):
                            raise sosException.SOSException(3,"begin observation (%s) must be between last observation (%s) and end procedure (%s); end observation (%s) must be after end procedure (%s)" %(start,lastMsr,prc["etime_prc"],end,prc["etime_prc"]))
                        #-- update end time of procedure
                        sql = "UPDATE %s.procedures SET etime_prc='%s'::TIMESTAMPTZ WHERE id_prc=%s" % (sosConfig.schema,stime[1],prc["id_prc"])
                        try:
                            b = pgdb.executeInThread(sql)
                            com=True
                        except Exception as err:
                            raise sosException.SOSException(3,"SQL: %s - %s" %(sql, err.pgerror))
                    else:
                        #-- verify begin observation is minor/equal then end time procedure and later then last observation
                        if not (end>=prc["etime_prc"] and start<=prc["etime_prc"] and start>=prc["stime_prc"]) :
                            raise sosException.SOSException(3,"begin observation (%s) must be between start procedure (%s) and end procedure (%s); end observation (%s) must be after end procedure (%s)" %(start,prc["stime_prc"],prc["etime_prc"],end,prc["etime_prc"]))
                        #-- update end time of procedure
                        sql = "UPDATE %s.procedures SET etime_prc='%s'::TIMESTAMPTZ WHERE id_prc=%s" %(sosConfig.schema,stime[1],prc["id_prc"])
                        try:
                            b = pgdb.executeInThread(sql)
                            com=True
                        except Exception as err:
                            raise sosException.SOSException(3,"SQL: %s - %s" %(sql, err.pgerror))
            else:
                sql = "UPDATE %s.procedures SET stime_prc='%s'::TIMESTAMPTZ, etime_prc='%s'::TIMESTAMPTZ WHERE id_prc=%s" %(sosConfig.schema,stime[0],stime[1],prc["id_prc"])                
                try:
                    b = pgdb.executeInThread(sql)
                    com=True
                except:
                    raise sosException.SOSException(3,"SQL: %s" %(sql))
            
        #  check data definition and uom (compare registered 
        #  observed properties with provided observations)
        #==================================================
        # get values for provided data: UOM, NAME, URN, ID
        #--------------------------------------------------
        sql  = "SELECT id_opr, name_opr, name_uom FROM %s.observed_properties, %s.proc_obs, %s.uoms" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
        sql += " WHERE id_uom_fk=id_uom AND id_opr_fk=id_opr AND id_prc_fk=%s" %(prc["id_prc"])
        try:
            opr = pgdb.select(sql)
        except Exception as err:
            raise sosException.SOSException(3,"SQL2: %s -%s" %(sql, err.pgerror))
            
        #---- get list of available ObservedProperty,unit of measure,property id for this procedure -----
        oprNames=[]
        oprUoms=[]
        oprIds=[]
        for row in opr:
            oprNames.append(row["name_opr"])
            oprUoms.append(row["name_uom"])
            oprIds.append(row["id_opr"])
        
        #---- get ordered list of observed properties ----
        dataKeys = [ key for key in filter.data.keys() ] 
        dataNames = dataKeys
        ### dataNames = [ key.split(":")[-1] for key in filter.data.keys() ]
        
        #----- get ordered list of unit of measures provided -------
        dataUoms = []
        for key in filter.data.keys():
            if "uom" in filter.data[key].keys():
                dataUoms.append(filter.data[key]["uom"])
            else:
                dataUoms.append('None')
                
        #------------------------------------------------------------------  
        # verify that all the properties observed by this procedure
        # are provided with th ecorrect data definition and uom  
        #------------------------------------------------------------------
        logTxt += " == verify that data definition and uom are correct == "
        log.info(" == verify that data definition and uom are correct == ")
        for i,opr in enumerate(oprNames):
            try: 
                #k = dataNames.index(opr)
                k = dataKeys.index(opr)
            except:
                raise sosException.SOSException(3,"parameter '%s' not observed by RegisteredSensor %s" %(opr,oprNames))
            if not str(dataUoms[k])==str(oprUoms[i]):
                raise sosException.SOSException(3,"parameter '%s' not observed with provided unit of measure" %(opr))
            
                    
        logTxt += " DONE!\n"
        log.info(" DONE!\n")
        #---------------------------------------------------------------    
        # verify if time and coordinates are passed as data parameters
        #--------------------------------------------------------------  
        logTxt += " == verify if time and coordinates are passed as data parameters == " 
        log.info(" == verify if time and coordinates are passed as data parameters == ")
        xobs=None
        yobs=None
        zobs=None
        tpar=None
        pars=[]
        parsId=[]
        # urn of different parameters
        #for i, dn in enumerate(dataNames):
        for i, dn in enumerate(dataKeys):
            log.info("%s" % dn)
            if dn.split(":")[-1] in sosConfig.parGeom["x"]:
                xobs = dataKeys[i]
            elif dn.split(":")[-1] in sosConfig.parGeom["y"]:
                yobs = dataKeys[i]
            elif dn.split(":")[-1] in sosConfig.parGeom["z"]:
                zobs = dataKeys[i]
            elif dn.find("iso8601")>=0:
                tpar = dataKeys[i]
            else:
                if not dn.split(":")[-1] == "qualityIndex":
                    pars.append(dataKeys[i])
                    try:
                        parsId.append(oprIds[oprNames.index(dataKeys[i])])
                    except:
                        raise sosException.SOSException(3,"parameter %s not observed by this sensor %s - %s" %(dn,pars,oprNames))
         
        #---------------------------------------------
        # set default quality index if not provided
        #---------------------------------------------
        log.info("SET QI\n")       
        for par in pars:
            try:
                kqi = dataKeys.index(par+":qualityIndex")
                log.info("Par %s has QI!\n" %(par))
            except:
                #filter.data[dn+":qualityIndex"]={"vals":[defaultQI]*len(filter.data[dn]["vals"])}
                #log.info("Par %s not found, QI generated!\n%s\n" %(par,filter.data[dn+":qualityIndex"]))
                filter.data[par+":qualityIndex"]={"vals":[defaultQI]*len(filter.data[par]["vals"])}
                log.info("Par %s not found, QI generated!\n%s\n" %(par,filter.data[par+":qualityIndex"]))
        
        logTxt += " DONE!\n"
        log.info(" DONE!\n")
        #---------------------------------------------------------------        
        # verify that mobile sensors provide coordinates as X,Y,Z
        #---------------------------------------------------------
        if (xobs==False and yobs==False and zobs==False) and prc["name_oty"] == "mobilepoint":
            raise sosException.SOSException(3,"Mobile sensors require x,y,z parameters")
        
        #---------------------------------------------------------------
        # verify that time parameter is provided
        #--------------------------------------------------        
        if not tpar:
            raise sosException.SOSException(3,"parameter 'time:iso8601' is required for InsertObservation")

        #======================        
        #-- insert observation
        #======================
        # delete existing observations if force flag is active
        #------------------------------------------------------
        logTxt += " == inserting observations ==\n"
        log.info(" == inserting observations ==\n")
        if filter.forceInsert:
            logTxt += " > FORCE INSERT: deleting from %s to %s " % (stime[0],stime[1])
            sql = "DELETE FROM %s.event_time WHERE id_prc_fk=%s AND time_eti>='%s'::TIMESTAMPTZ AND time_eti<='%s'::TIMESTAMPTZ" %(sosConfig.schema,prc["id_prc"],stime[0],stime[1])
            try:
                b = pgdb.executeInThread(sql)
                com=True
            except:
                raise sosException.SOSException(3,"SQL: %s" %(sql))
        
        #----------------------------------------
        # CASE I: observations list is void
        #----------------------------------------
        if len(filter.data[tpar]["vals"])==0:
            self.assignedId = ""
            logTxt += " > observation list is void\n"
        #----------------------------------------
        # CASE I: observations list contains data
        #----------------------------------------

        elif len(filter.data[tpar]["vals"])>0:
            #--------------------
            # insert event times
            #--------------------            
            sqlList = []
            sql  = "INSERT INTO %s.event_time (id_prc_fk,time_eti) VALUES" %(sosConfig.schema)
            for i in range(len(filter.data[tpar]["vals"])):
                sqlList.append("(%s,'%s'::TIMESTAMPTZ)" %(prc["id_prc"],filter.data[tpar]["vals"][i]))
            try:
                sql += (",".join(sqlList)) + " RETURNING id_eti"
                log.info(sql+'\n\n')
                ids_eti = pgdb.executeInThread(sql)
                com=True
            except:
                raise sosException.SOSException(3,"SQL: %s" %(sql))
            logTxt += " > insert eventime query: %s\n" %(sql)
            log.info("EventTime: %s" % dn)
            #--------------------
            #--insert par values
            #--------------------      
            log.info("DATA: %s\n" % filter.data)
            log.info("PARS: %s\n" % pars)      
            for i, par in enumerate(pars):
                log.info("Parameter: %s" % par)
                sqlList = []
                sql = "INSERT INTO %s.measures (id_opr_fk, id_eti_fk,id_qi_fk,val_msr) VALUES " %(sosConfig.schema)
                hasvalues = False
                for ii,id_et in enumerate(ids_eti):
                    log.info("filter.data[%s][vals][%s] (%s) == 'NULL'? : %s" %(par,ii,filter.data[par]["vals"][ii],filter.data[par]["vals"][ii] == 'NULL'))
                    if not filter.data[par]["vals"][ii] in ['NULL',None,-999,""]:
                        try:
                            #sqlList.append( "(%s,%s,%s,%s)" %(parsId[i],id_et["id_eti"],"1",filter.data[par]["vals"][ii]) )
                            sqlList.append( "(%s,%s,%s,%s)" %(parsId[i],id_et["id_eti"],filter.data[par+":qualityIndex"]["vals"][ii],filter.data[par]["vals"][ii]) )
                        except:
                            raise sosException.SOSException(3,"L: %s - %s - %s - %s" %(parsId,filter.data[par]["vals"],filter.data[par+":qualityIndex"]["vals"],ids_eti))
                        hasvalues = True
                if hasvalues:
                    try:
                        logTxt += sql + ",".join(sqlList) + " RETURNING id_msr\n\n"
                        #log.info(sql + ",".join(sqlList) + " RETURNING id_msr\n\n")
                        sql = sql + ",".join(sqlList) + " RETURNING id_msr"
                        ids_msr = pgdb.executeInThread(sql)
                        com=True
                    except:
                        #pgdb.executeInThread( "DELETE FROM %s.event_time WHERE id_eti IN (" %(sosConfig.schema) + ",".join([str(ids["id_eti"]) for ids in ids_eti]) + ")" )
                        com=False
                        raise sosException.SOSException(3,"SQL: %s" %(sql))
                else:
                    log.info(" > parameter %s has no values to be inserted!" %(par))
            #-------------------------------------
            #--insert position values if required
            #------------------------------------- 
            if prc["name_oty"] == "mobilepoint":
                logTxt += " > MOBILE POINT TYPE\n"
                xparspl = xobs.split(":")
                epsg = xparspl[xparspl.index("EPSG")+1]
                sqlList = []
                sql = "INSERT INTO %s.positions (id_qi_fk, id_eti_fk,geom_pos) VALUES" %(sosConfig.schema)
                for i,id_et in enumerate(ids_eti):
                    sqlList.append( "(%s,%s,ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s, %s), %s), %s))" %("100",id_et["id_eti"],filter.data[xobs]["vals"][i],filter.data[yobs]["vals"][i],filter.data[zobs]["vals"][i],epsg,sosConfig.istSOSepsg) )
                try:
                    sql += ",".join(sqlList) + " RETURNING id_pos"
                    logTxt += " > insert position query: %s\n" %(sql)
                    ids_pos = pgdb.executeInThread(sql)
                    com=True
                except Exception as a:
                    #pgdb.executeInThread( "DELETE FROM %s.event_time WHERE id_eti IN (" %(sosConfig.schema) + ",".join([ids["id_eti"] for ids in ids_eti]) + ")" )
                    com=False
                    raise sosException.SOSException(3,"%s\nSQL: %s" %(a,sql))
            # register assigned IDs
            self.assignedId = "@".join([str(ids["id_eti"]) for ids in ids_eti])
            # commit executed operations
        if com==True:
            pgdb.commitThread()

        log.info(logTxt)
            
