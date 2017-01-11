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

__author__ = 'Massimiliano Cannata, Milan Antonovic'
__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__credits__ = []
__license__ = 'GPL2'
__version__ = '1.0'
__maintainer__ = 'Massimiliano Cannata, Milan Antonovic'
__email__ = 'geoservice@supsi.ch'

import os
import sys
import json
import traceback
from walib import procedure, utils, databaseManager
from walib.resource import waResourceService
import lib.requests as requests

convertToSec = {
    'min': lambda x: x * 60,
    'h': lambda x: x * 3600,
    'd': lambda x: x * 24 * 3600,
    's': lambda x: x,
    'ms': lambda x: x/1000,
    'us': lambda x: x/1000000,
}


class waProcedures(waResourceService):
    """class to handle SOS service objects, support GET and POST method"""
    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)
        self.servicename = self.pathinfo[2]
        if not self.pathinfo[-1] == "procedures" and len(self.pathinfo) > 4:
            self.procedurename = self.pathinfo[4]
        else:
            self.procedurename = None

    def executePost(self, db=True):
        """Method for executing a POST requests that create a new SOS procedure

        @note: This method creates:
            1. Create a new procedure sending an XML to the istsos service

        The POST must be in Json format:

        >>> {
                "system_id": "P_TRE",
                "system": "P_TRE",
                "description": "ciao",
                "keywords": "uno,due,tre",
                "identification": [
                    {
                        "definition":"urn:ogc:def:identifier:OGC:P_TRE",
                        "name":"uniqueID",
                        "value":"urn:ogc:def:procedure:x-istsos:1.0:test"
                    }
                ],
                "classification": [
                    {
                        "name": "System Type",
                        "definition":
                            "urn:ogc:def:classifier:x-istsos:1.0:systemType",
                        "value": "insitu-fixed-point"
                    },
                    {
                        "name": "Sensor Type",
                        "definition":
                            "urn:ogc:def:classifier:x-istsos:1.0:sensorType",
                        "value": "bukket"
                    }
                ],
                "characteristics": "",
                "contacts": [],
                "documentation": [],
                "location": {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": ["123","456"]
                    },
                    "crs": {
                        "type": "name",
                        "properties": {"name": "EPSG:21781"}
                    },
                    "properties": {"name": "LUGANO"}
                },
                "interfaces": "",
                "inputs": [],
                "history": [],
                "capabilities": [
                    {
                        "name": "Memory Capacity",
                        "description": "",
                        "definition":
                            "urn:ogc:def:classifier:x-istsos:1.0:" +
                            "memoryCapacity",
                        "uom": "Byte",
                        "value": "131"
                    },
                    {
                        "name": "Sampling time resolution",
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0" +
                                      ":samplingTimeResolution",
                        "uom": "iso8601",
                        "value": "PT10M"
                    },
                    {
                        "name": "Acquisition time resolution",
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0" +
                                      ":acquisitionTimeResolution",
                        "uom": "iso8601",
                        "value": "PT1H"
                    }
                ],
                "outputs": [
                    {
                        "name": "Time",
                        "definition": "urn:ogc:def:dataType:x-istsos:1.0:time",
                        "uom": "iso8601",
                        "description": "",
                        "constraint": {
                            "role": "urn:ogc:def:classifiers:x-istsos:1.0" +
                                    ":dataAvailability",
                            "min": "",
                            "max": "",
                            "interval": [123,456],
                            "valuelist": ""
                        }
                    },
                    {
                        "name": "Conductivity",
                        "definition": "urn:ogc:def:phenomenon:x-istsos:1.0" +
                                      ":conductivity",
                        "uom": "Pressure",
                        "description": "foo bar",
                        "constraint": {
                            "role": "urn:ogc:def:classifiers:x-istsos:1.0" +
                                    ":qualityIndex:check:reasonable",
                            "interval": ["12","65"]
                        }
                    }
                ]
            }
        """
        #verify no service name in url
        if not self.procedurename is None:
            raise Exception(
                "POST action with url procedure name not supported")

        proc = procedure.Procedure(self.serviceconf)

        proc.loadDICT(self.json)
        smlstring = proc.toRegisterSensor(indent=False)

        headers = {"Content-type": "text/xml"}
        if 'HTTP_AUTHORIZATION' in self.waEnviron:
            headers['Authorization'] = self.waEnviron['HTTP_AUTHORIZATION']

        response = requests.post(
            self.serviceconf.serviceurl["url"],
            data=smlstring,
            headers=headers
        )

        try:
            response.raise_for_status()
            if response.text.find("AssignedSensorId") > 0:
                self.setMessage("%s" % response.text)

                # UPDATE MQTT Broker config
                #print proc.data
                if "mqtt" in proc.data:
                    try:
                        servicedb = databaseManager.PgDB(
                            self.serviceconf.connection['user'],
                            self.serviceconf.connection['password'],
                            self.serviceconf.connection['dbname'],
                            self.serviceconf.connection['host'],
                            self.serviceconf.connection['port']
                        )
                        sql = "UPDATE %s.procedures" % self.service
                        sql += """
                            SET
                                mqtt_prc = %s
                            WHERE
                                name_prc = %s
                        """
                        #print proc.data['mqtt']
                        if proc.data['mqtt'] is not None and (
                                proc.data['mqtt'] != ''):
                            #print " > Not null: updating"
                            #print sql % (
                            #    json.dumps(proc.data['mqtt']),
                            #    proc.data['system'])
                            servicedb.execute(sql, (
                                json.dumps(proc.data['mqtt']),
                                proc.data['system']))
                        else:
                            #print " > Null: removing"
                            servicedb.executeInTransaction(sql, (
                                None, proc.data['system']))

                    except Exception:
                        traceback.print_exc(file=sys.stderr)
                        raise Exception("MQTT Broker configuration wrong")

            else:
                self.setException(
                    "Register sensor failed - Communication: %s - "
                    "Response: %s" % (response.status_code, response.text))

        except Exception as e:
            self.setException(
                "Register sensor failed - Communication: %s %s - "
                "Response: %s" % (response.status_code, e, response.text))

    def executeDelete(self):
        """
        Method for executing a DELETE requests that erase a SOS procedure

            @note: This method delete:
                1. the given procedure

        """
        if self.procedurename is None:
            raise Exception(
                "DELETE action without url procedure name not supported")

        try:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port']
            )

            #DELETE from database in transaction
            sql = "DELETE from %s.procedures" % self.service
            sql += " WHERE name_prc = %s"
            params = (self.procedurename,)
            servicedb.executeInTransaction(sql, params)

            #DELETE sensorML
            procedureMLpath = os.path.join(
                self.sensormlpath,
                self.procedurename+".xml")
            os.remove(procedureMLpath)

            #COMMIT transaction
            servicedb.commitTransaction()
            self.setMessage(
                "Procedure '%s' successfully deleted" % self.procedurename)
        except Exception as e:
            self.setException("%s" % e)

    def executePut(self):
        """
        Method for executing a PUT requests that update a SOS
        sensorML procedure

            @note:  This method replace old sensorML with the new one,
                    note that database objectes are not updated. To update
                    entirely a procedure consider to delete and recreate it.
                1. ...

            The Put must be in Json format:

            >>> {
                    ...
                }
        """

        proc = procedure.Procedure()
        proc.loadDICT(self.json)

        print >> sys.stderr, self.json

        if not "system" in proc.data:
            raise Exception("system parameter is mandatory for PUT request")

        smlstring = proc.toXML()
        f = open(os.path.join(
            self.sensormlpath,
            self.procedurename+".xml"), 'w')

        f.write(smlstring)
        f.close()
        self.setMessage("SensorML successfully updated")
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port']
        )
        msg1 = ""
        msg2 = ""

        # update foi geometry inside db
        if proc.data['location']:
            name = proc.data['location']['properties']['name']
            foiX = float(proc.data['location']['geometry']['coordinates'][0])
            foiY = float(proc.data['location']['geometry']['coordinates'][1])
            foiZ = float(proc.data['location']['geometry']['coordinates'][2])
            foiSrid = int(proc.data['location']['crs']['properties']['name'])

            epsg = int(self.serviceconf.geo['istsosepsg'])

            sql = "UPDATE %s.foi " % self.service
            sql += """SET geom_foi = ST_Transform(
                              ST_GeomFromText('POINT(%s %s %s)',%s), %s)
                WHERE name_foi = %s"""

            params = (foiX, foiY, foiZ, foiSrid, epsg, name)
            servicedb.executeInTransaction(sql, params)

        if proc.data['system'] != self.procedurename:
            #rename procedure in transaction
            sql = "UPDATE %s.procedures" % self.service
            sql += " SET name_prc = %s WHERE name_prc= %s"
            params = (proc.data["system"], self.procedurename)
            servicedb.executeInTransaction(sql, params)

            #rename sensorML file
            os.rename(
                os.path.join(
                    self.sensormlpath,
                    self.procedurename+".xml"),
                os.path.join(
                    self.sensormlpath,
                    self.json["system"]+".xml"))

            #commit transaction
            msg1 = "Procedure '%s' successfully renamed to '%s'" % (
                self.procedurename,
                str(self.json["system"]))

        # UPDATE MQTT Broker config
        if "mqtt" in proc.data:
            try:
                sql = "UPDATE %s.procedures" % self.service
                sql += """
                    SET
                        mqtt_prc = %s
                    WHERE
                        name_prc = %s
                """
                if proc.data['mqtt'] is not None and proc.data['mqtt'] != '':
                    servicedb.executeInTransaction(sql, (
                        json.dumps(proc.data['mqtt']), self.procedurename))
                else:
                    servicedb.executeInTransaction(sql, (
                        None, self.procedurename))

            except Exception:
                traceback.print_exc(file=sys.stderr)
                raise Exception("MQTT Broker configuration wrong")

        # Update for sapling time and acquisition time
        time_acq_val = None
        time_sam_val = None

        for cap in proc.data['capabilities']:
            if 'samplingTimeResolution' in cap['definition']:
                time_sam_val = convertToSec[cap['uom']](int(cap['value']))

            elif 'acquisitionTimeResolution' in cap['definition']:
                time_acq_val = convertToSec[cap['uom']](int(cap['value']))

        sql = "UPDATE %s.procedures" % self.service
        sql += """
            SET
                time_res_prc = %s,
                time_acq_prc = %s
            WHERE
                name_prc = %s"""
        params = (time_sam_val, time_acq_val, self.procedurename)
        servicedb.executeInTransaction(sql, params)

        #allows to update observed property constraints
        for obsprop in proc.data['outputs']:
            if "constraint" in obsprop:
                if "role" in obsprop["constraint"]:
                    if obsprop["constraint"]["role"] == (
                            "urn:ogc:def:classifiers:x-istsos:"
                            "1.0:qualityIndex:check:reasonable"):
                        sql = """
                            SELECT
                                id_prc,
                                id_opr,
                                id_uom
                            FROM %s.procedures,
                                 %s.observed_properties,
                                 %s.uoms""" % (self.service,
                                               self.service,
                                               self.service)
                        sql += """
                            WHERE
                                name_prc=%s
                            AND
                                def_opr=%s
                            AND
                                name_uom=%s"""
                        params = (proc.data['system'],
                                  obsprop["definition"],
                                  obsprop["uom"])
                        try:
                            ids = servicedb.select(sql, params)
                        except Exception:
                            raise Exception(
                                "Procedure-observedProperty-UnitOfMeasure "
                                "triplet not found in system, SQL: %s" % (
                                    servicedb.mogrify(sql, params)))

                        if len(ids) == 1:
                            #update database values for the constraints
                            sql = "UPDATE %s.proc_obs" % self.service
                            sql += """
                                SET
                                    constr_pro = %s
                                WHERE
                                    id_prc_fk=%s
                                AND
                                    id_opr_fk=%s
                                AND
                                    id_uom_fk=%s"""
                            #calculate json string
                            upd = {}
                            if "role" in obsprop["constraint"]:
                                upd["role"] = obsprop["constraint"]["role"]
                            if "min" in obsprop["constraint"]:
                                try:
                                    upd["min"] = obsprop["constraint"]["min"]
                                except:
                                    raise Exception(
                                        "'min' constraint requires a "
                                        "float value")

                            elif "max" in obsprop["constraint"]:
                                try:
                                    upd["max"] = obsprop["constraint"]["max"]
                                except:
                                    raise Exception(
                                        "'max' constraint requires a "
                                        "float value")

                            elif "interval" in obsprop["constraint"]:
                                try:
                                    upd["interval"] = [
                                        float((
                                            obsprop["constraint"]
                                            )["interval"][0]
                                        ),
                                        float((
                                            obsprop["constraint"]
                                            )["interval"][1])
                                    ]
                                except:
                                    raise Exception(
                                        "'interval' constraint requires "
                                        "an array of two float value")

                            elif "valueList" in obsprop["constraint"]:
                                try:
                                    upd["valueList"] = [
                                        float(a) for a in (
                                            obsprop["constraint"]["valueList"]
                                        )]
                                except:
                                    raise Exception(
                                        "'interval' constraint requires "
                                        "an array of two float value")

                            params = (
                                json.dumps(upd),
                                ids[0]['id_prc'],
                                ids[0]['id_opr'],
                                ids[0]['id_uom'])
                            try:
                                ids = servicedb.executeInTransaction(
                                    sql, params)
                                msg2 = ("observed properties constraints "
                                        "have been updated")
                            except:
                                raise Exception(
                                    "Procedure-observedProperty-UnitOfMeasure "
                                    "triplet not found in system")

                else:
                    sql = """
                        SELECT
                            id_prc,
                            id_opr,
                            id_uom
                        FROM
                            %s.procedures,
                            %s.observed_properties,
                            %s.uoms""" % (self.service,
                                          self.service,
                                          self.service)
                    sql += """
                        WHERE
                            name_prc=%s
                        AND
                            def_opr=%s
                        AND
                            name_uom=%s"""
                    params = (
                        proc.data['system'],
                        obsprop["definition"],
                        obsprop["uom"])
                    try:
                        ids = servicedb.select(sql, params)
                    except Exception:
                        raise Exception(
                            "Procedure-observedProperty-UnitOfMeasure "
                            "triplet not found in system, SQL: %s" % (
                                servicedb.mogrify(sql, params)))

                    if len(ids) == 1:
                        #update database values for the constraints
                        sql = "UPDATE %s.proc_obs" % self.service
                        sql += """
                            SET
                                constr_pro = NULL
                            WHERE
                                id_prc_fk=%s
                            AND
                                id_opr_fk=%s
                            AND
                                id_uom_fk=%s"""

                        params = (
                            ids[0]['id_prc'],
                            ids[0]['id_opr'],
                            ids[0]['id_uom'])
                        try:
                            ids = servicedb.executeInTransaction(sql, params)
                            msg2 = ("observed properties constraints "
                                    "have been updated")
                        except:
                            raise Exception(
                                "Procedure-observedProperty-UnitOfMeasure "
                                "triplet not found in system")

        servicedb.commitTransaction()
        if msg1 and msg2:
            self.setMessage(" and ".join([msg1, msg2]))
        elif msg1:
            self.setMessage(msg1)
        else:
            self.setMessage(msg2)

    def executeGet(self):
        """
        Method for executing a GET requests that rename a SOS service

        {
            "message": "Sensor Description secessfully loaded",
            "total": 1,
            "data": {
                "inputs": [],
                "description": "",
                "classification": [
                    {
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0" +
                                      ":systemType",
                        "name": "System Type",
                        "value": "insitu-fixed-point"
                    },
                    {
                        "definition": "urn:ogc:def:classifier:x-istsos:1.0" +
                                      ":sensorType",
                        "name": "Sensor Type",
                        "value": "temperature"
                    }
                ],
                "characteristics": "",
                "interfaces": "",
                "keywords": "",
                "contacts": [],
                "assignedSensorId": "ec08e1f51ab879f4e1796f3c187daff6",
                "documentation": [],
                "system": "DEMO_1",
                "capabilities": [],
                "identification": [],
                "location": {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            "8.88",
                            "45.45"
                        ]
                    },
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "4326"
                        }
                    },
                    "type": "Feature",
                    "properties": {
                        "name": "lugano"
                    }
                },
                "outputs": [
                    {
                        "definition": "urn:ogc:def:parameter:x-istsos::time" +
                                      ":iso8601",
                        "constraint": {
                            "max": "",
                            "interval": [
                                "2007-11-03T14:00:00+01:00",
                                "2011-12-07T18:00:00+01:00"
                            ],
                            "role": "",
                            "valuelist": "",
                            "min": ""
                        },
                        "name": "Time",
                        "uom": "",
                        "description": ""
                    },
                    {
                        "definition": "urn:ogc:def:parameter:x-istsos::meteo" +
                                      ":air:temperature",
                        "constraint": {
                            "max": "",
                            "interval": "",
                            "role": "",
                            "valuelist": "",
                            "min": ""
                        },
                        "name": "meteo-air-temperature",
                        "uom": "deg",
                        "description": ""
                    }
                ],
                "system_id": "DEMO_1",
                "history": []
            },
            "success": true
        }
        """

        try:
            headers = {}
            if 'HTTP_AUTHORIZATION' in self.waEnviron:
                headers['Authorization'] = self.waEnviron['HTTP_AUTHORIZATION']

            res = requests.get(
                self.serviceconf.serviceurl["url"],
                params={
                    "request": "DescribeSensor",
                    "procedure": self.procedurename,
                    "outputFormat": "text/xml;subtype=\"sensorML/1.0.1\"",
                    "service": "SOS",
                    "version": "1.0.0"
                },
                headers=headers
            )
        except Exception as e:
            raise Exception(
                "Error loading DescribeSensor of '%s': %s" % (
                    self.procedurename, e))
        try:
            res.raise_for_status()

        except Exception as e:
            raise Exception(
                "Error loading DescribeSensor of '%s' "
                "[STATUS CODE: %s]: %s" % (
                    self.procedurename,
                    res.status_code, e))

        try:
            smlobj = procedure.Procedure()
            smlobj.loadXML(res.content)

        except Exception as e:
            raise Exception(
                "Error loading DescribeSensor of '%s': %s" % (
                    self.procedurename, e))

        # Searching for the assignedSensorId from the database
        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port']
        )
        sql = """
               SELECT assignedid_prc, mqtt_prc
               FROM %s.procedures """ % ((self.service,))
        sql += " WHERE name_prc = %s"
        rows = servicedb.select(sql, (self.procedurename,))
        if rows:
            ret = {
                'assignedSensorId': rows[0]["assignedid_prc"],
                'mqtt': None
            }
            if rows[0]["mqtt_prc"] is not None and rows[0]["mqtt_prc"] != '':
                import json
                ret["mqtt"] = json.loads(rows[0]["mqtt_prc"])

            ret.update(smlobj.data)  # merging dictionaries
            self.setData(ret)
            self.setMessage("Sensor Description successfully loaded")
        else:
            self.setException(
                "Unable to find the procedure's assignedSensorId")


class waGetlist(waResourceService):
    """
    Class to execute
        istsos/services/{serviceName}/procedures/operations/getlist
    """
    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)
        self.servicename = self.pathinfo[2]

    def executeGet(self):
        if self.servicename == "default":
            raise Exception("getlist operation can not be done for "
                            "default service instance.")
        else:
            data = []
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port']
            )
            if self.waEnviron['parameters'] and (
                    'tzoffset' in self.waEnviron['parameters']):
                tzoffset = self.waEnviron['parameters']['tzoffset'][0]
                servicedb.setTimeTZ(tzoffset)

            proceduresList = utils.getProcedureNamesList(
                servicedb, self.servicename)

            for proc in proceduresList:
                elem = {}
                elem.update(proc)
                ops = utils.getObservedPropertiesFromProcedure(
                    servicedb, self.servicename, proc["name"])
                if ops is not None:
                    elem["observedproperties"] = [{
                        "name": op["name"],
                        "uom": op["uom"]
                    } for op in ops]

                else:
                    elem["observedproperties"] = []

                offs = utils.getOfferingsFromProcedure(
                    servicedb, self.servicename, proc["name"])

                if offs is not None:
                    elem["offerings"] = [off["name"] for off in offs]

                else:
                    elem["offerings"] = []

                data.append(elem)

            self.setData(data)
            self.setMessage(
                "Procedures of service <%s> successfully retrived" % (
                    self.servicename))


class waGetGeoJson(waResourceService):
    """
    Class to execute
        istsos/services/{serviceName}/procedures/operations/geojson/{epsg}
    """
    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)

        if self.waEnviron['parameters'] and (
                self.waEnviron['parameters']['epsg']):
            self.epsg = self.waEnviron['parameters']['epsg'][0]
        else:
            self.epsg = self.serviceconf.get("geo")['istsosepsg']

        self.offering = None
        if self.waEnviron['parameters'] and (
                'offering' in self.waEnviron['parameters']):
            self.offering = self.waEnviron['parameters']['offering'][0]

        self.observedProperty = None
        if self.waEnviron['parameters'] and (
                'observedProperty' in self.waEnviron['parameters']):
            self.observedProperty = (
                self.waEnviron['parameters']['observedProperty'][0])

        self.procedure = None
        if self.waEnviron['parameters'] and (
                'procedure' in self.waEnviron['parameters']):
            self.procedure = self.waEnviron['parameters']['procedure'][0]

    def executeGet(self):
        if self.service == "default":
            raise Exception(
                "getlist operation can not be done for "
                "default service instance.")

        else:
            try:
                data = {
                    "type": "FeatureCollection",
                    "features": []
                }

                servicedb = databaseManager.PgDB(
                    self.serviceconf.connection['user'],
                    self.serviceconf.connection['password'],
                    self.serviceconf.connection['dbname'],
                    self.serviceconf.connection['host'],
                    self.serviceconf.connection['port']
                )

                proceduresList = utils.getProcedureNamesList(
                    servicedb, self.service,
                    offering=self.offering,
                    procedure=self.procedure)

                for proc in proceduresList:
                    if proc['samplingTime']['beginposition'] == '':
                        headers = {}
                        if 'HTTP_AUTHORIZATION' in self.waEnviron:
                            headers['Authorization'] = (
                                self.waEnviron['HTTP_AUTHORIZATION'])

                        res = requests.get(
                            self.serviceconf.serviceurl["url"],
                            params={
                                "request": "DescribeSensor",
                                "procedure": proc['name'],
                                "outputFormat": (
                                    "text/xml;"
                                    "subtype=\"sensorML/1.0.1\""),
                                "service": "SOS",
                                "version": "1.0.0"
                            },
                            headers=headers
                        )
                        smlobj = procedure.Procedure()
                        try:
                            smlobj.loadXML(res.content)
                        except Exception as e:
                            print >> sys.stderr, "\n\nSML: %s\n\n" % (
                                res.content)
                            raise Exception(
                                "Error loading DescribeSensor of '%s' "
                                "[STATUS CODE: %s]: %s" % (
                                    proc['name'],
                                    res.status_code, e))

                        ret = {}
                        ret.update(smlobj.data)

                        if 'constraint' in ret['outputs'][0]:
                            proc['samplingTime']['beginposition'] = (
                                ret['outputs'][0]['constraint']['interval'][0])

                            proc['samplingTime']['endposition'] = (
                                ret['outputs'][0]['constraint']['interval'][1])
                        else:
                            proc['samplingTime']['beginposition'] = ''
                            proc['samplingTime']['endposition'] = ''

                    elem = {}
                    elem.update(proc)
                    ops = utils.getObservedPropertiesFromProcedure(
                        servicedb, self.service, proc["name"])
                    if ops is not None:
                        if self.observedProperty:
                            elem["observedproperties"] = []
                            opPresent = False
                            for op in ops:
                                if self.observedProperty == op["def"]:
                                    opPresent = True
                                elem["observedproperties"].append({
                                    "name": op["name"],
                                    "def":  op["def"],
                                    "uom":  op["uom"]
                                })
                            if not opPresent:
                                continue

                        else:
                            elem["observedproperties"] = [{
                                "name": op["name"],
                                "def":  op["def"],
                                "uom":  op["uom"]
                            } for op in ops]

                    else:
                        elem["observedproperties"] = []

                    offs = utils.getOfferingsFromProcedure(
                        servicedb, self.service, proc["name"])
                    if offs is not None:
                        elem["offerings"] = [off["name"] for off in offs]

                    else:
                        elem["offerings"] = []

                    geom = utils.getGeoJSONFromProcedure(
                        servicedb, self.service, proc["name"], self.epsg)
                    if geom is None:
                        continue

                    data["features"].append({
                        "type": "Feature",
                        "geometry": geom,
                        "properties": elem
                    })

                self.setData(data)
            except Exception as e:
                self.setMessage("%s" % e)

    def setData(self, data):
        """ Set data in response """
        self.response = data
