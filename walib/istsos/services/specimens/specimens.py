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
from datetime import datetime


# TODO: we are not yet validating the specimen object

class waSpecimens(waResourceService):
    """class to handle Specimens objects, support GET, POST, DELETE and UPDATE method"""
    
    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)
        self.identifier = self.pathinfo[-1] if not self.pathinfo[-1]=="specimens" else None
        self.servicename = self.pathinfo[2]
        self.force = False
        
        if self.identifier is None:
            if (self.waEnviron['parameters']
                and ('etime' in self.waEnviron['parameters'])
                and ('procedure' in self.waEnviron['parameters'])):
                
                self.etime = [
                    iso.parse_datetime(t) for t in self.waEnviron['parameters']['etime'][0].split("/")
                ]
                # self.etime = self.waEnviron['parameters']['etime'][0].split("/")
                self.procedure = self.waEnviron['parameters']['procedure'][0]
            else:
                self.etime = None
                self.procedure = None
        
        if (self.waEnviron['parameters']
                and 'forceInsert' in self.waEnviron['parameters']):
            if self.waEnviron['parameters'] in ['true', 'True','TRUE']:
                self.force = True 

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
                if self.identifier is None:
                    if self.etime is not None and self.procedure is not None:
                        if len(self.etime) == 1:
                            self.etime = self.etime * 2
                        elif len(self.etime) == 2:
                            pass
                        else:
                            raise Exception("etime parameter accept single time"
                                            " [2019-12-30T16:25:00+01]"
                                            " or pariod [2019-12-30T16:25:00+01"
                                            "/2019-12-31T16:25:00+01] values")
                        
                        rows = self.conn.select(
                        """
                            select 
                                array_to_json(array_agg(row_to_json(rows)))
                            from (
                                SELECT 
                                    t.procedure,
                                    t.observations,
                                    t."eventTime",
                                    sp.specimen
                                FROM
                                (
                                SELECT
                                    MIN(p.name_prc) as procedure,
                                    json_collect(json_build_object(op.def_opr,me.val_msr)) as observations,
                                    et.time_eti as "eventTime",
                                    et.id_eti
                                FROM
                                    %s.procedures p,
                                    %s.proc_obs po,
                                    %s.observed_properties op,
                                    %s.obs_type ot,
                                    %s.measures me,
                                    %s.event_time et
                                """ % (self.service,self.service,
                                    self.service,self.service,
                                    self.service,self.service) + """
                                WHERE
                                    po.id_prc_fk = p.id_prc
                                AND
                                    po.id_opr_fk = op.id_opr
                                AND
                                    name_prc = %s
                                AND
                                    id_oty = id_oty_fk
                                AND
                                    me.id_pro_fk = id_pro
                                AND
                                    et.time_eti BETWEEN %s AND %s
                                AND
                                    me.id_eti_fk = et.id_eti
                                AND
                                    ot.name_oty = 'insitu-fixed-specimen'
                                GROUP BY 
                                    et.time_eti, et.id_eti
                            ) t,
                            """ + "%s.specimens sp" % self.service +
                            """
                            WHERE
                                sp.id_eti_fk = t.id_eti) rows
                        """, (self.procedure, self.etime[0], self.etime[1]))
                    else:
                        raise Exception("GET specimen without [specimen_id] or [etime and procedure] not allowed")
                else:
                    # retrieve specimen from id
                    rows = self.conn.select(
                        """
                            select 
                                array_to_json(array_agg(row_to_json(rows)))
                            from (
                                SELECT 
                                    t.procedure,
                                    t.observations,
                                    t."eventTime",
                                    sp.specimen
                                FROM
                                (
                                SELECT
                                    MIN(p.name_prc) as procedure,
                                    json_collect(json_build_object(op.def_opr,me.val_msr)) as observations,
                                    et.time_eti as "eventTime",
                                    et.id_eti
                                FROM
                                    %s.procedures p,
                                    %s.proc_obs po,
                                    %s.observed_properties op,
                                    %s.obs_type ot,
                                    %s.measures me,
                                    %s.event_time et
                                """ % (self.service,self.service,
                                    self.service,self.service,
                                    self.service,self.service) + """
                                WHERE
                                    po.id_prc_fk = p.id_prc
                                AND
                                    po.id_opr_fk = op.id_opr
                                AND
                                    id_oty = id_oty_fk
                                AND
                                    me.id_pro_fk = id_pro
                                AND
                                    me.id_eti_fk = et.id_eti
                                AND
                                    ot.name_oty = 'insitu-fixed-specimen'
                                GROUP BY 
                                    et.time_eti, et.id_eti
                            ) t,
                            """ + "%s.specimens sp" % self.service +
                            """
                            WHERE
                                sp.id_eti_fk = t.id_eti
                                AND
	                            sp.identifier = %s) rows
                            """, (self.identifier,))
                if rows:
                    self.setMessage("Specimen(s) successfully retrived")
                    if len(rows[0][0]) < 2:
                        self.setData(rows[0][0][0])
                    else:
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
                if 'data' not in self.json or self.json['data'] is None:
                    raise Exception(
                        "POST specimen without data not allowed")
                
                if 'forceInsert' in self.json:
                    self.force = self.json['forceInsert']
                
                # verify specimen procedure exists and get info
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

                # loop dataset and insert specimens & observations
                if not isinstance(self.json['data'], list):
                    self.json['data'] = [self.json['data']]

                id_specs = []

                for dataset in self.json['data']:

                    if 'eventTime' not in dataset or dataset['eventTime'] is None:
                        raise Exception(
                            "POST specimen without eventTime name not allowed")                             

                    def check_sampling(sampling):
                        # If the end position exists the new measures must be after
                        if ep is not None and sampling <= ep:
                            return False
                        # Check that the sampling time is before now
                        if sampling > now:
                            return False
                        return True
                    
                    # get and verify specimen eventTime
                    try:
                        eventTime = iso.parse_datetime(dataset['eventTime'])
                    except:
                        raise Exception(
                            "Procedure %s, Sampling time (%s) "
                            "wrong format" % (
                                name_prc, eventTime
                            )
                        )

                    if self.force is True:
                        if check_sampling(eventTime) is False:
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

                    data = []
                    # set observedProperties data values
                    for row in rows:

                        val = dataset['observations'][row['def_opr']]
                        
                        if row[8]:
                            pco = json.loads(row[8]) # constraint of the observation (level 0)
                        else:
                            pco = None
                        if row[3]:
                            pcp = json.loads(row[3]) # constraint of the procedure (level 1)
                        else:
                            pcp = None

                        # set qualityIndex if not set
                        if row['def_opr']+":qualityIndex" in dataset['observations']:
                            qi = dataset['observations'][row['def_opr']+":qualityIndex"]
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
                            identifier,
                            id_eti_fk,
                            specimen
                        )
                        """ % self.servicename) + """
                                VALUES (%s, %s, %s, %s)
                            RETURNING identifier;
                        """,
                        (
                            int(self.serviceconf.getobservation['default_qi']),
                            dataset["specimen"]["identifier"],
                            int(id_eti[0][0]),
                            json.dumps(dataset["specimen"])
                        )
                    )[0]

                    id_specs.append(id_spec)

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
                self.setMessage("Specimen %s succesfully inserted" % len(id_specs))
                self.setData(id_specs)

            except Exception as e:
                self.conn.rollbackTransaction()
                print(traceback.print_exc(), file=sys.stderr)
                self.setException("Error in POST sepcimen (%s): %s" % (type(e), e))
                           
    def executePut(self):
        """
        Method for executing a PUT requests that updates an existing Specimen but not associated data
        If you want to change data also, please use a combination of DELETE & POST specimen wa-requests

        """
        if self.service == "default":
            raise Exception("speciemns operation can not be done for default service instance.")
        else:
            try:
                if self.specimen_id is None:
                    if self.etime is not None and self.procedure is not None:
                        if len(self.etime) > 1:
                            raise Exception("UPDATE etime parameter accept single time"
                                            " [2019-12-30T16:25:00+01] value")

                        # update the specimen by eventTime and procedure_name
                        rows = self.conn.executeInTransaction(
                            """
                                UPDATE
                                    %s.specimens
                                    """ % (self.service) + """
                                SET 
                                    specimen = %s
                                WHERE
                                    id_spec = ANY (
                                        SELECT 
                                            s.id_spec
                                        FROM
                                        """ + """
                                            %s.specimens s,
                                            %s.event_time et,
                                            %s.procedures p
                                            """ % (self.service,
                                            self.service,
                                            self.service) + """
                                        WHERE
                                            p.name_prc = %s
                                            AND
                                            p.id_prc = et.id_prc_fk
                                            AND
                                            et.time_eti = %s
                                            AND
                                            et.id_eti = s.id_eti_fk
                                    )
                                RETURNING *;
                            """, 
                            (json.dumps(self.json), self.procedure, self.etime[0])
                            )

                else:
                    # update the specimen by id
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
        Method for executing a DELETE requests that remove an existing SOS speciemn and related data
        
        """
        if self.service == "default":
            raise Exception("speciemns operation can not be done for default service instance.")
        else:
            try:
                if self.identifier is None:
                    if self.etime is not None and self.procedure is not None:
                        if len(self.etime) == 1:
                            self.etime = self.etime * 2
                        elif len(self.etime) == 2:
                            pass
                        else:
                            raise Exception("etime parameter accept single time"
                                            " [2019-12-30T16:25:00+01]"
                                            " or pariod [2019-12-30T16:25:00+01"
                                            "/2019-12-31T16:25:00+01] values")
                        
                        # delete specimen by eventTime and procedure_name
                        rows = self.conn.executeInTransaction(
                            """
                            DELETE
                            FROM 
                            %s.event_time e
                            WHERE
                                e.id_eti = ANY (
                                   SELECT 
                                        id_eti_fk
                                    FROM 
                                        %s.specimens s,
                                        %s.event_time et,
	                                    %s.procedures p""" % (
                                        self.service,
                                        self.service,
                                        self.service,
                                        self.service) + """
                                    WHERE
                                        p.name_prc = %s
                                        AND
                                        p.id_prc = et.id_prc_fk
                                        AND
                                        et.time_eti BETWEEN %s AND %s
                                        AND
                                        et.id_eti = s.id_eti_fk
                                )
                            RETURNING id_eti;
                        """, (self.procedure, self.etime[0], self.etime[1]))

                        # get start-end position
                        if rows:
                            trows = self.conn.select(
                                """
                                    SELECT
                                        procedures.stime_prc,
                                        procedures.etime_prc
                                    FROM
                                        %s.procedures""" % (self.service) + """
                                    WHERE
                                        procedures.name_prc = %s
                                """, (self.procedure,)
                            )
                        
                        bp = trows[0][0]
                        ep = trows[0][1]
                        bpu = False
                        epu = False

                        # evalaute if begin/end position of the procedure
                        # should be updated
                        #------------------------------------------------

                        # deleted inteval crosses begin position
                        if (self.etime[0] < bp < self.etime[1]) and self.etime[1] < ep:
                            bp = self.etime[1]
                            bpu = True
                        
                        # deleted interval crosses end position
                        if (self.etime[0] < ep < self.etime[1]) and self.etime[0] > bp:
                            ep = self.etime[0]
                            epu = True
                        
                        # deleted interval cover all observed period
                        if (self.etime[0] < bp and self.etime[1] > ep):
                            ep = None
                            bp = None
                            bpu = True
                            epu = True

                        # update begin position
                        if bpu:
                            self.conn.executeInTransaction(
                                ("""
                                    UPDATE %s.procedures
                                """ % self.servicename) + """
                                    SET stime_prc=%s WHERE name_prc=%s
                                """,
                                (
                                    bp,
                                    self.procedure
                                )
                            )
                        
                        # update end position
                        if epu:
                            self.conn.executeInTransaction(
                                ("""
                                    UPDATE %s.procedures
                                """ % self.servicename) + """
                                    SET etime_prc=%s WHERE name_prc=%s
                                """,
                                (
                                    ep,
                                    self.procedure
                                )
                            )
                    
                else:
                    # delete specimen by identifier
                    rows = self.conn.executeInTransaction(
                        """
                            DELETE
                            FROM 
                            %s.event_time e""" % (self.service) + """
                            WHERE
                                e.id_eti = ANY (
                                    SELECT id_eti_fk
                                    FROM %s.specimens """ % (self.service) + """
                                    WHERE identifier = %s
                                )
                            RETURNING id_eti;
                        """, (self.identifier,))

                self.conn.commitTransaction()
                if rows:
                    self.setMessage("Specimen(s) and related data succesfully deleted" % rows)
                else:
                    self.setMessage("Specimen(s) not found!")
                
            except Exception as e:
                self.conn.rollbackTransaction()
                print(traceback.print_exc(), file=sys.stderr)
                self.setException(
                    "Error in DELETE sepcimen (%s): %s" % (type(e), e))
