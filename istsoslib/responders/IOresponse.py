# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# =============================================================================

__author__ = 'Milan Antonovic'
__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__credits__ = []
__license__ = 'GPL2'
__version__ = '1.0'
__maintainer__ = 'Massimiliano Cannata, Milan Antonovic'
__email__ = 'milan.antonovic@gmail.com'

import sys
import pprint
from istsoslib import sosException
from lib import isodate as iso
from datetime import datetime
import json

now = datetime.now()


class InsertObservationResponse:
    def __init__(self, filter, pgdb):

        # get procedure information
        sql = """
            SELECT
                id_prc,
                name_prc,
                name_oty,
                name_foi,
                stime_prc,
                etime_prc
            FROM
                %s.procedures,
                %s.obs_type,
                %s.foi""" % (filter.sosConfig.schema,
                             filter.sosConfig.schema,
                             filter.sosConfig.schema)
        sql += """
            WHERE
                id_oty=id_oty_fk
            AND
                id_foi=id_foi_fk
            AND
                assignedid_prc=%s"""

        params = (filter.assignedSensorId,)
        try:
            prc = pgdb.select(sql, params)[0]
        except:
            raise sosException.SOSException(
                "InvalidParameterValue",
                "assignedSensorId",
                "assignedSensorId '%s' is not valid!" % (
                    filter.assignedSensorId))

        # check requested procedure name exists
        if not prc["name_prc"] == filter.procedure:
            raise sosException.SOSException(
                "NoApplicableCode",
                None,
                "procedure '%s' not associated with provided "
                "assignedSensorId!" % (filter.procedure))

        # check requested  foi name exists
        if not filter.foiName == prc["name_foi"]:
            raise sosException.SOSException(
                "NoApplicableCode",
                None,
                "featureOfInterest '%s' not associated with "
                "provided assignedSensorId" % (filter.foiName))

        # check provided samplingTime and upadate
        #  begin/end time procedure if necessary
        #  (samplingTime=period or istant of provided
        #  observations defined by samplingTime filter)
        #=============================================
        if filter.samplingTime:
            stime = filter.samplingTime.split("/")
            #
            if len(stime) == 2:  # is a TimePeriod
                start = iso.parse_datetime(stime[0])
                end = iso.parse_datetime(stime[1])

            elif len(stime) == 1:  # is a TimeInstant
                start = end = iso.parse_datetime(stime[0])

            else:
                raise Exception("filter samplingTime error! given '%s'" % (
                    filter.samplingTime))

            if start > end:
                raise Exception(
                    "endPosition (%s) must be after beginPosition (%s)" % (
                        end, start))

            # check samplingTime
            #  > verify procedure begin/end exist
            if not (prc["stime_prc"].__class__.__name__ == "NoneType" and (
                    prc["etime_prc"].__class__.__name__ == "NoneType")):

                # check eventTime interval and update begin/end position when
                #  force flas is active
                if filter.forceInsert:
                    # update begin time of procedure
                    if start < prc["stime_prc"]:
                        sql = """
                            UPDATE
                                %s.procedures""" % (filter.sosConfig.schema)
                        sql += """
                            SET
                                stime_prc=%s::TIMESTAMPTZ
                            WHERE
                                id_prc=%s"""
                        params = (stime[0], prc["id_prc"])
                        try:
                            a = pgdb.executeInTransaction(sql, params)
                            com = True

                        except:
                            raise Exception("SQL: %s" % (
                                pgdb.mogrify(sql, params)))

                    # update end time of procedure
                    if end > prc["etime_prc"]:
                        sql = """
                            UPDATE
                                %s.procedures""" % (filter.sosConfig.schema)
                        sql += """
                            SET
                                etime_prc=%s::TIMESTAMPTZ
                            WHERE
                                id_prc=%s"""
                        params = (stime[1], prc["id_prc"])
                        try:
                            b = pgdb.executeInTransaction(sql, params)
                            com = True

                        except Exception as err:
                            raise Exception("SQL: %s - %s" % (
                                pgdb.mogrify(sql, params), err.pgerror))

                # check eventTime interval and update begin/end position when
                #  force flag is off
                else:
                    sql = """
                        SELECT
                            max(time_eti) as max_time_eti
                        FROM
                            %s.event_time""" % (filter.sosConfig.schema)
                    sql += """
                        WHERE
                            id_prc_fk = %s
                        GROUP BY
                            id_prc_fk"""
                    params = (prc["id_prc"],)
                    try:
                        lastMsr = pgdb.select(sql, params)[0]["max_time_eti"]
                    except:
                        lastMsr = None

                    if lastMsr is not None:
                        # verify begin observation is minor/equal then end
                        #  time procedure and later then last observation
                        if not (end >= prc["etime_prc"] and (
                                start <= prc["etime_prc"]) and (
                                start >= lastMsr)):
                            raise Exception(
                                "begin observation (%s) must be between last "
                                "observation (%s) and end procedure (%s); end"
                                " observation (%s) must be after end "
                                "procedure (%s)" % (
                                    start,
                                    lastMsr, prc["etime_prc"],
                                    end,
                                    prc["etime_prc"]))
                    else:
                        # verify begin observation is minor/equal then end
                        #  time procedure and later then first observation
                        if not (end >= prc["etime_prc"] and (
                                start <= prc["etime_prc"]) and (
                                start >= prc["stime_prc"])):
                            raise Exception(
                                "begin observation (%s) must be between start "
                                "procedure (%s) and end procedure (%s); end "
                                "observation (%s) must be after end procedure "
                                "(%s)" % (
                                    start,
                                    prc["stime_prc"], prc["etime_prc"],
                                    end,
                                    prc["etime_prc"]))

                    #-- update end time of procedure
                    sql = """
                        UPDATE
                            %s.procedures""" % (filter.sosConfig.schema)
                    sql += """
                        SET
                            etime_prc=%s::TIMESTAMPTZ
                        WHERE
                            id_prc=%s"""
                    params = (str(stime[1]), int(prc["id_prc"]))
                    try:
                        b = pgdb.executeInTransaction(sql, params)
                        com = True
                    except Exception as err:
                        raise Exception("SQL: %s - %s" % (
                            pgdb.mogrify(sql, params), err.pgerror))

            else:
                sql = """
                    UPDATE
                        %s.procedures""" % (filter.sosConfig.schema)
                sql += """
                    SET
                        stime_prc=%s::TIMESTAMPTZ,
                        etime_prc=%s::TIMESTAMPTZ
                    WHERE
                        id_prc=%s"""
                params = (str(stime[0]), str(stime[1]), int(prc["id_prc"]))
                try:
                    b = pgdb.executeInTransaction(sql, params)
                    com = True
                except:
                    raise Exception("SQL: %s" % (pgdb.mogrify(sql, params)))

        # check data definition and uom (compare registered
        #  observed properties with provided observations)
        #==================================================
        # get values for provided data: UOM, NAME, URN, ID
        #--------------------------------------------------
        sql = """
            SELECT
                id_pro,
                id_opr,
                def_opr,
                name_uom,
                constr_opr,
                constr_pro
            FROM
                %s.observed_properties,
                %s.proc_obs,
                %s.uoms""" % (filter.sosConfig.schema,
                              filter.sosConfig.schema,
                              filter.sosConfig.schema)
        sql += """
            WHERE
                id_uom_fk = id_uom
            AND
                id_opr_fk = id_opr
            AND
                id_prc_fk = %s"""
        params = (prc["id_prc"],)
        try:
            opr = pgdb.select(sql, params)
        except Exception as err:
            raise Exception("SQL2: %s -%s" % (
                pgdb.mogrify(sql, params), err.pgerror))

        # get list of available ObservedProperty, unit of measure, property
        #  id for this procedure
        oprNames = []
        oprUoms = []
        oprIds = []  # to be removed ????
        proIds = []
        obsPropConstr = []
        procConstr = []

        '''
        Building a matrix:

        oprNames = ["urn:ogc:def:parameter:x-istsos:1.0:" +
                    "meteo:air:temperature" , ...]
        oprUoms = ["mm" , ...]
        oprIds = [id_opr , ...]
        proIds = [id_pro , ...]
        obsPropConstr = [{
            "interval": ["-40", "50"],
            "role": "urn:ogc:def:classifiers:x-istsos:1.0:" +
                    "qualityIndex:check:acceptable"} , ...]
        procConstr = [{
            "max": "100",
            "role": "urn:ogc:def:classifiers:x-istsos:1.0:" +
                    "qualityIndex:check:reasonable"} , ...]
        '''

        for row in opr:

            oprNames.append(row["def_opr"])
            oprUoms.append(row["name_uom"])
            oprIds.append(row["id_opr"])
            proIds.append(row["id_pro"])

            if not row["constr_opr"] in [None, '']:
                obsPropConstr.append(json.loads(row["constr_opr"]))
            else:
                obsPropConstr.append(None)

            if not row["constr_pro"] in [None, '']:
                procConstr.append(json.loads(row["constr_pro"]))
            else:
                procConstr.append(None)

        # get ordered list of observed properties in data----
        dataKeys = [key for key in filter.data.keys()]

        # get ordered list of unit of measures provided with data-------
        dataUoms = []
        for key in filter.data.keys():
            if "uom" in filter.data[key].keys():
                dataUoms.append(filter.data[key]["uom"])
            else:
                dataUoms.append('None')

        # verify that all the properties observed by this procedure
        #  are provided with the correct data definition and uom
        for i, opr in enumerate(oprNames):
            try:
                k = dataKeys.index(opr)
            except:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "parameter '%s' not observed by RegisteredSensor "
                    "%s - %s" % (opr, oprNames, dataKeys))

            if not dataUoms[k] == oprUoms[i]:
                raise sosException.SOSException(
                    "NoApplicableCode", None,
                    "parameter '%s' not observed with provided unit of "
                    "measure" % (opr))

        # verify if time and coordinates are passed as data parameters
        #  and create the parameters list and parameters ID
        xobs = yobs = zobs = tpar = None
        pars = []  # Observed parameters
        parsId = []
        parsConsObs = []
        parsConsPro = []

        # urn of different parameters
        for i, dn in enumerate(dataKeys):
            if dn.split(":")[-1] in filter.sosConfig.parGeom["x"]:
                xobs = dataKeys[i]
            elif dn.split(":")[-1] in filter.sosConfig.parGeom["y"]:
                yobs = dataKeys[i]
            elif dn.split(":")[-1] in filter.sosConfig.parGeom["z"]:
                zobs = dataKeys[i]
            elif dn.find("iso8601") >= 0:
                tpar = dataKeys[i]
            else:
                if dn.split(":")[-1] != "qualityIndex":
                    pars.append(dn)
                    try:
                        parsId.append(proIds[oprNames.index(dn)])
                        parsConsObs.append(obsPropConstr[oprNames.index(dn)])
                        parsConsPro.append(procConstr[oprNames.index(dn)])
                    except:
                        raise Exception(
                            "parameter %s not observed by this sensor "
                            "%s - %s" % (dn, pars, oprNames))

        # set default quality index if not provided
        for par in pars:
            try:
                dataKeys.index(par+":qualityIndex")
            except:
                filter.data[par+":qualityIndex"] = {
                    "vals": [filter.sosConfig.default_qi] * len(
                        filter.data[par]["vals"])}

        # verify that mobile sensors provide coordinates as X,Y,Z
        if (xobs is False and yobs is False and zobs is False) and (
                prc["name_oty"] == "insitu-mobile-point"):
            raise Exception("Mobile sensors require x, y, z parameters")

        # verify that time parameter is provided
        if not tpar:
            raise Exception(
                "parameter 'time:iso8601' is required for InsertObservation")

        # verify that eventime are in provided samplingTime
        if len(filter.data[tpar]["vals"]) > 0:
            maxDate = iso.parse_datetime(max(filter.data[tpar]["vals"]))
            minDate = iso.parse_datetime(min(filter.data[tpar]["vals"]))
            if not maxDate <= end and minDate >= start:
                raise Exception(
                    "provided data (min: %s, max:%s) are not included in "
                    "provided <samplingTime> period (%s / %s) for "
                    "procedure %s" % (
                        minDate.isoformat(), maxDate.isoformat(),
                        start.isoformat(), end.isoformat(),
                        prc["name_prc"]))

        # insert observation
        #  delete existing observations if force flag is active
        if filter.forceInsert:
            sql = """
                DELETE FROM
                    %s.event_time""" % (filter.sosConfig.schema)
            sql += """
                WHERE
                    id_prc_fk = %s
                AND
                    time_eti >= %s::TIMESTAMPTZ
                AND
                    time_eti <= %s::TIMESTAMPTZ"""
            params = (prc["id_prc"], stime[0], stime[1])
            try:
                b = pgdb.executeInTransaction(sql, params)
                com = True
            except:
                raise Exception("SQL: %s" % (pgdb.mogrify(sql, params)))

        # CASE I: observations list is void
        if len(filter.data[tpar]["vals"]) == 0:
            self.assignedId = ""
            ids_eti = []

        # CASE I: observations list contains data
        elif len(filter.data[tpar]["vals"]) > 0:
            # insert event times
            ids_eti = []
            params = []
            sql = """
                INSERT INTO
                    %s.event_time (id_prc_fk,time_eti)""" % (
                filter.sosConfig.schema)
            sql += """
                VALUES (
                    %s, %s::TIMESTAMPTZ)
                RETURNING
                    id_eti"""
            for val in filter.data[tpar]["vals"]:
                try:
                    ids_eti.append(
                        pgdb.executeInTransaction(
                            sql, (prc["id_prc"], val))[0]['id_eti'])
                    com = True
                except Exception as e:
                    raise Exception(
                        "Error inserting event times for %s: %s" % (
                            prc["name_prc"], e))

            for i, par in enumerate(pars):
                params = []
                ids_msr = []
                sql = """
                    INSERT INTO %s.measures (
                        id_pro_fk,
                        id_eti_fk,
                        id_qi_fk,
                        val_msr)""" % (filter.sosConfig.schema)
                sql += """
                    VALUES
                        (%s, %s, %s, %s)
                    RETURNING
                        id_msr"""

                pco = parsConsObs[i]
                pcp = parsConsPro[i]
                for ii, id_et in enumerate(ids_eti):
                    if not filter.data[par]["vals"][ii] in [
                            'NULL', u'NULL', None, 'None', u'None',
                            filter.sosConfig.aggregate_nodata]:
                        # TODO: add an else statement to add the
                        #  aggregate_nodata value OR delete the event time if
                        #  not filter.data[par]["vals"][ii] in ['NULL',u'NULL',
                        #  None]:
                        pqi = int(filter.data[par+":qualityIndex"]["vals"][ii])
                        # Constraint quality is done only if the quality index
                        #  is equal to the default qi (RAW DATA)
                        if int(filter.sosConfig.default_qi) == pqi:
                            # quality check level I (gross error)
                            val = float(filter.data[par]["vals"][ii])
                            if filter.sosConfig.correct_qi is not None and (
                                    pco is not None):
                                if 'max' in pco:
                                    if val <= (
                                            float(pco['max'])):
                                        pqi = int(filter.sosConfig.correct_qi)

                                elif 'min' in pco:
                                    if val >= (
                                            float(pco['min'])):
                                        pqi = int(filter.sosConfig.correct_qi)

                                elif 'interval' in pco:
                                    if (float(pco['interval'][0])
                                            <= val
                                            <= float(pco['interval'][1])):
                                        pqi = int(filter.sosConfig.correct_qi)

                                elif 'valueList' in pco:
                                    if val in [float(p) for p in (
                                            pco['valueList'])]:
                                        pqi = int(filter.sosConfig.correct_qi)

                            # quality check level II (statistical range)
                            if filter.sosConfig.stat_qi is not None and (
                                    pcp is not None):
                                if 'max' in pcp:
                                    if val <= float(pcp['max']):
                                        pqi = int(filter.sosConfig.stat_qi)

                                elif 'min' in pcp:
                                    if val >= float(pcp['min']):
                                        pqi = int(filter.sosConfig.stat_qi)

                                elif 'interval' in pcp:
                                    if (float(pcp['interval'][0]) <=
                                            val <=
                                            float(pcp['interval'][1])):
                                        pqi = int(filter.sosConfig.stat_qi)

                                elif 'valueList' in pcp:
                                    if val in [float(p) for p in pcp[
                                            'valueList']]:
                                        pqi = int(filter.sosConfig.stat_qi)

                        params = (
                            int(parsId[i]), int(id_et),
                            pqi, float(filter.data[par]["vals"][ii]))
                        try:
                            nid_msr = pgdb.executeInTransaction(sql, params)
                            ids_msr.append(str(nid_msr[0]['id_msr']))
                        except Exception as e:
                            com = False
                            raise e

            #--insert position values if required
            if prc["name_oty"] == "insitu-mobile-point":
                xparspl = xobs.split(":")
                epsg = xparspl[xparspl.index("EPSG")+1]
                params = []
                sql = """
                    INSERT INTO %s.positions (
                        id_qi_fk,
                        id_eti_fk,
                        geom_pos)""" % (filter.sosConfig.schema)
                sql += """
                    VALUES (
                        %s, %s,
                        ST_Transform(
                            ST_SetSRID(ST_MakePoint(%s, %s, %s), %s), %s))"""

                for i, id_et in enumerate(ids_eti):
                    params = (
                        filter.sosConfig.default_qi, id_et,
                        filter.data[xobs]["vals"][i],
                        filter.data[yobs]["vals"][i],
                        filter.data[zobs]["vals"][i],
                        epsg,
                        filter.sosConfig.istsosepsg)
                    try:
                        ids_pos = pgdb.executeInTransaction(sql, params)
                        com = True
                    except Exception as a:
                        com = False
                        raise Exception(
                            "%s\nSQL: %s" % (a, pgdb.mogrify(sql, params)))

            # register assigned IDs of measures
            self.assignedId = "@".join([str(p) for p in ids_eti])
            # commit executed operations

        #Register the transactional operation in Log table
        if filter.sosConfig.transactional_log in ['True', 'true', 1]:
            sqlLog = """
                INSERT INTO %s.tran_log (
                    operation_trl,
                    procedure_trl,
                    begin_trl,
                    end_trl,
                    count,
                    stime_prc,
                    etime_prc)""" % (filter.sosConfig.schema)
            sqlLog += """
                VALUES (
                    'InsertObservation',
                    %s,
                    %s::TIMESTAMPTZ,
                    %s::TIMESTAMPTZ,
                    %s,
                    %s::TIMESTAMPTZ,
                    %s::TIMESTAMPTZ)"""
            params = (
                str(filter.procedure),
                start,
                end,
                len(ids_eti),
                prc["stime_prc"],
                prc["etime_prc"])
            try:
                pgdb.executeInTransaction(sqlLog, params)
                com = True
            except:
                raise Exception("SQL: %s" % (pgdb.mogrify(sqlLog, params)))

        if com is True:
            pgdb.commitTransaction()
            # broadcasting to mqtt broker if configured
            if filter.sosConfig.mqtt["broker_url"] != '' and (
                    filter.sosConfig.mqtt["broker_port"] != ''):
                from istmqttlib import PahoPublisher
                PahoPublisher({
                    "broker_url": filter.sosConfig.mqtt["broker_url"],
                    "broker_port": filter.sosConfig.mqtt["broker_port"],
                    "broker_topic": "%s%s" % (
                        filter.sosConfig.mqtt["broker_topic"],
                        filter.procedure),
                    "data": filter.dataArray
                }).start()
