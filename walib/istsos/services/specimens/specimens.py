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
from walib import databaseManager
from walib.resource import waResourceService
import traceback

from walib import resource, utils, databaseManager, configManager
from walib.resource import waResourceService
import sys, os
import isodate as iso
import json


# TODO: we are not yet validating the specimen object

class waSpecimens(waResourceService):
    """class to handle Specimens objects, support GET, POST, DELETE and UPDATE method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self, waEnviron)
        self.specimen_id = int(self.pathinfo[-1]) if not self.pathinfo[-1]=="specimens" else None
        self.servicename = self.pathinfo[2]

        self.conn = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
        
    def executeGet(self):
        """
        Method for executing a GET requests that return a specific specime
                          
        """
        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
        else:
            try:
                if self.specimen_id is None:
                    raise Exception("GET specimen without specimen_id not allowed")
                # retrieve specimen from id
                rows = self.conn.select(
                    """
                        SELECT 
                            specimen
                        FROM
                            %s.specimens
                        """ % (self.service) + """
                        WHERE
                            id_spec = %s
                    """, (self.specimen_id,))
                if rows:
                    self.setMessage("Specimen %s successfully retrived" % self.specimen_id)
                    self.setData(rows[0][0])
                else:
                    self.setMessage("Specimen %s not found!" % self.specimen_id)
                
            except Exception as e:
                print(traceback.print_exc(), file=sys.stderr)
                self.setException(
                    "Error in GET sepcimen (%s): %s" % (type(e), e))

    def executePost(self):
        """
        Method for executing a POST request to insert a new specimen
        Return: the specimen id

        @note: This request create a new specimen for a given procedure and sampling time

        >>> {
                "procedure_id": "absc12c32v3cbv1c23b213c2b",
                "eventTime": "2017-06-30T15:27:00+01:00",
                "observations": {
                    "urn:ogc:def:parameter:x-istsos:1.0:lake:water:pp": 0.25,
                    "urn:ogc:def:parameter:x-istsos:1.0:lake:water:ph": 443,
                    "urn:ogc:def:parameter:x-istsos:1.0:lake:water:chl-a": 12
                }
                "specimen": {
                    "description": "A sample for the Lugano Lake water quality monitoring",
                    "campaign": "Settembre_2019",
                    "identifier": "LUG_20170830",
                    "name": "LUG_20170808",
                    "sampledFeature": "http://www.istsos.org/demo/feature/LuganoLake",
                    "samplingTime": "2017-06-30T15:27:00+01:00",
                    "materialClass": "http://www.istsos.org/material/water",
                    "samplingMethod": "http://www.istsos.org/samplingMethod/bottiglia",
                    "processingDetails": [
                                {
                                    "processOperator": "http://www.supsi.ch/ist?person=MarioBianchi",
                                    "processingDetails": "http://www.istsos.org/processes/storage",
                                    "processingProtocol": "http://ti.ch/oasi/sop12",
                                    "time": "2017-07-01T15:27:00+01:00"
                                },
                                {
                                    "processOperator": "https://www.supsi.ch/ist?person=LucaRossi",
                                    "processingDetails": "http://www.istsos.org/processes/Reaction",
                                    "processingProtocol": "http://ti.ch/oasi/sop12",
                                    "time": "2017-07-06T15:27:00+01:00"
                                }
                            ],
                    "size": {
                        "value": 1,
                        "uom": "http://www.uom/liter"
                    },
                    "currentLocation": {
                        "href": "http://www.ti.ch/umam",
                        "rel": "http://www.onu.org/offices",
                        "title": "Ufficio Monitoraggio Ambientale - Canton Ticino"
                    },
                    "specimenType": null
                    }
                }
            }
        """

        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
        else:
            try:
                # insert new specimen in db
                # =========================
                # get info of observed properties for the specified procedure
                if 'procedure_id' not in self.json or self.json['procedure_id'] is None:
                    raise Exception(
                        "POST specimen without procedure_id not allowed")
                if 'eventTime' not in self.json or self.json['eventTime'] is None:
                    raise Exception(
                        "POST specimen without eventTime name not allowed")

                from datetime import datetime
                now = datetime.now(iso.UTC)
                
                rows = self.conn.select(
                    """
                        SELECT
                            procedures.id_prc,
                            proc_obs.id_pro,
                            observed_properties.def_opr,
                            proc_obs.constr_pro,
                            procedures.stime_prc,
                            procedures.etime_prc,
                            procedures.name_prc,
                            obs_type.name_oty,
                            observed_properties.constr_opr
                        FROM
                            %s.procedures,
                            %s.proc_obs,
                            %s.observed_properties,
                            %s.obs_type
                        """ % (
                            self.servicename, self.servicename, 
                            self.servicename, self.servicename
                            ) + """
                        WHERE
                            proc_obs.id_prc_fk = procedures.id_prc
                        AND
                            proc_obs.id_opr_fk = observed_properties.id_opr
                        AND
                            assignedid_prc = %s
                        AND
                            id_oty = id_oty_fk
                        ORDER BY
                            proc_obs.id_pro ASC;
                        """,
                    (
                        self.json["procedure_id"],
                    )
                )
                print("ROWS: ",rows)

                if not rows:
                    raise Exception("Cannot find specified procedure_id %s" % self.json["procedure_id"])

                if rows[0][7] not in ['insitu-fixed-specimen']:
                    raise Exception("Cannot insert specimen for procedure that is not a apecimen type")

                id_prc = rows[0][0]
                name_prc = rows[0][6]
                bp = rows[0][4]
                bpu = False
                ep = rows[0][5]
                epu = False
                data = []                

                def check_sampling(sampling):
                    # If the end position exists the new measures must be after
                    if ep is not None and sampling <= ep:
                        return False
                    # Check that the sampling time is before now
                    if sampling > now:
                        return False
                    return True
                
                # get and verify specimen eventTime
                print(self.json['eventTime'], type(self.json['eventTime']))
                try:
                    eventTime = iso.parse_datetime(self.json['eventTime'])
                    # import dateutil.parser
                    # samplingTime = dateutil.parser.parse(self.json['samplingTime'])
                except:
                    raise Exception(
                        "Procedure %s, Sampling time (%s) "
                        "wrong format" % (
                            name_prc, eventTime
                        )
                    )

                if check_sampling(eventTime):
                    raise Exception("eventTime in begin/end periods")
                    
                
                # create the eventTime
                id_eti = self.conn.executeInTransaction(
                    ("""
                        INSERT INTO %s.event_time (id_prc_fk, time_eti)
                    """ % self.servicename) + """
                        VALUES (%s, %s::TIMESTAMPTZ) RETURNING id_eti;
                    """,
                    (
                        id_prc, eventTime
                    )
                )

                # set observedProperties data values
                for row in rows:

                    val = self.json['observations'][row['def_opr']]
                    pco = json.loads(row[8]) # constraint of the observation (level 0)
                    pcp = json.loads(row[3]) # constraint of the procedure (level 1)
                    
                    # set qualityIndex if not set
                    if row['def_opr']+":qualityIndex" in self.json['observations']:
                        qi = self.json['observations'][row['def_opr']+":qualityIndex"]
                    else:
                        # Constraint quality is done only if the quality index
                        #  is equal to the default qi (RAW DATA)
                        qi = int(self.serviceconf.getobservation['default_qi'])
                        
                        # quality check level I (gross error)
                        if self.serviceconf.getobservation['correct_qi'] is not None and (
                                pco is not None):
                            if 'max' in pco:
                                if val <= (
                                        float(pco['max'])):
                                    qi = int(self.serviceconf.getobservation['correct_qi'])

                            elif 'min' in pco:
                                if val >= (
                                        float(pco['min'])):
                                    qi = int(self.serviceconf.getobservation['correct_qi'])

                            elif 'interval' in pco:
                                if (float(pco['interval'][0])
                                        <= val
                                        <= float(pco['interval'][1])):
                                    qi = int(self.serviceconf.getobservation['correct_qi'])

                            elif 'valueList' in pco:
                                if val in [float(p) for p in (
                                        pco['valueList'])]:
                                    qi = int(self.serviceconf.getobservation['correct_qi'])

                        # quality check level II (statistical range)
                        if self.serviceconf.getobservation['stat_qi'] is not None and (
                                pcp is not None):
                            if 'max' in pcp:
                                if val <= float(pcp['max']):
                                    qi = int(self.serviceconf.getobservation['stat_qi'])

                            elif 'min' in pcp:
                                if val >= float(pcp['min']):
                                    qi = int(self.serviceconf.getobservation['stat_qi'])

                            elif 'interval' in pcp:
                                if (float(pcp['interval'][0]) <=
                                        val <=
                                        float(pcp['interval'][1])):
                                    qi = int(self.serviceconf.getobservation['stat_qi'])

                            elif 'valueList' in pcp:
                                if val in [float(p) for p in pcp[
                                        'valueList']]:
                                    qi = int(self.serviceconf.getobservation['stat_qi'])

                    data.append(
                        (
                            int(id_eti[0][0]),
                            int(row['id_pro']),
                            float(val),
                            int(qi)
                            )
                    )
                
                print("DATA: ", data)

                # insert data values
                for d in data:
                    self.conn.executeInTransaction(
                        ("""
                            INSERT INTO %s.measures(
                                id_eti_fk,
                                id_pro_fk,
                                val_msr,
                                id_qi_fk
                            )
                        """ % self.servicename) + """
                            VALUES (%s, %s, %s, %s);
                        """, d
                    )

                # insert the specimen
                id_spec = self.conn.executeInTransaction(
                    ("""INSERT INTO %s.specimens(
                        id_qi_fk,
                        id_eti_fk,
                        specimen
                    )
                    """ % self.servicename) + """
                            VALUES (%s, %s, %s)
                        RETURNING id_spec;
                    """,
                    (
                        int(self.serviceconf.getobservation['default_qi']),
                        int(id_eti[0][0]),
                        json.dumps(self.json["specimen"])
                    )
                )[0]

                # update begin/end position of the procedure
                if (bp is None) or (bp == '') or (
                        eventTime < bp):
                    bp = eventTime
                    bpu = True

                if (ep is None) or (ep == '') or (
                        eventTime > ep):
                    ep = eventTime
                    epu = True

                if bpu:
                    self.conn.executeInTransaction(
                        ("""
                            UPDATE %s.procedures
                        """ % self.servicename) + """
                            SET stime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s
                        """,
                        (
                            bp.isoformat(),
                            id_prc
                        )
                    )

                if epu:
                    self.conn.executeInTransaction(
                        ("""
                            UPDATE %s.procedures
                        """ % self.servicename) + """
                            SET etime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s
                        """,
                        (
                            ep.isoformat(),
                            id_prc
                        )
                    )

                self.conn.commitTransaction()
                self.setMessage("Specimen %s succesfully inserted" % id_spec)
                self.setData(id_spec)

            except Exception as e:
                self.conn.rollbackTransaction()
                print(traceback.print_exc(), file=sys.stderr)
                self.setException("Error in POST sepcimen (%s): %s" % (type(e), e))
                           
    def executePut(self):
        """
        Method for executing a PUT requests that updates an existing Specimen

        """
        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
        else:
            try:
                if self.specimen_id is None:
                    raise Exception("GET specimen without specimen_id not allowed")
                
                # update the specimen
                rows = self.conn.executeInTransaction(
                    """
                        UPDATE
                            %s.specimens
                            """ % (self.service) + """
                        SET 
                            specimen = %s
                        WHERE
                            id_spec = %s
                        RETURNING *;
                    """, 
                    (json.dumps(self.json), self.specimen_id)
                    )
                if rows and len(rows)==1:
                    self.conn.commitTransaction()
                    self.setMessage("Specimen %s succesfully inserted" % self.specimen_id)
                else:
                    raise Exception("cannot find secimen %s" % self.specimen_id)

            except Exception as e:
                self.conn.rollbackTransaction()
                print(traceback.print_exc(), file=sys.stderr)
                self.setException("Error in POST sepcimen (%s): %s" % (type(e), e))
                           
    def executeDelete(self):
        """
        Method for executing a DELETE requests that remove an existing SOS data quality
        
        """
        if self.service == "default":
            raise Exception("dataqualities operation can not be done for default service instance.")
        else:
            try:
                if self.specimen_id is None:
                    raise Exception(
                        "GET specimen without specimen_id not allowed")
                # retrieve specimen from id
                rows = self.conn.execute(
                    """
                        UPDATE
                            %s.specimens
                            """ % (self.service) + """
                        SET 
                            specimen = NULL
                        WHERE
                            id_spec = %s
                        RETURNING *;
                    """, (self.specimen_id,))
                if rows:
                    self.setMessage("Specimen %s set to NULL" % self.specimen_id)
                    self.setData(json.dumps(rows[0][0]))
                else:
                    self.setMessage("Specimen %s not found!" % self.specimen_id)
                
            except Exception as e:
                print(traceback.print_exc(), file=sys.stderr)
                self.setException(
                    "Error in DELETE sepcimen (%s): %s" % (type(e), e))
