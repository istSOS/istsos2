# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301  USA
#
# ===============================================================================

import os
import sys
from abc import ABC, abstractmethod
import copy
import datetime
from datetime import timedelta
import isodate as iso
import pytz
import importlib
import traceback
from operator import add
from dateutil.parser import parse

from istsoslib import sosException
from ..utils import escape

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else float(obj)
)


class VirtualProcess(ABC):
    """Virtual procedure object

    Attributes:
        filter (obj): the filter object
        pgdb (obj): the database connection object
        procedure (dict): representation of the procedure
        observation (obj): observation object
        samplingTime (tuple): sampling time bounds

    """

    procedures = {}
    offering = None
    samplingTime = (None, None)
    obs_input = [':']

    def _configure(self, filterRequest, pgdb, props=None):
        """Configure base object"""
        self.filter = copy.deepcopy(filterRequest)
        self.pgdb = pgdb
        if props:
            self.coords = props['coords']
            self.obs = props['obs']
            self.name = props['name']

    def addProcedure(self, name, observedProperty):
        """Add a procedure to the self.procedures[name]
        Args:
            name (str): name of procedure
            observedProperty (str/list): uri or uris of observed properties
        """
        self.procedures[name] = observedProperty

    @abstractmethod
    def execute(self):
        "This method must be overridden to implement data gathering for this virtual procedure"
        raise Exception("function execute must be overridden")

    def calculateObservations(self, observation):
        """Calculate the observations of the virtual procedure"""
        self.observation = observation
        self.observation.samplingTime = self.getSampligTime()
        self.observation.data = self.execute()
        if self.filter.aggregate_interval is not None:
            self.applyFunction()

    def getSampligTime(self):
        """Extract sampling time of Virtual procedure"""
        self.setSampligTime()
        return self.samplingTime

    def setSampligTime(self):
        """
        This method can be overridden to set the virtual procedure sampling time
        *************************************************************************
        By default This method calculate the sampling time of a virtual procedure
        giving the procedure name from witch the data are derived
        as single string or array of strings.

        If derivation procedures are more than one it will return the minimum
        begin position and the maximum end position among all the procedures
        name given.

        It supports also SamplingTime calculation from cascading Virtual Procedures.
        """
        if self.offering:
            self.proc_info = self.getProceduresFromOffering(self.offering)
        if len(self.procedures) == 0:
            self.samplingTime = (None, None)
        else:

            # Identify if procedures are virtual
            if isinstance(self.procedures, list):
                tmp = self.procedures
            else:
                tmp = list(self.procedures.keys())
            procedures = []

            # Handle cascading virtual procedures
            for p in tmp:

                sql = """
                    SELECT name_oty
                    FROM %s.obs_type, %s.procedures
                    WHERE id_oty=id_oty_fk""" % ((self.filter.sosConfig.schema,)*2)
                sql += " AND name_prc = %s"

                result = self.pgdb.select(sql, (p,))

                if len(result)==0:
                    raise sosException.SOSException(
                        "InvalidParameterValue",
                        "procedure",
                        "Virtual Procedure Error: procedure %s not found in the database" % (p)
                    )

                result = result[0]

                if result[0] == 'virtual':
                    vpFolder = os.path.join(self.filter.sosConfig.virtual_processes_folder,p)
                    try:
                        if vpFolder not in sys.path:
                            sys.path.append(vpFolder)

                    except Exception as e:
                        raise Exception("error in loading virtual procedure path (%s):\n%s" % (vpFolder,e))

                    # check if python file exist
                    if os.path.isfile("%s/%s.py" % (vpFolder,p)):
                        vproc = importlib.import_module(p)
                        # exec("import %s as vproc" %(p))
                        vp = vproc.istvp()
                        if len(vp.procedures)>0:
                            # Add data source of virtual procedure
                            tmp.extend(list(vp.procedures.keys()))

                else:
                    procedures.append(p)

            # removing duplicates
            procedures = list(set(procedures))

            pnf = [] # procedures_not_found
            for procedure in procedures:
                sql = """
                  SELECT COUNT(*) FROM %s.procedures
                """ % self.filter.sosConfig.schema
                sql += " WHERE name_prc=%s"
                result = self.pgdb.select(sql, (procedure,))
                if result[0] == 0:
                    pnf.append(procedure)

            if len(pnf)>0:
                raise Exception("Virtual Procedure Error: procedure %s not found in the database" % (", ".join(pnf)) )

            if len(procedures)>1:
                sql = """
                    SELECT min(stime_prc), max(etime_prc)
                    FROM %s.procedures
                    WHERE (stime_prc IS NOT NULL
                    AND etime_prc IS NOT NULL)
                    AND (
                """ % self.filter.sosConfig.schema
                sql += " OR ".join(["name_prc=%s"] * len(procedures))
                sql += ") GROUP BY stime_prc, etime_prc"
                param = tuple(procedures)

            else:
                sql = """
                    SELECT stime_prc, etime_prc
                    FROM %s.procedures
                    WHERE (stime_prc IS NOT NULL
                    AND etime_prc IS NOT NULL)
                """ % self.filter.sosConfig.schema
                sql += "AND name_prc=%s"
                param = (procedures[0],)

            try:
                result = self.pgdb.select(sql, param)
                if len(result)==0:
                    result = [None, None]

                else:
                    result = result[0]

            except Exception as e:
                raise Exception("Database error: %s - %s" % (sql, e))

            self.samplingTime = (result[0], result[1])

    def getProceduresFromOffering(self, offering):
        sql = """
            SELECT id_prc, name_prc, st_z(geom_foi), array_agg(def_opr)
            FROM (
                (
                    SELECT *
                    FROM (
                        SELECT
                            *
                        FROM %s.procedures
                        JOIN %s.proc_obs
                        ON id_prc = id_prc_fk
                    ) p1 JOIN %s.observed_properties ON id_opr = id_opr_fk
                ) p2 JOIN %s.off_proc ON off_proc.id_prc_fk = id_prc
            ) p3 JOIN %s.offerings ON id_off = p3.id_off_fk, %s.foi """ % (
                (self.filter.sosConfig.schema,)*6
            )
        sql += """
            WHERE id_foi = p3.id_foi_fk AND name_off = \'%s\' AND name_prc != \'%s\'
            GROUP BY id_prc, name_prc, geom_foi
            ORDER BY st_z DESC""" % (offering, self.filter.procedure[0])

        try:
            result = self.pgdb.select(sql)
            self.procedures = {}

            if len(result) == 0:
                raise Exception("Virtual Procedure Error: procedure %s not found in the database" % procedure)
            else:
                for res in result:
                    self.procedures[res[1]] = res[3]
            # result = result[0]
            return result

        except Exception as e:
            raise Exception("Database error: %s - %s" % (sql, e))

    def getData(self, procedure=None, disableAggregation=True):
        """Return the observations of associated procedure

		Args:
        	procedure (str): the procedure name
			disableAggregation (bbol): apply aggregation (True) or not (False)
        """

        # Validating:
        # If procedure is None, it is supposed that only one procedure has been added
        if procedure is None:
            if len(self.procedures)==0:
                raise Exception("Virtual Procedure Error: no procedures added")

            procedure = list(self.procedures.keys())[0]

        elif procedure not in list(self.procedures.keys()):
            raise Exception("Virtual Procedure Error: procedure %s has not been added to this virtual procedure" % procedure)

        virtualFilter = copy.deepcopy(self.filter)
        virtualFilter.procedure = [procedure]
        virtualFilter.observedProperty = self.procedures[procedure]

        sql = """
            SELECT DISTINCT id_prc, name_prc, name_oty,
                stime_prc, etime_prc, time_res_prc
            FROM
                %s.procedures,
                %s.proc_obs p,
                %s.observed_properties,
                %s.uoms,
                %s.obs_type """ % ((self.filter.sosConfig.schema,)*5 )
        sql += """
                WHERE id_prc = p.id_prc_fk
                AND id_opr_fk = id_opr
                AND id_uom = id_uom_fk
                AND id_oty = id_oty_fk
                AND name_prc=%s"""

        try:
            result = self.pgdb.select(sql, (procedure,))
            if len(result)==0:
                raise Exception("Virtual Procedure Error: procedure %s not found in the database" % procedure)

            result = result[0]

        except Exception as e:
            raise Exception("Database error: %s - %s" % (sql, e))

        obs = Observation()
        obs.baseInfo(self.pgdb, result, virtualFilter.sosConfig)

        if disableAggregation:
            virtualFilter.aggregate_function = None
            virtualFilter.aggregate_interval = None

        obs.setData(self.pgdb, result, virtualFilter)

        return obs.data

    def applyFunction(self):
        """apply virtual procedure function"""
        try:
            # Create array container
            begin = iso.parse_datetime(self.filter.eventTime[0][0])
            end = iso.parse_datetime(self.filter.eventTime[0][1])
            duration = iso.parse_duration(self.filter.aggregate_interval)
            result = {}
            dt = begin
            # + 1 # +1 timestamp field not mentioned in the
            # observedProperty array
            fields = len(self.observation.observedProperty)

            while dt < end:
                dt2 = dt + duration
                result[dt2] = []
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
            raise Exception("Error while applying aggregate function on virtual procedures: %s" % (e))


class VirtualProcessProfile(VirtualProcess):

    def observed_properties(self, offering):
        sql = """
            SELECT array_agg(def_opr)
            FROM (
                (
                    SELECT *
                    FROM (
                        SELECT
                            *
                        FROM %s.procedures
                        JOIN %s.proc_obs
                        ON id_prc = id_prc_fk
                    ) p1 JOIN %s.observed_properties ON id_opr = id_opr_fk
                ) p2 JOIN %s.off_proc ON off_proc.id_prc_fk = id_prc
            ) p3 JOIN %s.offerings ON id_off = p3.id_off_fk, %s.foi """ % (
                (self.filter.sosConfig.schema,)*6
            )
        sql += """
            WHERE id_foi = p3.id_foi_fk AND name_off = \'%s\' AND name_prc = \'%s\'
            """ % (offering, self.filter.procedure[0])

        try:
            result = self.pgdb.select(sql)
            self.procedures = {}

            if len(result) == 0:
                raise Exception("Virtual Procedure Error: procedure %s not have observed properties" % procedure)
            # result = result[0]
            return result[0]

        except Exception as e:
            raise Exception("Database error: %s - %s" % (sql, e))

    def getProceduresInfo(self):
        proc_sql = ('\' OR name_prc=\'').join(self.procedures)
        sql_filter = ' WHERE name_prc=\'' + proc_sql + '\' '
        sql = """
            SELECT id_prc, name_prc, st_z(geom_foi), array_agg(def_opr)
            FROM ((
            SELECT *
            FROM
            (
                SELECT
                    *
                FROM %s.procedures
                JOIN %s.proc_obs
                ON id_prc = id_prc_fk""" % ((self.filter.sosConfig.schema,)*2)

        sql += sql_filter
        sql += """
            ) p1 JOIN %s.observed_properties ON id_opr = id_opr_fk
            ) p2 JOIN %s.off_proc ON off_proc.id_prc_fk = id_prc
            ) p3 JOIN %s.offerings ON id_off = p3.id_off_fk, demo.foi
            WHERE id_foi = p3.id_foi_fk GROUP BY id_prc, name_prc, geom_foi
            ORDER BY st_z DESC""" % ((self.filter.sosConfig.schema,)*3)
        try:
            result = self.pgdb.select(sql)

            if len(result) == 0:
                raise Exception(
                    "Virtual Procedure Error: procedure %s not found in the database"
                    % procedure
                )
            self.procedures = {}
            for res in result:
                self.procedures[res[1]] = res[3]

            # result = result[0]
            return result

        except Exception as e:
            raise Exception("Database error: %s - %s" % (sql, e))

    def execute(self):
        try:
            procs_info = self.proc_info
        except Exception as e:
            procs_info = self.getProceduresInfo()
        if self.offering:
            obs = self.observed_properties(self.filter.offering)
        else:
            obs = self.observed_properties(self.filter.offering)
        data = []
        # start_time = time.time()
        for proc in procs_info:
            check = False
            obs_tmp = []
            for i in range(len(obs)):
                if obs[i] in proc[3]:
                    obs_tmp.append(obs[i])
            proc[3] = obs_tmp
            if check:
                raise Exception('Procedure does not measure the required observed properties.')
            else:
                self.procedures[proc[1]] = self.obs_input
                data_temp = self.getData(proc[1])
                if data_temp:
                    if self.filter.qualityIndex is True:
                        depths_list = [
                            [round(abs(self.coords[2] - proc[2]), 1), 100]
                        ] * len(data_temp)

                    else:
                        depths_list = [
                            [round(abs(self.coords[2] - proc[2]), 1)]
                        ] * len(data_temp)

                    data_temp = list(
                        map(add, data_temp, depths_list)
                    )
                    data = data + data_temp

        data.sort(key=lambda row: row[0])
        if self.filter.qualityIndex is True:
            data.sort(key=lambda row: row[4], reverse=True)

        else:
            data.sort(key=lambda row: row[3], reverse=True)

        if len(self.obs) != (len(data[0]) - 1):
            raise Exception("Number of observed properties mismatches")

        return data


class VirtualProcessHQ(VirtualProcess):

    def setDischargeCurves(self):
        "method for setting h-q tranformation tables/curves"
        # set requested period
        hqFile = os.path.join(
            self.filter.sosConfig.virtual_processes_folder,
            self.observation.name,
            "%s.rcv" % self.observation.name
        )
        tp=[]
        if self.filter.eventTime == None:
            tp = [None,None]

        else:
            for t in self.filter.eventTime:
                if len(t) == 2:
                    if t[0].find('+')==-1 and t[0][:-8].find('-')== -1:
                        t[0] += "+00:00"
                    if t[1].find('+')==-1 and t[0][:-8].find('-')== -1:
                        t[1] += "+00:00"
                    tp.append(iso.parse_datetime(t[0]))
                    tp.append(iso.parse_datetime(t[1]))

                if len(t)==1:
                    if t[0].find('+')==-1 and t[0][:-8].find('-')== -1:
                        t[0] += "+00:00"

                    tp.append(iso.parse_datetime(t[0]))

        period = (min(tp),max(tp))
        # get required parameters
        try:
            hq_fh = open(hqFile,'r')
        except Exception as e:
            raise Exception("Unable to open hq rating curve file at: %s" % hqFile)
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
            raise Exception("setDischargeCurves: FILE %s ,%s error in header.\n %s" %(hqFile,head,e))

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

        self.hqCurves = hqs

    def execute(self):
        """execute method"""
        self.setDischargeCurves()
        data = self.getData()

        if self.filter.qualityIndex == True:
            data_out=[]
            for rec in data:
                if rec[1] is None or (float(rec[1])) < -999.0:
                    data_out.append([ rec[0], -999.9, 110 ])

                else:
                    for o in range(len(self.hqCurves['from'])):
                        if rec[1] == None:
                            data_out.append([ rec[0], -999.9, 120 ])
                            break

                        elif (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] <= float(rec[1]) < self.hqCurves['up'][o]):
                            if (float(rec[1])-self.hqCurves['B'][o]) >=0:
                                data_out.append([ rec[0], "%.4f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])), rec[2] ])

                            else:
                                data_out.append([ rec[0], -999.9, 120 ])

                            break

                        if o == ( len(self.hqCurves['from']) -1):
                            data_out.append([ rec[0], -999.9, 120 ])

        else:
            data_out=[]
            for rec in data:
                for o in range(len(self.hqCurves['from'])):
                    if rec[1] == None:
                        data_out.append([ rec[0], -999.9 ])
                        break

                    elif (self.hqCurves['from'][o] < rec[0] <= self.hqCurves['to'][o]) and (self.hqCurves['low'][o] <= float(rec[1]) < self.hqCurves['up'][o]):
                        if (float(rec[1])-self.hqCurves['B'][o]) >=0:
                            data_out.append([ rec[0], "%.4f" %(self.hqCurves['K'][o] + self.hqCurves['A'][o]*((float(rec[1])-self.hqCurves['B'][o])**self.hqCurves['C'][o])) ])

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
    sql = "SELECT distinct(def_opr) as nopr, p.id_pro FROM %s.procedures, %s.proc_obs p," %(sosConfig.schema,sosConfig.schema)
    sql += " %s.observed_properties, %s.off_proc o, %s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_opr_fk=id_opr AND p.id_prc_fk=id_prc AND o.id_prc_fk=id_prc AND id_off=id_off_fk"
    sql += " AND name_off='%s' ORDER BY p.id_pro" %(offering)

    # TODO:
    #  IGRAC SPECIALIZED
    sql = f"select distinct(def_opr) as nopr from istsos.observed_properties"
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
        raise Exception("sql: %s" %(sql))

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


def BuildProcedureCount(pgdb,offering, procedures, sosConfig):
    sql = "SELECT name_prc FROM %s.procedures, %s.off_proc, %s.offerings"  %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += f''' WHERE id_prc=id_prc_fk AND id_off=id_off_fk AND name_off='{offering}' AND name_prc IN ({','.join([f"'{procedure}'" for procedure in procedures])})'''
    sql += " ORDER BY name_prc"
    rows=pgdb.select(sql)

    return len(rows)

def BuildOfferingList(pgdb,sosConfig):
    list=[]
    sql = "SELECT distinct(name_off) FROM %s.offerings" %(sosConfig.schema,)
    rows=pgdb.select(sql)
    for row in rows:
        list.append(row["name_off"])
    return list


def applyFunction(ob, filter):
    """apply H-Q function"""
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
        raise Exception("Error while applying aggregate function on virtual procedures: %s" % (e))


class offInfo:
    def __init__(self, off_name, pgdb, sosConfig):
        sql = "SELECT name_off, desc_off FROM %s.offerings WHERE name_off='%s'"  % (sosConfig.schema, off_name)
        try:
            off = pgdb.select(sql)[0]
            self.name=off["name_off"]
            self.desc=off["desc_off"]

        except:
            raise sosException.SOSException("InvalidParameterValue", "offering",
                "Parameter \"offering\" sent with invalid value: %s" % (off_name))


# @todo instantation with Builder pattern will be less confusing, observation class must be just a data container
class Observation:
    """The obsevation related to a single procedure

    Attributes:
        id_prc (str): the internal id of the selected procedure
        name (str): the name of the procedure
        procedure (str): the URI name of the procedure
        procedureType (str): the type of procedure (one of "insitu-fixed-point","insitu-fixed-specimen","insitu-mobile-point","virtual")
        samplingTime (list): the time interval for which this procedure has data [*from*, *to*]
        timeResVal (str): the time resolution setted for this procedure when registered in ISO 8601 duration
        observedPropertyName (list): list of observed properties names as string
        observedProperty (list): list of observed properties URI as string
        uom (list): list of unit of measure associated with the observed properties according to list index
        featureOfInterest (str): the feature of interest name
        foi_urn (str): the feature of interest URI
        foiGml (str): the GML representation of the feature of interest (in istSOS is only of type POINT)
        srs (str): the epsg code
        refsys (str): the URI of the reference system (srs)
        x (float): the X coordinate
        y (float): the Y coordinate
        dataType (str): the URN used for timeSeries data type
        timedef (str): URI of the time observed propertiy
        data (list): the list of observations as list of values (it is basically a matrix with fields as columns and measurements as rows)
    """


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
        self.csv=None

    def baseInfo(self, pgdb, row, sosConfig):
        """set base information of registered procedure"""

        k = list(row.keys())
        if not ("id_prc" in k and "name_prc" in k and  "name_oty" in k and "stime_prc" in k and "etime_prc" in k and "time_res_prc" in k  ):
            raise Exception("Error, baseInfo argument: %s"%(row))

        # SET PROCEDURE NAME AND ID
        self.id_prc=row["id_prc"]
        self.name = row["name_prc"]
        self.procedure = sosConfig.urn["procedure"] + row["name_prc"]

        # CHECK & SET PROCEDURE TYPE
        if row["name_oty"].lower() in [
            "insitu-fixed-point",
            "insitu-fixed-specimen",
            "insitu-mobile-point",
            "virtual"]:
            self.procedureType=row["name_oty"]
        else:
            raise Exception("error in procedure type setting")

        # SET TIME: RESOLUTION VALUE AND UNIT
        self.timeResVal = row["time_res_prc"]

        # SET SAMPLING TIME
        if row["stime_prc"]!=None and row["etime_prc"]!=None:
            self.samplingTime=[row["stime_prc"],row["etime_prc"]]

        else:
            self.samplingTime = None

        self.dataType = sosConfig.urn["dataType"] + "timeSeries"
        self.timedef = sosConfig.urn["parameter"] + "time:iso8601"
        self.qualitydef = None


    def setData(self, pgdb, row, filter):
        """get data according to request filters"""

        # SET FOI OF PROCEDURE
        sqlFoi  = "SELECT name_fty, name_foi, ST_AsGml(ST_Transform(geom_foi,%s)) as gml, st_x(geom_foi) as x, st_y(geom_foi) as y, st_z(geom_foi) as z " %(filter.srsName)
        sqlFoi += " FROM %s.procedures, %s.foi, %s.feature_type" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sqlFoi += " WHERE id_foi_fk=id_foi AND id_fty_fk=id_fty AND id_prc=%s" %(row["id_prc"])
        try:
            resFoi = pgdb.select(sqlFoi)

        except:
            raise Exception("SQL: %s"%(sqlFoi))

        self.featureOfInterest = resFoi[0]["name_foi"]
        self.foi_urn = filter.sosConfig.urn["feature"] + resFoi[0]["name_fty"] + ":" + resFoi[0]["name_foi"]
        srs = filter.srsName or filter.sosConfig.istsosepsg
        if resFoi[0]["gml"].find("srsName")<0:
            self.foiGml = resFoi[0]["gml"][:resFoi[0]["gml"].find(">")] + " srsName=\"EPSG:%s\"" % srs + resFoi[0]["gml"][resFoi[0]["gml"].find(">"):]

        else:
            self.foiGml = resFoi[0]["gml"]

        self.srs = srs
        self.x = resFoi[0]["x"]
        self.y = resFoi[0]["y"]
        self.z = resFoi[0]["z"]

        # SET INFORMATION ABOUT OBSERVED_PROPERTIES
        sqlObsPro = "SELECT id_pro, id_opr, name_opr, def_opr, name_uom FROM %s.observed_properties, %s.proc_obs, %s.uoms" %(filter.sosConfig.schema,filter.sosConfig.schema,filter.sosConfig.schema)
        sqlObsPro += " WHERE id_opr_fk=id_opr AND id_uom_fk=id_uom AND id_prc_fk=%s" %(row["id_prc"])
        sqlObsPro += " AND ("
        sqlObsPro += " OR ".join(["def_opr='" + str(i) + "'" for i in filter.observedProperty])
        sqlObsPro += " ) ORDER BY id_pro ASC"
        try:
            obspr_res = pgdb.select(sqlObsPro)

        except:
            raise Exception("SQL: %s"%(sqlObsPro))

        self.observedProperty = []
        self.observedPropertyId = []
        self.observedPropertyName = []
        self.opr_urn = []
        self.uom = []
        self.qualityIndex = filter.qualityIndex

        for orRow in obspr_res:
            self.observedProperty += [str(orRow["def_opr"])]
            self.observedPropertyId += [str(orRow["id_opr"])]
            self.observedPropertyName +=[str(orRow["name_opr"])]
            self.opr_urn += [str(orRow["def_opr"])]
            try:
                self.uom += [orRow["name_uom"]]

            except:
                self.uom += ["n/a"]

            if self.qualityIndex==True:
                self.observedProperty += [str(orRow["def_opr"])+":qualityIndex"]
                self.observedPropertyId += [str(-orRow["id_opr"])]
                self.observedPropertyName += [str(orRow["name_opr"])+":qualityIndex"]
                self.opr_urn += [str(orRow["def_opr"] +":qualityIndex")]
                self.uom += ["-"]

        # SET DATA
        #  CASE is not virtual #"insitu-fixed-point", "insitu-mobile-point" or "insiru-fixed-specimen"
        if self.procedureType != "virtual":

            sqlSel = "SELECT "

            csv_sql_cols = [
                "row_to_json(row(time_eti))->>'f1'"
            ]
            if 'text/plain' == filter.responseFormat:
                csv_sql_cols.append("'%s'" % self.name)

            csv_sql_sel = """
                SELECT
            """
            joinar=[]
            cols=['et.time_eti as t']

            aggrCols=["row_to_json(row(ts.sint))->>'f1' as t"]
            csv_aggr_cols=["row_to_json(row(ts.sint))->>'f1'"]
            if 'text/plain' == filter.responseFormat:
                csv_aggr_cols.append("'%s'" % self.name)

            aggrNotNull=[]

            valeFieldName = []
            qi_field_name = []

            multi_obs = len(obspr_res) > 1

            for idx, obspr_row in enumerate(obspr_res):
                key = f'C{idx}'
                if not multi_obs:
                    key = 'et'

                if self.qualityIndex==True:

                    cols += [
                        "%s.val_msr as %s_v" % (key, key),
                        "COALESCE(%s.id_qi_fk, %s) as %s_qi" % (
                            key,
                            filter.aggregate_nodata_qi,
                            key
                        )
                    ]
                    csv_sql_cols += [
                        "COALESCE(%s.val_msr, %s)" % (key, filter.aggregate_nodata),
                        "COALESCE(%s.id_qi_fk, %s)" % (key, filter.aggregate_nodata_qi)
                    ]

                    valeFieldName.append("c%s_v" %(idx))
                    valeFieldName.append("c%s_qi" %(idx))
                    qi_field_name.append("C%s.id_qi_fk" %(idx))

                else:
                    cols.append("%s.val_msr as c%s_v" %(key,idx))
                    csv_sql_cols.append("%s.val_msr" %(key))
                    valeFieldName.append("%s_v" %(key))

                # If Aggregatation funtion is set
                if filter.aggregate_interval != None:
                    # This accept only numeric results
                    aggrCols.append(
                        "COALESCE(%s(nullif(dt.%s_v, 'NaN')),'%s')" % (
                            filter.aggregate_function,
                            key,
                            filter.aggregate_nodata
                        )
                    )
                    csv_aggr_cols.append(
                        "COALESCE(%s(nullif(dt.%s_v, 'NaN')),'%s')" % (
                            filter.aggregate_function,
                            key,
                            filter.aggregate_nodata
                        )
                    )
                    if self.qualityIndex==True:
                        aggrCols.append("COALESCE(MIN(dt.%s_qi),%s) as %s_qi\n" % (
                            key,
                            filter.aggregate_nodata_qi,
                            key
                        ))
                        csv_aggr_cols.append("COALESCE(MIN(dt.%s_qi),%s)" % (
                            key,
                            filter.aggregate_nodata_qi
                        ))

                    aggrNotNull.append(" %s_v > -900 " %(key))

                if multi_obs:
                    # Set SQL JOINS
                    join_txt = """
                        JOIN (
                            SELECT
                                A%s.id_msr,
                                A%s.val_msr,
                                A%s.id_eti_fk
                    """ % (idx, idx, idx)

                    if self.qualityIndex==True:
                        join_txt += ", A%s.id_qi_fk\n" %(idx)

                    join_txt += """
                            FROM
                                %s.measures A%s
                            WHERE
                                A%s.id_pro_fk = '%s'
                    """ % (
                        filter.sosConfig.schema, idx,
                        idx, obspr_row["id_pro"]
                    )

                    # ATTENTION: HERE -999 VALUES ARE EXCLUDED WHEN ASKING AN AGGREAGATE FUNCTION
                    if filter.aggregate_interval != None: # >> Should be removed because measures data is not inserted if there is a nodata value
                        join_txt += " AND A%s.val_msr > -900 " % idx

                    # close SQL JOINS
                    join_txt += " ) as C%s\n" %(idx)
                    join_txt += " on C%s.id_eti_fk = et.id_eti" %(idx)
                    joinar.append(join_txt)


            # Set FROM CLAUSE
            table = f'{filter.sosConfig.schema}.event_time'
            if not multi_obs:
                table = 'istsos.measures'

            sqlSel += "%s FROM %s et" % (
                ", ".join(cols), table
            )

            # Set FROM CLAUSE
            csv_sql_sel += "%s FROM %s et" % (
                (
                    ",".join(cols)
                    if filter.aggregate_interval != None
                    else " || ',' || ".join(csv_sql_cols)
                ),
                table
            )

            # Set WHERE CLAUSES
            sqlData = " ".join(joinar)
            sqlData += " WHERE et.id_prc_fk=%s\n" %(row["id_prc"])
            if not multi_obs:
                sqlData += f""" AND  et.id_pro_fk = '{obspr_row["id_pro"]}'"""

            # Set FILTER ON RESULT (OGC:COMPARISON)
            if filter.result:
                for ind, ov in enumerate(self.observedProperty):
                    if ov.find(filter.result[0])>0:
                        sqlData += " AND C%s.val_msr %s" %(ind,filter.result[1])

            # Set FILTER ON EVENT-TIME
            if filter.eventTime:
                sqlData += " AND ("
                etf=[]
                for ft in filter.eventTime:
                    if len(ft)==2:
                        etf.append("et.time_eti > timestamptz '%s' AND et.time_eti <= timestamptz '%s' " %(ft[0],ft[1]))

                    elif len(ft)==1:
                        etf.append("et.time_eti = timestamptz '%s' " %(ft[0]))

                    else:
                        raise Exception("error in time filter")

                sqlData += " OR ".join(etf)
                sqlData +=  ")\n"

            # TODO: IGRAC Custom
            # else:
            #     # Get last observed measuement
            #     sqlData += " AND et.time_eti = (SELECT max(time_eti) FROM %s.event_time WHERE id_prc_fk=%s) " %(filter.sosConfig.schema,row["id_prc"])

            # Quality index filtering
            if (
                self.qualityIndex==True and
                filter.qualityFilter
            ):
                if filter.qualityFilter[0]=='<':
                    qi_sql = []
                    for qi_field in qi_field_name:
                        qi_sql.append(
                            " %s < %s " % (
                                qi_field,
                                filter.qualityFilter[1]
                            )
                        )
                    sqlData += " AND (%s)" % " AND ".join(qi_sql)

                elif filter.qualityFilter[0]=='>':
                    qi_sql = []
                    for qi_field in qi_field_name:
                        qi_sql.append(
                            " %s > %s " % (
                                qi_field,
                                filter.qualityFilter[1]
                            )
                        )
                    sqlData += " AND (%s)" % " AND ".join(qi_sql)

                elif filter.qualityFilter[0]=='>=':
                    qi_sql = []
                    for qi_field in qi_field_name:
                        qi_sql.append(
                            " %s >= %s " % (
                                qi_field,
                                filter.qualityFilter[1]
                            )
                        )
                    sqlData += " AND (%s)" % " AND ".join(qi_sql)

                elif filter.qualityFilter[0]=='<=':
                    qi_sql = []
                    for qi_field in qi_field_name:
                        qi_sql.append(
                            " %s <= %s " % (
                                qi_field,
                                filter.qualityFilter[1]
                            )
                        )
                    sqlData += " AND (%s)" % " AND ".join(qi_sql)

                elif filter.qualityFilter[0]=='=':
                    qi_sql = []
                    for qi_field in qi_field_name:
                        qi_sql.append(
                            " %s = %s " % (
                                qi_field,
                                filter.qualityFilter[1]
                            )
                        )
                    sqlData += " AND (%s)" % " OR ".join(qi_sql)
                elif filter.qualityFilter[0]=='~*':
                    qi_sql = []
                    for qi_field in qi_field_name:
                        qi_sql.append(
                            " %s::text ~* \'%s\' " % (
                                qi_field,
                                filter.qualityFilter[1]
                            )
                        )
                    sqlData += " AND (%s)" % " OR ".join(qi_sql)

            sqlData += " ORDER by et.time_eti"

            sql = sqlSel + sqlData
            csv_sql = csv_sql_sel + sqlData

            if filter.aggregate_interval != None:
                self.aggregate_function = filter.aggregate_function.upper()

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
                    if isoInt.years>0:
                        sqlInt += "%s years " % isoInt.years

                    if isoInt.months>0:
                        sqlInt += "%s months " % int(isoInt.months)

                    if isoInt.days>0:
                        sqlInt += "%s days " % isoInt.days

                    if isoInt.seconds>0:
                        sqlInt += "%s seconds " % isoInt.seconds

                # @todo improve this part
                # calculate how many step are included in the asked interval.
                hopBefore = 1
                hop = 0
                tmpStart = iso.parse_datetime(filter.eventTime[0][0])
                tmpEnd = self.samplingTime[1]

                while (tmpStart+isoInt)<=tmpEnd and (tmpStart+isoInt)<=iso.parse_datetime(filter.eventTime[0][1]):

                    if tmpStart <  self.samplingTime[0]:
                        hopBefore+=1
                        hop+=1

                    elif (tmpStart >= self.samplingTime[0]) and ((tmpStart+isoInt)<=self.samplingTime[1]):
                        hop+=1

                    tmpStart=tmpStart+isoInt

                aggr_sql = """
                    SELECT
                        %s
                    FROM (
                        SELECT
                            (
                                '%s'::TIMESTAMP WITH TIME ZONE +
                                s.a *
                                '%s'::interval
                            )::TIMESTAMP WITH TIME ZONE as sint
                        FROM
                            generate_series(%s, %s) as s(a)
                    ) as ts

                    LEFT JOIN ( 
                        %s
                    ) as dt
                    ON (
                        dt.t > (ts.sint-'%s'::interval)
                        AND dt.t <= (ts.sint)
                    )

                    GROUP BY ts.sint
                    ORDER BY ts.sint
                """

                sql = aggr_sql % (
                    ", ".join(aggrCols),
                    filter.eventTime[0][0],
                    sqlInt,
                    hopBefore,
                    hop,
                    sql,
                    sqlInt
                )

                if filter.responseFormat in [
                    'text/plain',
                    'text/xml;subtype="om/1.0.0"',
                    'text/xml'
                ]:
                    csv_sql = aggr_sql % (
                        " || ',' || ".join(csv_aggr_cols),
                        filter.eventTime[0][0],
                        sqlInt,
                        hopBefore,
                        hop,
                        csv_sql,
                        sqlInt
                    )

            else:
                self.aggregate_function = None


            try:
                a = datetime.datetime.now()

                if 'text/plain' == filter.responseFormat:
                    self.data = pgdb.select(sql)
                    self.csv = pgdb.to_string(csv_sql)

                elif filter.responseFormat in [
                    'text/xml;subtype="om/1.0.0"',
                    "text/xml"
                ]:
                    self.csv = pgdb.to_string(csv_sql, lineterminator='@')
                    self.data = []
                else:
                    self.data = pgdb.select(sql)

            except Exception as xx:
                print(traceback.print_exc(), file=sys.stderr)
                # sys.stderr.flush()
                raise Exception("SQL: %s"%(sql))

        # CASE "virtual"
        elif self.procedureType in ["virtual"]:

            self.aggregate_function = filter.aggregate_function
            self.aggregate_interval = filter.aggregate_interval
            self.aggregate_nodata = filter.aggregate_nodata
            self.aggregate_nodata_qi = filter.aggregate_nodata_qi

            vpFolder = os.path.join(os.path.join(filter.sosConfig.virtual_processes_folder,self.name))

            if not os.path.isfile("%s/%s.py" % (vpFolder,self.name)):
                raise Exception(
                    "Virtual procedure folder does not contain "
                    "any Virtual Procedure code for %s" % self.name
                )

            #----- VIRTUAL PROCESS LOADING -----
            try:
                sys.path.append(vpFolder)
            except:
                raise Exception("error in loading virtual procedure path")
            #import procedure process
            # exec("import %s as vproc" %(self.name))
            vproc = importlib.import_module(self.name)

            # Initialization of virtual procedure will load the source data
            vp = vproc.istvp()
            props = {
                "name": self.name,
                "coords": [self.x, self.y, self.z],
                "obs": self.observedProperty
            }
            vp._configure(filter, pgdb, props)

            # Calculate virtual procedure data
            vp.calculateObservations(self)


class GetObservationResponse:
    """The class that contain all the observations related to all the procedures

    Attributes:
        offInfo (obj): the general information about offering name, connection object, and configuration options
        refsys (str): the uri that refers to the EPSG refrence system
        filter (obj): the filter object that contains all the parameters setting of the GetObservation request
        period (list): a list of two values in *datetime*: the minimum and maximum instants of the requested time filters
        reqTZ (obj): the timezone in *pytz.tzinfo*
        obs (list): list of *Observation* objects
    """

    def __init__(self, filter, pgdb):
        self.offInfo = offInfo(filter.offering, pgdb, filter.sosConfig)
        self.refsys = filter.sosConfig.urn["refsystem"] + filter.srsName
        self.filter = filter

        # CHECK FILTER VALIDITY
        """
        off_list = BuildOfferingList(pgdb,filter.sosConfig)
        if not filter.offering in off_list:
            raise sosException.SOSException("InvalidParameterValue","offering","Parameter \"offering\" sent with invalid value: %s -  available options for offering are %s" %(filter.offering,off_list))
        """
        if filter.procedure:
            # IGRAC SPECIFIED
            pl = BuildProcedureCount(pgdb, filter.offering, filter.procedure, filter.sosConfig)
            if not pl:
                raise sosException.SOSException("InvalidParameterValue","procedure","Parameter \"procedure\" sent with invalid value")

        if filter.featureOfInterest:
            fl = BuildfeatureOfInterestList(pgdb,filter.offering, filter.sosConfig)
            if not filter.featureOfInterest in fl:
                raise sosException.SOSException("InvalidParameterValue","featureOfInterest","Parameter \"featureOfInterest\" sent with invalid value: %s - available options: %s"%(filter.featureOfInterest,fl))

        if filter.observedProperty:
            opl = BuildobservedPropertyList(pgdb, filter.offering, filter.sosConfig)
            opr_sel = "SELECT def_opr FROM %s.observed_properties WHERE " %(filter.sosConfig.schema,)
            opr_sel_w = []
            for op in filter.observedProperty:
                opr_sel_w += ["def_opr = '%s'" %(op)]

            opr_sel = opr_sel + " OR ".join(opr_sel_w)
            try:
                opr_filtered = pgdb.select(opr_sel)

            except:
                raise Exception("SQL: %s"%(opr_sel))
            if not len(opr_filtered)>0:
                raise sosException.SOSException("InvalidParameterValue","observedProperty","Parameter \"observedProperty\" sent with invalid value: %s - available options: %s"%(filter.observedProperty,opl))

        # SET TIME PERIOD
        tp=[]
        if filter.eventTime == None:
            self.period = None
        else:
            for t in filter.eventTime:
                if len(t) == 2:
                    tp.append(iso.parse_datetime(t[0]))
                    tp.append(iso.parse_datetime(t[1]))

                if len(t)==1:
                    tp.append(iso.parse_datetime(t[0]))
            self.period = [min(tp),max(tp)]

        self.obs=[]

        # SET REQUEST TIMEZONE
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


        # BUILD PROCEDURES LIST
        #  select part of query
        sqlSel = "SELECT DISTINCT id_prc, name_prc, concat('insitu-fixed-point','') as name_oty, stime_prc, etime_prc, null as time_res_prc"

        #  from part of query
        sqlFrom = "FROM istsos.observed_properties_sensor"
        sqlWhere = "WHERE "

        #  where condition based on procedures
        if filter.procedure:
            sqlWhere += " ("
            procWhere = []
            for proc in filter.procedure:
                procWhere.append("name_prc='%s'" %(proc))
            sqlWhere += " OR ".join(procWhere)
            sqlWhere += ")"

        #  where condition based on observed properties
        if sqlWhere != 'WHERE':
            sqlWhere += " AND "
        sqlWhere += " ("
        obsprWhere = []
        for obs in opr_filtered:
            obsprWhere.append("def_opr='%s'" %(obs["def_opr"]))
        sqlWhere += " OR ".join(obsprWhere)
        sqlWhere += ")"

        try:
            res = pgdb.select(sqlSel + " " + sqlFrom + " " + sqlWhere)
        except:
            raise Exception("SQL: %s"%(sqlSel + " " + sqlFrom + " " + sqlWhere))

        # FOR EACH PROCEDURE
        for o in res:
            # id_prc, name_prc, name_oty, stime_prc, etime_prc, time_res_prc, name_tru

            # CRETE OBSERVATION OBJECT
            ob = Observation()

            # BUILD BASE INFOS FOR EACH PROCEDURE (Pi)
            ob.baseInfo(pgdb, o, filter.sosConfig)

            # GET DATA FROM PROCEDURE ACCORDING TO THE FILTERS
            ob.setData(pgdb, o, filter)

            # ADD OBSERVATIONS
            self.obs.append(ob)


class GetObservationResponse_2_0_0:
    """
    The class that contain all the observations related to all the procedures


    Reference: http://www.opengis.net/doc/IS/SOS/2.0

    Requirement 35: http://www.opengis.net/spec/SOS/2.0/req/core/go-empty-response
        An instance of GetObservationResponse type shall be empty if none of the
        observations associated with the SOS fulfill the GetObservation parameters specified by the client.

    Attributes:
        offInfo (obj): the general information about offering name, connection object, and configuration options
        refsys (str): the uri that refers to the EPSG refrence system
        filter (obj): the filter object that contains all the parameters setting of the GetObservation request
        period (list): a list of two values in *datetime*: the minimum and maximum instants of the requested time filters
        reqTZ (obj): the timezone in *pytz.tzinfo*
        obs (list): list of *Observation* objects
    """

    def __init__(self, filter, pgdb):

        #self.offInfo = offInfo(filter.offering, pgdb, filter.sosConfig)
        self.refsys = filter.sosConfig.urn["refsystem"] + filter.srsName
        self.filter = filter

        self.obs = []


        # check if requested foi exist
        if not filter.featureOfInterest in ['', None]:
            params = [
                filter.featureOfInterest,
                filter.featureOfInterest
            ]
            sql = """
                SELECT %s as name_foi, exists(
                    select id_foi from """ + filter.sosConfig.schema + """.foi where name_foi=%s
                ) as exist_foi
            """
            try:
                # print(pgdb.mogrify(sql, tuple(params)), file=sys.stderr)
                result=pgdb.select(sql, tuple(params))

            except Exception as ex:
                raise Exception("SQL: %s\n\n%s" %(pgdb.mogrify(sql, tuple(params)), ex))

            filter.featureOfInterest = ''
            for row in result:
                if row["exist_foi"]:
                    filter.featureOfInterest = row["name_foi"]
                else:
                    raise sosException.SOSException("InvalidParameterValue", "featureOfInterest", "Invalid parameter value in 'featureOfInterest' parameter: %s" % row["name_foi"])


        # check if requested observed property exist
        if isinstance(filter.observedProperty, list) and len(filter.observedProperty)>0:
            clauses = []
            params = []

            if len(filter.observedProperty)==1:
                sql = """
                    SELECT %s as def_opr, exists(
                        SELECT id_opr FROM """ + filter.sosConfig.schema + """.observed_properties WHERE def_opr SIMILAR TO '%%(:|)'||%s||'(:|)%%'
                    ) as exist_opr
                """
                params = [
                    filter.observedProperty[0],
                    filter.observedProperty[0]
                ]
            else:
                for p in filter.observedProperty:
                    params.extend([p,p])
                    clauses.append("""
                        
                          SELECT %s as def_opr, exists(select id_opr from """ +
                              filter.sosConfig.schema + """.observed_properties WHERE def_opr SIMILAR TO '%%(:|)'||%s||'(:|)%%) as exist_opr
                    """)

                sql = " UNION ".join(clauses)
            try:
                result=pgdb.select(sql, tuple(params))

            except Exception as ex:
                raise Exception("SQL: %s\n\n%s" %(pgdb.mogrify(sql, tuple(params)), ex))

            filter.observedProperty = []
            for row in result:
                if row["exist_opr"]:
                    filter.observedProperty.append(row["def_opr"])
                else:
                    raise sosException.SOSException("InvalidParameterValue", "observedProperty", "Invalid parameter value in 'observedProperty' parameter: %s" % row["def_opr"])

        # check if requested offering/procedure exist
        if isinstance(filter.procedure, list) and len(filter.procedure)>0:
            clauses = []
            params = []

            if len(filter.procedure)==1:
                sql = """
                    SELECT %s as name_prc, exists(
                        select id_prc from """ + filter.sosConfig.schema + """.procedures where name_prc=%s
                    ) as exist_prc
                """
                params = [
                    filter.procedure[0],
                    filter.procedure[0]
                ]
            else:
                for p in filter.procedure:
                    params.extend([p,p])
                    clauses.append("""

                          SELECT %s as name_prc, exists(select id_prc from """ +
                              filter.sosConfig.schema + """.procedures where name_prc=%s) as exist_prc

                    """)

                sql = " UNION ".join(clauses)
            try:
                result=pgdb.select(sql, tuple(params))

            except Exception as ex:
                raise Exception("SQL: %s\n\n%s" %(pgdb.mogrify(sql, tuple(params)), ex))

            filter.procedure = []
            for row in result:
                if row["exist_prc"]:
                    filter.procedure.append(row["name_prc"])
                else:
                    raise sosException.SOSException("InvalidParameterValue", "procedure", "Invalid parameter value in 'procedure' parameter: %s" % row["name_prc"])

            # REQ35 - http://www.opengis.net/spec/SOS/2.0/req/core/go-empty-response
            #    if procedures requested not exists the GetObservationResponse type shall be empty
            if len(filter.procedure)==0:
                return

        # REQ29: http://www.opengis.net/spec/SOS/2.0/req/core/go-parameters
        #    The SOS returns all observations that match the specified parameter values. The
        #    filter parameters (e.g., observedProperty , procedure , or temporalFilter ) shall be connected
        #    with an implicit AND. The values of each of the parameters shall be connected with an implicit OR.

        params = []

        sql = """
            SELECT DISTINCT
              procedures.id_prc,
              procedures.name_prc,
              obs_type.name_oty,
              procedures.stime_prc,
              procedures.etime_prc,
              procedures.time_res_prc

            FROM
              """ + filter.sosConfig.schema + """.procedures,
              """ + filter.sosConfig.schema + """.foi,
              """ + filter.sosConfig.schema + """.proc_obs,
              """ + filter.sosConfig.schema + """.observed_properties,
              """ + filter.sosConfig.schema + """.obs_type

            WHERE
              procedures.id_foi_fk = foi.id_foi

            AND
              proc_obs.id_prc_fk = procedures.id_prc

            AND
              obs_type.id_oty = procedures.id_oty_fk

            AND
              observed_properties.id_opr = proc_obs.id_opr_fk
        """


        # Adding offering and procedure filter
        #  > in istSOS offerings are equals to procedures
        if isinstance(filter.procedure, list) and len(filter.procedure)>0:
            clauses = []
            for c in range(0, len(filter.procedure)):
                clauses.append("procedures.name_prc = %s")
                params.append(filter.procedure[c])

            sql = "%s AND (%s)" % (sql, (' OR '.join(clauses)))

        # Adding feature of interest filter
        if filter.featureOfInterest != None:
            params.append(filter.featureOfInterest)
            sql = "%s %s" % (sql, """
                AND foi.name_foi = %s
            """)

        # Adding observed properties filter
        if isinstance(filter.observedProperty, list) and len(filter.observedProperty)>0:
            clauses = []
            for c in range(0, len(filter.observedProperty)):
                clauses.append("def_opr SIMILAR TO '%%(:|)'||%s||'(:|)%%'")
                params.append(filter.observedProperty[c])

            sql = "%s AND (%s)" % (sql, (' OR '.join(clauses)))

        # Adding temporal filter
        if isinstance(filter.eventTime, list) and len(filter.eventTime)>0:
            clauses = []
            for c in range(0, len(filter.eventTime)):
                if len(filter.eventTime[c])==1: # time instant
                    clauses.append("(stime_prc < timestamptz %s AND timestamptz %s <= etime_prc)")
                    params.extend([filter.eventTime[c][0]]*2)

                elif len(filter.eventTime[c])==2: # time period
                    clauses.append("(timestamptz %s <= etime_prc AND timestamptz %s >= stime_prc)")
                    params.extend(filter.eventTime[c])

            sql = "%s AND (%s)" % (sql, (' OR '.join(clauses)))

        # Executing search query
        try:
            result = pgdb.select(sql, tuple(params))
            # If empty, the service will return an empty GetObservationResponse
            if len(result)==0:
                return

        except Exception as ex:
            raise Exception("SQL: %s\n\n%s" %(pgdb.mogrify(sql,tuple(params)), ex))

        # Preparing Observation object
        for row in result:

            # CRETE OBSERVATION OBJECT
            ob = Observation()

            # BUILD BASE INFOS FOR EACH PROCEDURE
            ob.baseInfo(pgdb, row, filter.sosConfig)

            # GET DATA FROM PROCEDURE ACCORDING TO THE FILTERS
            ob.setData(pgdb, row, filter)

            # ADD OBSERVATIONS
            self.obs.append(ob)
