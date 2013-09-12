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
import os, sys

#import sosConfig
#from istsoslib import sosDatabase
from istsoslib import sosException
#import mx.DateTime.ISO
from datetime import timedelta
import copy
#from datetime import datetime
from lib import isodate as iso
from lib import pytz

class VirtualProcess():
    
    procedures = {}
    samplingTime = (None,None)
    
    def _configure(self, filterRequest, pgdb):
        self.filter = copy.deepcopy(filterRequest)
        self.pgdb = pgdb
        
    def addProcedure(self, name, observedProperty):
        """
        name: String
        observedProperty: String or Array of String
        """
        self.procedures[name] = observedProperty
        
    def execute(self):
        "This method must be overridden to implement data gathering for this virtual procedure"
        raise sosException.SOSException(3,"function execute must be overridden")
    
    def calculateObservations(self, observation):
        self.observation = observation
        self.observation.samplingTime = self.getSampligTime()
        self.observation.data = self.execute()
        if self.filter.aggregate_interval != None:
            self.applyFunction()
    
    def getSampligTime(self):
        self.setSampligTime()
        return self.samplingTime
        
    def setSampligTime(self):
        """
        This method can be overridden to set the virtual procedure sampling time
        *************************************************************************
        By default This method calculate the sampling time of a virtual procedure 
        giving the procedure name from witch the data are derived 
        as single string or array of strings.
        
        If an array is give by default it will return the minimum begin position 
        and the maximum end position among all the procedures name given.
        """
        if len(self.procedures)==0:
            self.samplingTime = (None,None)
        else:
            if len(self.procedures)>1: 
                sql = """ 
                    SELECT min(stime_prc), max(etime_prc)
                    FROM %s.procedures 
                    WHERE (stime_prc IS NOT NULL
                    AND etime_prc IS NOT NULL)
                    AND (
                """ % self.filter.sosConfig.schema
                sql += ("name_prc=%s OR "*len(self.procedures))
                sql += ") GROUP BY stime_prc, etime_prc"
                param = tuple(self.procedures.keys())
            else:
                sql = """ 
                    SELECT stime_prc, etime_prc
                    FROM %s.procedures 
                    WHERE (stime_prc IS NOT NULL
                    AND etime_prc IS NOT NULL)
                """ % self.filter.sosConfig.schema
                sql += "AND name_prc=%s"
                param = (self.procedures.keys()[0],)
                
            try:
                result = self.pgdb.select(sql, param)
                if len(result)==0:
                    raise sosException.SOSException(3,"Virtual Procedure Error: procedure %s not found in the database" % (", ".join(param)) )
                result = result[0]
            except Exception as e:
                raise sosException.SOSException(3,"Database error: %s - %s" % (sql, e))    
                
            self.samplingTime = (result[0],result[1])
        
    def getData(self, procedure=None, disableAggregation=False):
        """
        procedure: String
        """
        
        # Validating:
        # If procedure is None, it is supposed that only one procedure has been added
        if procedure is None:
            if len(self.procedures)==0:
                raise sosException.SOSException(3,"Virtual Procedure Error: no procedures added")    
            procedure = self.procedures.keys()[0]
            
        elif procedure not in self.procedures.keys():
            raise sosException.SOSException(3,"Virtual Procedure Error: procedure %s has not been added to this virtual procedure" % procedure)    
        
        virtualFilter = copy.deepcopy(self.filter)
        virtualFilter.procedure = [procedure]
        virtualFilter.observedProperty = self.procedures[procedure]
        
        sql = """
            SELECT DISTINCT id_prc, name_prc, name_oty, 
                stime_prc, etime_prc, time_res_prc, name_tru 
            FROM 
                %s.procedures, 
                %s.proc_obs p, 
                %s.observed_properties, 
                %s.uoms, 
                %s.time_res_unit, 
                %s.obs_type """ % ((self.filter.sosConfig.schema,)*6 )
        sql += """
                WHERE id_prc = p.id_prc_fk 
                AND id_opr_fk = id_opr 
                AND id_uom = id_uom_fk 
                AND id_tru = id_tru_fk 
                AND id_oty = id_oty_fk
                AND name_prc=%s"""
        
        try:
            result = self.pgdb.select(sql, (procedure,))
            if len(result)==0:
                raise sosException.SOSException(3,"Virtual Procedure Error: procedure %s not found in the database" % procedure)
            result = result[0]
        except Exception as e:
            raise sosException.SOSException(3,"Database error: %s - %s" % (sql, e))    
        
        obs = Observation()
        
        obs.baseInfo(self.pgdb, result, virtualFilter.sosConfig)
        obs.setData(self.pgdb, result, virtualFilter)
        
        return obs.data
    
    def applyFunction(self):
        try:
            # Create array container
            begin = iso.parse_datetime(self.filter.eventTime[0][0])
            end = iso.parse_datetime(self.filter.eventTime[0][1])
            duration = iso.parse_duration(self.filter.aggregate_interval)
            result = {}
            dt = begin
            fields = len(self.observation.observedProperty)# + 1 # +1 timestamp field not mentioned in the observedProperty array
            
            while dt < end:
                dt2 = dt + duration
                result[dt2]=[]
                for c in range(fields):
                    result[dt2].append([])
                
                d = 0
                data = copy.copy(self.observation.data)
                while len(data) > 0:
                    tmp = data.pop(d)
                    if dt < tmp[0] and tmp[0] <= dt2:
                        self.observation.data.pop(d)
                        for c in range(fields):
                            result[dt2][c].append(float(tmp[c+1]))
                    elif dt > tmp[0]:
                        self.observation.data.pop(d)
                    elif dt2 < tmp[0]:
                        break
                        
                dt = dt2
                
            data = []
            
            for r in sorted(result):
                record = [r]
                for v in range(len(result[r])):
                    if self.observation.observedProperty[v].split(":")[-1]=="qualityIndex":
                        if len(result[r][v])==0:
                            record.append(self.filter.aggregate_nodata_qi)
                        else:
                            record.append(int(min(result[r][v])))
                    else:
                        val = None
                        if len(result[r][v])==0:
                            val = self.filter.aggregate_nodata
                        elif self.filter.aggregate_function.upper() == 'SUM':
                            val = sum(result[r][v])
                        elif self.filter.aggregate_function.upper() == 'MAX':
                            val = max(result[r][v])
                        elif self.filter.aggregate_function.upper() == 'MIN':
                            val = min(result[r][v])
                        elif self.filter.aggregate_function.upper() == 'AVG':
                            val = round(sum(result[r][v])/len(result[r][v]),4)
                        elif self.filter.aggregate_function.upper() == 'COUNT':
                            val = len(result[r][v])
                        record.append(val)
                data.append(record)
                    
            self.observation.data = data
            
        except Exception as e:
            raise sosException.SOSException(3,"Error while applying aggregate function on virtual procedures: %s" % (e))
        

class VirtualProcessHQ(VirtualProcess):
    
    def setDischargeCurves(self):
        "method for setting h-q tranformation tables/curves"       
        #set requested period
        #================================================
        hqFile = os.path.join(
                        self.filter.sosConfig.virtual_processes_folder,
                        self.filter.procedure[0],
                        self.filter.procedure[0]+".rcv"
				)
        tp=[]
        if self.filter.eventTime == None:
            tp = [None,None]
        else:
            for t in self.filter.eventTime:
                if len(t) == 2:
                    if t[0].find('+')==-1:
                        t[0] += "+00:00"
                    if t[1].find('+')==-1:
                        t[1] += "+00:00"    
                    tp.append(iso.parse_datetime(t[0]))
                    tp.append(iso.parse_datetime(t[1]))
                if len(t)==1:
                    if t[0].find('+')==-1:
                        t[0] += "+00:00"
                    tp.append(iso.parse_datetime(t[0]))
        period = (min(tp),max(tp))
        #get required parameters
        #==================================================
        try:        
            hq_fh = open(hqFile,'r')
        except Exception as e:
            raise sosException.SOSException(3,"Unable to open hq rating curve file at: %s" % hqFile)
        lines = hq_fh.readlines()
        #read header
        hqs = {'from':[],'to':[],'low':[],'up': [],'A':[],'B':[],'C':[],'K':[]}
        head = lines[0].strip().split("|")
        try:
            fromt = head.index('from')  #from time
            tot = head.index('to')      #to time
            low = head.index('low_val') #if value is bigger than
            up = head.index('up_val')   #and is lower than
            A = head.index('A')         #use this A
            B = head.index('B')         #use this B
            C = head.index('C')         #use this C
            K = head.index('K')         #use this K
        except Exception as e:
            raise sosException.SOSException(3,"setDischargeCurves: FILE %s ,%s error in header.\n %s" %(hqFile,head,e))
        
        #get equations
        if not period[0] == None:
            for l in range(1,len(lines)):
                line = lines[l].split("|")
                if iso.parse_datetime(line[1]) > period[0] or iso.parse_datetime(line[0]) <= period[1]:
                    hqs['from'].append(iso.parse_datetime(line[fromt]))
                    hqs['to'].append(iso.parse_datetime(line[tot]))
                    hqs['low'].append(float(line[low]))
                    hqs['up'].append(float(line[up]))
                    hqs['A'].append(float(line[A]))
                    hqs['B'].append(float(line[B]))
                    hqs['C'].append(float(line[C]))
                    hqs['K'].append(float(line[K]))
        else:
            for l in [-1,-2]:
                try:
                    line = lines[l].split("|")
                    hqs['from'].append(iso.parse_datetime(line[fromt]))
                    hqs['to'].append(iso.parse_datetime(line[tot]))
                    hqs['low'].append(float(line[low]))
                    hqs['up'].append(float(line[up]))
                    hqs['A'].append(float(line[A]))
                    hqs['B'].append(float(line[B]))
                    hqs['C'].append(float(line[C]))
                    hqs['K'].append(float(line[K]))
                except:
                    pass
        #raise sosException.SOSException(3,"%s" %(hqs))
        self.hqCurves = hqs
        
    def execute(self):
        #print "self running.."
        #import datetime, decimal, sys
        
        self.setDischargeCurves()
        data = self.getData()
        
        if self.filter.qualityIndex == True:
            data_out=[]
            for rec in data:
                if (float(rec[1])) < -999.0:
                    data_out.append([ rec[0], -999.9, 110 ])
                else:
                    for o in range(len(self.hqCurves['from'])):
                        if (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] <= float(rec[1]) < self.hqCurves['up'][o]):
                            if (float(rec[1])-self.hqCurves['B'][o]) >=0:
                                data_out.append([ rec[0], "%.3f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])), rec[2] ])
                            else:
                                #data not evaluable
                                data_out.append([ rec[0], -999.9, 120 ])
                            break
                        if o == ( len(self.hqCurves['from']) -1):
                            #data non in curves definition
                            data_out.append([ rec[0], -999.9, 120 ])       
        else:
            data_out=[]
            for rec in data:
                for o in range(len(self.hqCurves['from'])):
                    if (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] <= float(rec[1]) < self.hqCurves['up'][o]):
                        if (float(rec[1])-self.hqCurves['B'][o]) >=0:
                            data_out.append([ rec[0], "%.3f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])) ])
                        else:
                            data_out.append([ rec[0],-999.9 ])
                        break
                    if o == (len(self.hqCurves['from'])-1):
                        data_out.append([ rec[0], -999.9 ])
                        
        return data_out  
        
        
#--this while is not
#import TEST as Vproc        
#----------------------------------

def BuildobservedPropertyList(pgdb,offering,sosConfig):
    list=[]
    sql = "SELECT distinct(def_opr) as nopr FROM %s.procedures, %s.proc_obs p," %(sosConfig.schema,sosConfig.schema)
    sql += " %s.observed_properties, %s.off_proc o, %s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_opr_fk=id_opr AND p.id_prc_fk=id_prc AND o.id_prc_fk=id_prc AND id_off=id_off_fk"
    sql += " AND name_off='%s' ORDER BY nopr" %(offering)
    rows=pgdb.select(sql)
    for row in rows:
        list.append(row["nopr"])
    return list

def BuildfeatureOfInterestList(pgdb,offering,sosConfig):
    list=[]
    sql = "SELECT distinct(name_foi) as nfoi FROM %s.foi, %s.procedures " %(sosConfig.schema,sosConfig.schema)
    sql += " , %s.off_proc, %s.offerings" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_foi=id_foi_fk AND id_prc_fk=id_prc"
    sql += " AND id_off=id_off_fk AND name_off='%s' ORDER BY nfoi"  %(offering)
  
    try:
        rows=pgdb.select(sql)
    except:
        raise sosException.SOSException(1,"sql: %s" %(sql))
    for row in rows:
        list.append(row["nfoi"])
    return list
    
def BuildProcedureList(pgdb,offering,sosConfig):
    list=[]
    sql = "SELECT name_prc FROM %s.procedures, %s.off_proc, %s.offerings"  %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc=id_prc_fk AND id_off=id_off_fk AND name_off='%s'" %(offering)
    sql += " ORDER BY name_prc"
    rows=pgdb.select(sql)
    for row in rows:
        list.append(row["name_prc"])    
    return list

def BuildOfferingList(pgdb,sosConfig):
    list=[]
    sql = "SELECT distinct(name_off) FROM %s.procedures,%s.off_proc,%s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE  id_prc=id_prc_o_fk AND id_off_fk=id_off ORDER BY name_off"
    rows=pgdb.select(sql)
    for row in rows:
        list.append(row["name_off"])

'''
def buildQuery(parameters):
    """Documentation"""

'''

                
'''
filter.eventTime
filter.aggregate_function
filter.aggregate_interval
filter.aggregate_nodata
filter.aggregate_nodata_qi
'''

def applyFunction(ob, filter):
    import copy
    try:
        # Create array container
        begin = iso.parse_datetime(filter.eventTime[0][0])
        end = iso.parse_datetime(filter.eventTime[0][1])
        duration = iso.parse_duration(filter.aggregate_interval)
        result = {}        
        dt = begin
        fields = len(ob.observedProperty)# + 1 # +1 timestamp field not mentioned in the observedProperty array
        
        while dt < end:
            dt2 = dt + duration
            result[dt2]=[]
            for c in range(fields):
                result[dt2].append([])
            
            d = 0
            data = copy.copy(ob.data)
            while len(data) > 0:
                tmp = data.pop(d)
                if dt < tmp[0] and tmp[0] <= dt2:
                    ob.data.pop(d)
                    for c in range(fields):
                        result[dt2][c].append(float(tmp[c+1]))
                elif dt > tmp[0]:
                    ob.data.pop(d)
                elif dt2 < tmp[0]:
                    break
                    
            dt = dt2
            
        data = []
        
        for r in sorted(result):
            record = [r]
            for v in range(len(result[r])):
                if ob.observedProperty[v].split(":")[-1]=="qualityIndex":
                    if len(result[r][v])==0:
                        record.append(filter.aggregate_nodata_qi)
                    else:
                        record.append(int(min(result[r][v])))
                else:
                    val = None
                    if len(result[r][v])==0:
                        val = filter.aggregate_nodata
                    elif filter.aggregate_function.upper() == 'SUM':
                        val = sum(result[r][v])
                    elif filter.aggregate_function.upper() == 'MAX':
                        val = max(result[r][v])
                    elif filter.aggregate_function.upper() == 'MIN':
                        val = min(result[r][v])
                    elif filter.aggregate_function.upper() == 'AVG':
                        val = round(sum(result[r][v])/len(result[r][v]),4)
                    elif filter.aggregate_function.upper() == 'COUNT':
                        val = len(result[r][v])
                    record.append(val)
            data.append(record)
                
        ob.data = data
        
    except Exception as e:
        raise sosException.SOSException(3,"Error while applying aggregate function on virtual procedures: %s" % (e))
    

class offInfo:
    def __init__(self,off_name,pgdb,sosConfig):
        sql = "SELECT name_off, desc_off FROM %s.offerings WHERE name_off='%s'" %(sosConfig.schema,off_name)
        try:
            off = pgdb.select(sql)[0]
            self.name=off["name_off"]
            self.desc=off["desc_off"]
        except:
            raise sosException.SOSException(2,"Parameter \"offering\" sent with invalid value: %s"%(off_name))


# @todo instantation with Builder pattern will be less confusing, observation class must be just a data container
class Observation:

    def __init__(self):
        self.procedure=None
        self.name = None
        self.id_prc=None
        self.procedureType=None
        self.samplingTime=None
        #self.reqTZ = None
        self.refsys = None
        self.timeResUnit=None
        self.timeResVal=None
        self.observedProperty=None
        self.opr_urn=None
        self.uom=None
        self.featureOfInterest=None
        self.foi_urn=None
        self.foiGml = None
        self.dataType=None
        self.timedef = None
        self.qualitydef = None
        self.data=[]
        
    def baseInfo(self, pgdb, o, sosConfig):
        #set base information of registered procedure
        #=============================================
        
        k = o.keys()
        if not ("id_prc" in k and "name_prc" in k and  "name_oty" in k and "stime_prc" in k and "etime_prc" in k and "time_res_prc" in k and "name_tru" in k ):
            raise sosException.SOSException(3,"Error, baseInfo argument: %s"%(o))
        
        #SET PROCEDURE NAME AND ID
        #===========================
        self.id_prc=o["id_prc"]
        self.name = o["name_prc"]
        #self.procedure = sosConfig.urn["procedure"] + ":" + o["name_prc"]
        self.procedure = sosConfig.urn["procedure"] + o["name_prc"]
        
        #SET PROCEDURE TYPE
        #========================= --> ADD OTHER TYPES (IN CONFIG??)
        if o["name_oty"].lower() in ["insitu-fixed-point","insitu-mobile-point","virtual"]:
            self.procedureType=o["name_oty"]
            #TO BE IMPLEMENTED FOR MORE OPTIONS
        else:
            raise sosException.SOSException(2,"error in procedure type setting")
        
        #SET TIME: RESOLUTION VALUE AND UNIT
        #===================================
        self.timeResVal = o["time_res_prc"]
        self.timeResUnit = o["name_tru"]
        
        #SET SAMPLING TIME
        #===================================
        if o["stime_prc"]!=None and o["etime_prc"]!=None:
            self.samplingTime=[o["stime_prc"],o["etime_prc"]]
        else:
            self.samplingTime = None
        
        self.dataType = sosConfig.urn["dataType"] + "timeSeries"
        self.timedef = sosConfig.urn["parameter"] + "time:iso8601"
        self.qualitydef = None
        
        
    def setData(self,pgdb,o,filter):
        """get data according to request filters"""
        # @todo mettere da qualche altra parte
	        
        #SET FOI OF PROCEDURE
        #=========================================
        sqlFoi  = "SELECT name_fty, name_foi, ST_AsGml(ST_Transform(geom_foi,%s)) as gml" %(filter.srsName)
        sqlFoi += " FROM %s.procedures, %s.foi, %s.feature_type" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sqlFoi += " WHERE id_foi_fk=id_foi AND id_fty_fk=id_fty AND id_prc=%s" %(o["id_prc"])
        try:
            resFoi = pgdb.select(sqlFoi)
        except:
            raise sosException.SOSException(3,"SQL: %s"%(sqlFoi))
        
        self.featureOfInterest = resFoi[0]["name_foi"]
        self.foi_urn = filter.sosConfig.urn["feature"] + resFoi[0]["name_fty"] + ":" + resFoi[0]["name_foi"]
        if resFoi[0]["gml"].find("srsName")<0:
            srs = filter.srsName or filter.sosConfig.istsosepsg
            self.foiGml = resFoi[0]["gml"][:resFoi[0]["gml"].find(">")] + " srsName=\"EPSG:%s\"" % srs + resFoi[0]["gml"][resFoi[0]["gml"].find(">"):]
        else:
            self.foiGml = resFoi[0]["gml"]
        
        #SET INFORMATION ABOUT OBSERVED_PROPERTIES
        #=========================================       
        sqlObsPro = "SELECT id_pro, id_opr, name_opr, def_opr, name_uom FROM %s.observed_properties, %s.proc_obs, %s.uoms" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sqlObsPro += " WHERE id_opr_fk=id_opr AND id_uom_fk=id_uom AND id_prc_fk=%s" %(o["id_prc"])
        sqlObsPro += " AND ("
        #sqlObsPro += " OR ".join(["def_opr='" + str(i) + "'" for i in filter.observedProperty])
        sqlObsPro += " OR ".join(["def_opr SIMILAR TO '%(:|)" + str(i) + "(:|)%'" for i in filter.observedProperty])
        sqlObsPro += " ) ORDER BY def_opr ASC"
        try:
            obspr_res = pgdb.select(sqlObsPro)
        except:
            raise sosException.SOSException(3,"SQL: %s"%(sqlObsPro))
            
        self.observedProperty = []
        self.observedPropertyName = []
        self.opr_urn = []
        self.uom = []
        self.qualityIndex = filter.qualityIndex
        
        for row in obspr_res:
            self.observedProperty += [str(row["def_opr"])]
            self.observedPropertyName +=[str(row["name_opr"])]
            self.opr_urn += [str(row["def_opr"])]
            try:
                #self.uom += [str(row["name_uom"]).encode('utf-8')]
                self.uom += [row["name_uom"]]
            except:
                self.uom += ["n/a"]
            if self.qualityIndex==True:
                self.observedProperty += [str(row["def_opr"])+":qualityIndex"]
                self.observedPropertyName += [str(row["name_opr"])+":qualityIndex"]
                self.opr_urn += [str(row["def_opr"] +":qualityIndex")]
                self.uom += ["-"]
        
        #SET DATA
        #=========================================getSampligTime
        #CASE "insitu-fixed-point" or "insitu-mobile-point"
        #-----------------------------------------
        if self.procedureType in ["insitu-fixed-point","insitu-mobile-point"]:
            sqlSel = "SELECT et.time_eti as t," 
            joinar=[]
            cols=[]

            aggrCols=[]
            aggrNotNull=[]

            valeFieldName = []
            for idx, obspr_row in enumerate(obspr_res):
                if self.qualityIndex==True:
                    cols.append("C%s.val_msr as c%s_v, C%s.id_qi_fk as c%s_qi" %(idx,idx,idx,idx))
                    valeFieldName.append("c%s_v" %(idx))
                    valeFieldName.append("c%s_qi" %(idx))
                else:
                    cols.append("C%s.val_msr as c%s_v" %(idx,idx))
                    valeFieldName.append("c%s_v" %(idx))

                # If Aggregatation funtion is set
                #---------------------------------
                if filter.aggregate_interval != None:
                    # This can be usefull with string values
                    '''aggrCols.append("CASE WHEN %s(dt.c%s_v) is NULL THEN '%s' ELSE '' || %s(dt.c%s_v) END as c%s_v\n" % ( 
                        filter.aggregate_function, idx, filter.aggregate_nodata, filter.aggregate_function, idx, idx)
                    )'''
                    # This accept only numeric results
                    aggrCols.append("COALESCE(%s(dt.c%s_v),'%s') as c%s_v\getSampligTimen" %(filter.aggregate_function,idx,filter.aggregate_nodata,idx))
                    if self.qualityIndex==True:
                        #raise sosException.SOSException(3,"QI: %s"%(self.qualityIndex))
                        aggrCols.append("COALESCE(MIN(dt.c%s_qi),%s) as c%s_qi\n" %( idx, filter.aggregate_nodata_qi, idx ))
                    aggrNotNull.append(" c%s_v > -900 " %(idx))
                
                # Set SQL JOINS
                #---------------
                join_txt  = " left join (\n"
                join_txt += " SELECT distinct A%s.id_msr, A%s.val_msr, A%s.id_eti_fk\n" %(idx,idx,idx)

                if self.qualityIndex==True:
                    join_txt += ",A%s.id_qi_fk\n" %(idx)
                join_txt += "   FROM %s.measures A%s, %s.event_time B%s\n" %(filter.sosConfig.schema,idx,filter.sosConfig.schema,idx)
                join_txt += " WHERE A%s.id_eti_fk = B%s.id_eti\n" %(idx,idx)
                join_txt += " AND A%s.id_pro_fk=%s\n" %(idx,obspr_row["id_pro"])
                join_txt += " AND B%s.id_prc_fk=%s\n" %(idx,o["id_prc"])
                
                # if qualityIndex has filter
                #------------------------------
                #if filter.qualityIndex and filter.qualityIndex.__class__.__name__=='str':
                #    join_txt += " AND %s\n" %(filter.qualityIndex)

                # ATTETION: HERE -999 VALUES ARE EXCLUDED WHEN ASKING AN AGGREAGATE FUNCTION
                if filter.aggregate_interval != None:
                    join_txt += " AND A%s.val_msr > -900 " % idx
                
                # If eventTime is set add to JOIN part
                #--------------------------------------
                if filter.eventTime:
                    join_txt += " AND ("
                    etf=[]
                    for ft in filter.eventTime:
                        if len(ft)==2:
                            etf.append("B%s.time_eti > timestamptz '%s' AND B%s.time_eti <= timestamptz '%s' \n" %(idx,ft[0],idx,ft[1]))
                        elif len(ft)==1:
                            etf.append("B%s.time_eti = timestamptz '%s' \n" %(idx,ft[0]))
                        else:
                            raise sosException.SOSException(2,"error in time filter")
                    join_txt += " OR ".join(etf)
                    join_txt +=  ")\n"
                else:
                    join_txt += " AND B%s.time_eti = (SELECT max(time_eti) FROM %s.event_time WHERE id_prc_fk=%s) \n" %(idx,filter.sosConfig.schema,o["id_prc"])
                
                # close SQL JOINS
                #-----------------
                join_txt += " ) as C%s\n" %(idx)
                join_txt += " on C%s.id_eti_fk = et.id_eti" %(idx)
                joinar.append(join_txt)
            
            
            #If MOBILE PROCEDURE
            #--------------------
            if self.procedureType=="insitu-mobile-point":
                join_txt  = " left join (\n"
                join_txt += " SELECT distinct Ax.id_pos, X(ST_Transform(Ax.geom_pos,%s)) as x,Y(ST_Transform(Ax.geom_pos,%s)) as y,Z(ST_Transform(Ax.geom_pos,%s)) as z, Ax.id_eti_fk\n" %(filter.srsName,filter.srsName,filter.srsName)
                if self.qualityIndex==True:
                    join_txt += ", Ax.id_qi_fk as posqi\n"
                join_txt += "   FROM %s.positions Ax, %s.event_time Bx\n" %(filter.sosConfig.schema,filter.sosConfig.schema)
                join_txt += " WHERE Ax.id_eti_fk = Bx.id_eti"
                join_txt += " AND Bx.id_prc_fk=%s" %(o["id_prc"])
                
                if filter.eventTime:
                    join_txt += " AND ("
                    etf=[]
                    for ft in filter.eventTime:
                        if len(ft)==2:
                            etf.append("Bx.time_eti > timestamptz '%s' AND Bx.time_eti <= timestamptz '%s' " %(ft[0],ft[1]))
                        elif len(ft)==1:
                            etf.append("Bx.time_eti = timestamptz '%s' " %(ft[0]))                       
                        else:
                            raise sosException.SOSException(2,"error in time filter")
                    join_txt += " OR ".join(etf)
                    join_txt +=  ")\n"
                else:
                    join_txt += " AND Bx.time_eti = (SELECT max(time_eti) FROM %s.event_time WHERE id_prc_fk=%s) " %(filter.sosConfig.schema,o["id_prc"])
                
                join_txt += " ) as Cx on Cx.id_eti_fk = et.id_eti\n"
                sqlSel += " Cx.x as x, Cx.y as y, Cx.z as z, "
                if self.qualityIndex==True:
                    sqlSel += "Cx.posqi, "
                joinar.append(join_txt)
            
            
            # Set FROM CLAUSE
            #-----------------    
            sqlSel += ", ".join(cols)
            sqlSel += " FROM %s.event_time et\n" %(filter.sosConfig.schema)

            #====================            
            # Set WHERE CLAUSES
            #====================
            sqlData = " ".join(joinar)
            sqlData += " WHERE et.id_prc_fk=%s\n" %(o["id_prc"]) 

            # Set FILTER ON RESULT (OGC:COMPARISON) -
            #----------------------------------------
            if filter.result:
                for ind, ov in enumerate(self.observedProperty):
                    if ov.find(filter.result[0])>0:
                        sqlData += " AND C%s.val_msr %s" %(ind,filter.result[1])
                #sqlData += " AND C%s.val_msr %s" %(self.observedProperty.index(filter.result[0]),filter.result[1])
                
            # Set FILTER ON EVENT-TIME -
            #---------------------------
            if filter.eventTime:
                sqlData += " AND ("
                etf=[]
                for ft in filter.eventTime:
                    if len(ft)==2:
                        etf.append("et.time_eti > timestamptz '%s' AND et.time_eti <= timestamptz '%s' " %(ft[0],ft[1]))
                    elif len(ft)==1:
                        etf.append("et.time_eti = timestamptz '%s' " %(ft[0]))                        
                    else:
                        raise sosException.SOSException(2,"error in time filter")
                sqlData += " OR ".join(etf)
                sqlData +=  ")"
            else:
                sqlData += " AND et.time_eti = (SELECT max(time_eti) FROM %s.event_time WHERE id_prc_fk=%s) " %(filter.sosConfig.schema,o["id_prc"])

            sqlData += " ORDER by et.time_eti"

            sql = sqlSel+sqlData
            
            #
            if filter.aggregate_interval != None:
                self.aggregate_function = filter.aggregate_function.upper()
                '''
                for i in range(0,len(self.observedProperty)):
                    self.observedProperty[i] = "%s:%s" % (self.observedProperty[i], filter.aggregate_function)

                for ob in self.observedProperty:
                    ob = "%s:%s" % (ob, filter.aggregate_function)'''
                
                # Interval preparation
                # Converting ISO 8601 duration
                isoInt = iso.parse_duration(filter.aggregate_interval)
                sqlInt = ""

                if isinstance(isoInt, timedelta):
                
                    if isoInt.days>0:
                        sqlInt += "%s days " % isoInt.days
                    if isoInt.seconds>0:
                        sqlInt += "%s seconds " % isoInt.seconds
                        
                elif isinstance(isoInt, iso.Duration): 
                    print "INTERVAL:"
                    if isoInt.years>0:
                        print isoInt.years
                        sqlInt += "%s years " % isoInt.years
                    if isoInt.months>0:
                        isoInt.months = int(isoInt.months)
                        print isoInt.months
                        sqlInt += "%s months " % isoInt.months
                    if isoInt.days>0:
                        print isoInt.days
                        sqlInt += "%s days " % isoInt.days
                    if isoInt.seconds>0:
                        print isoInt.seconds
                        sqlInt += "%s seconds " % isoInt.seconds

                
                # @todo improve this part
                # calculate how many step are included in the asked interval.
                hopBefore = 1
                hop = 0
                tmpStart = iso.parse_datetime(filter.eventTime[0][0])
                tmpEnd = self.samplingTime[1]
                
                while (tmpStart+isoInt)<=tmpEnd and (tmpStart+isoInt)<=iso.parse_datetime(filter.eventTime[0][1]):
                    
                    if   tmpStart <  self.samplingTime[0]:
                        hopBefore+=1
                        hop+=1

                    elif (tmpStart >= self.samplingTime[0]) and ((tmpStart+isoInt)<=self.samplingTime[1]):
                        hop+=1
                        
                    tmpStart=tmpStart+isoInt

                aggregationSQL = "SELECT ts.sint  as t, %s\n"
                aggregationSQL += "FROM\n"
                aggregationSQL += "    (\n" # Generating time series here
                aggregationSQL += "        select\n"
                aggregationSQL += "        (('%s'::TIMESTAMP WITH TIME ZONE)  \n"
                aggregationSQL += "            + s.a * '%s'::interval)::TIMESTAMP WITH TIME ZONE as sint\n"
                aggregationSQL += "        from generate_series(%s, %s) as s(a)\n"
                aggregationSQL += "    ) as ts LEFT JOIN ( \n\n"
                aggregationSQL += "    %s \n\n"
                aggregationSQL += "    ) as dt\n"
                aggregationSQL += "    ON (\n"
                aggregationSQL += "        dt.t > (ts.sint-'%s'::interval)\n"
                aggregationSQL += "        AND\n"
                aggregationSQL += "        dt.t <= (ts.sint) \n"
                aggregationSQL += "    )\n"
                aggregationSQL += "    GROUP BY ts.sint\n"
                aggregationSQL += "    ORDER BY ts.sint"
                sql = aggregationSQL % (", ".join(aggrCols), filter.eventTime[0][0], sqlInt, hopBefore, hop, sql, sqlInt)
                
            else:
                self.aggregate_function = None
                
            #--------- debug execute query --------
            #raise sosException.SOSException(3,sql)
            #print >> sys.stderr, sql
            #--------------------------------------
            try:
                data_res = pgdb.select(sql)
            except:
                raise sosException.SOSException(3,"SQL: %s"%(sql))
            

            #------------------------------------            
            #--------- APPEND DATA IN ARRAY -----
            #------------------------------------            
            #append data
            for line in data_res:
                if self.procedureType=="insitu-fixed-point":
                    data_array = [line["t"]]
                elif self.procedureType=="insitu-mobile-point":
                    if self.qualityIndex==True:
                        data_array = [line["t"],line["x"],line["y"],line["z"],line["posqi"]]
                    else:
                        data_array = [line["t"],line["x"],line["y"],line["z"]]
                data_array.extend([line[field] for field in valeFieldName])
                self.data.append(data_array)
            #raise sosException.SOSException(3,self.data)
            #else:
            #    raise sosException.SOSException(3,"SQLEEE: %s"%(sql))
            
        #-----------------------------------------                
        #CASE "virtual"
        #-----------------------------------------       
        elif self.procedureType in ["virtual"]:
            
            
            self.aggregate_function = filter.aggregate_function
            self.aggregate_interval = filter.aggregate_interval
            self.aggregate_nodata = filter.aggregate_nodata
            self.aggregate_nodata_qi = filter.aggregate_nodata_qi
                        
            vpFolder = os.path.join(os.path.join(filter.sosConfig.virtual_processes_folder,self.name))
            
            if not os.path.isfile("%s/%s.py" % (vpFolder,self.name)):
                raise sosException.SOSException(2,"Virtual procedure folder does not contain any Virtual Procedure code for %s" % self.name)
                
            #----- VIRTUAL PROCESS LOADING -----
            try:
                sys.path.append(vpFolder)
            except:
                raise sosException.SOSException(2,"error in loading virtual procedure path")
            #import procedure process
            exec "import %s as vproc" %(self.name)
            
            # Initialization of virtual procedure will load the source data
            vp = vproc.istvp()
            vp._configure(filter, pgdb)
            # Calculate virtual procedure data
            vp.calculateObservations(self)
                
                
class observations:
    def __init__(self,filter,pgdb):
        self.offInfo = offInfo(filter.offering,pgdb,filter.sosConfig)
        self.refsys = filter.sosConfig.urn["refsystem"] + filter.srsName
        self.filter = filter
        
        #CHECK FILTER VALIDITY
        #=========================================
        if filter.procedure:
            pl = BuildProcedureList(pgdb,filter.offering,filter.sosConfig)
            for p in filter.procedure:
                if not p in pl:
                    raise sosException.SOSException(2,"Parameter \"procedure\" sent with invalid value: %s -  available options for offering \"%s\": %s"%(p,filter.offering,pl))
        
        if filter.featureOfInterest:
            fl = BuildfeatureOfInterestList(pgdb,filter.offering,filter.sosConfig)
            if not filter.featureOfInterest in fl:
                raise sosException.SOSException(2,"Parameter \"featureOfInterest\" sent with invalid value: %s - available options: %s"%(filter.featureOfInterest,fl))
        
        if filter.observedProperty:
            opl = BuildobservedPropertyList(pgdb, filter.offering,filter.sosConfig)
            opr_sel = "SELECT def_opr FROM %s.observed_properties WHERE " %(filter.sosConfig.schema,)
            opr_sel_w = []
            for op in filter.observedProperty:
                opr_sel_w += ["def_opr SIMILAR TO '%%(:|)%s(:|)%%'" %(op)]
            opr_sel = opr_sel + " OR ".join(opr_sel_w)
            try:
                opr_filtered = pgdb.select(opr_sel)
            except:
                raise sosException.SOSException(3,"SQL: %s"%(opr_sel))
            if not len(opr_filtered)>0:
                raise sosException.SOSException(2,"Parameter \"observedProperty\" sent with invalid value: %s - available options: %s"%(filter.observedProperty,opl))
        
        #SET TIME PERIOD
        #=========================================
        tp=[]
        if filter.eventTime == None:
            tp = [None,None]
        else:
            for t in filter.eventTime:
                if len(t) == 2:
                    tp.append(iso.parse_datetime(t[0]))
                    tp.append(iso.parse_datetime(t[1]))
                if len(t)==1:
                    tp.append(iso.parse_datetime(t[0]))
                #else: rise error ???
        self.period = [min(tp),max(tp)]
        
        self.obs=[]
        
        # SET REQUEST TIMEZONE
        #===================================
        if filter.eventTime:
            if iso.parse_datetime(filter.eventTime[0][0]).tzinfo:
                self.reqTZ = iso.parse_datetime(filter.eventTime[0][0]).tzinfo
                pgdb.setTimeTZ(iso.parse_datetime(filter.eventTime[0][0]))
            else:
                self.reqTZ = pytz.utc
                pgdb.setTimeTZ("UTC")
        else:
            self.reqTZ = pytz.utc
            pgdb.setTimeTZ("UTC")
            
        
        
        #BUILD PROCEDURES LIST
        #=========================================
        #---select part of query
        sqlSel = "SELECT DISTINCT"
        sqlSel += " id_prc, name_prc, name_oty, stime_prc, etime_prc, time_res_prc, name_tru"
        #---from part of query
        sqlFrom = "FROM %s.procedures, %s.proc_obs p, %s.observed_properties, %s.uoms, %s.time_res_unit," %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sqlFrom += " %s.off_proc o, %s.offerings, %s.obs_type" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        if filter.featureOfInterest or filter.featureOfInterestSpatial:
            sqlFrom += " ,%s.foi, %s.feature_type" %(filter.sosConfig.schema,filter.sosConfig.schema)
        
        sqlWhere = "WHERE id_prc=p.id_prc_fk AND id_opr_fk=id_opr AND o.id_prc_fk=id_prc AND id_off_fk=id_off AND id_uom=id_uom_fk AND id_tru=id_tru_fk AND id_oty=id_oty_fk"
        sqlWhere += " AND name_off='%s'" %(filter.offering) 
        
        #---where condition based on featureOfInterest
        if filter.featureOfInterest:
            sqlWhere += " AND id_foi=id_foi_fk AND id_fty=id_fty_fk AND (name_foi='%s')" %(filter.featureOfInterest)
        if filter.featureOfInterestSpatial:
            sqlWhere += " AND id_foi_fk=id_foi AND %s" %(filter.featureOfInterestSpatial)
        
        #---where condition based on procedures
        if filter.procedure:
            sqlWhere += " AND ("
            procWhere = []
            for proc in filter.procedure:
                procWhere.append("name_prc='%s'" %(proc))
            sqlWhere += " OR ".join(procWhere)
            sqlWhere += ")"
        
        #---where condition based on observed properties
        sqlWhere += " AND ("
        obsprWhere = []
        for obs in opr_filtered:
            obsprWhere.append("def_opr='%s'" %(obs["def_opr"])) 
        sqlWhere += " OR ".join(obsprWhere)
        sqlWhere += ")"
        
        try:
            res = pgdb.select(sqlSel + " " + sqlFrom + " " + sqlWhere)
        except:
            raise sosException.SOSException(3,"SQL: %s"%(sqlSel + " " + sqlFrom + " " + sqlWhere))
        
        #FOR EACH PROCEDURE
        #=========================================
        for o in res:
            #id_prc, name_prc, name_oty, stime_prc, etime_prc, time_res_prc, name_tru
            
            #CRETE OBSERVATION OBJECT
            #=================================================
            ob = Observation()
            
            #BUILD BASE INFOS FOR EACH PROCEDURE (Pi)
            #=================================================
            ob.baseInfo(pgdb,o,filter.sosConfig)
            
            #GET DATA FROM PROCEDURE ACCORDING TO THE FILTERS
            #=================================================
            ob.setData(pgdb,o,filter)
            
            #ADD OBSERVATIONS
            #=================================================
            self.obs.append(ob)
            
            
