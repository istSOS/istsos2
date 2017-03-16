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

from walib import utils, databaseManager, configManager
from walib.resource import waResourceAdmin, waResourceService
import sys
import os
import shutil
import errno
import traceback
import psycopg2
from datetime import datetime
from lib.etree import et
import lib.requests as requests
from lib import isodate as iso

reurl = (r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+'
         '([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')


class waServices(waResourceAdmin):
    """class to handle SOS service objects, support GET and POST method"""
    def __init__(self, waEnviron):
        waResourceAdmin.__init__(self, waEnviron)
        self.urlservicename = self.pathinfo[-1] if (
            not self.pathinfo[-1] == "services") else None

    def executePost(self, db=True):
        """Method for executing a POST requests that initialize a new
        SOS service

        .. note::  This method creates:
            1. service folder,
            2. service configuration file
            3. C{sensorML} folder
            4. C{virtual procedures} folder
            5. a new schema with the same name of your service
            6. istSOS tables and relations in the new schema

        The POST must be in Json format with mandatory service key, if
        databease keys are not provided the server default connection are used:

        >>> {
                "service" : "service_name",
                "user" : "pinco"
                "password" : "pallino"
                "dbname" : "sos_db"
                "host" : "10.7.5.3"
                "port" : "5432"
            }
        """

        # check to be at service level without serviceID provided in url
        if not self.urlservicename is None and db is True:
            raise Exception("POST action with url service name not supported")

        # check that service name was provided
        if not "service" in self.json:
            raise Exception("PUT action require the new service"
                            "name sent within request body")

        # validate schemaname against injection
        utils.preventInjection(self.json["service"])

        # validate db connection
        jsoncount = 0
        dbkeys = ["user", "password", "dbname", "host", "port"]
        for key in dbkeys:
            if key in self.json:
                jsoncount += 1

        defaultcfgpath = os.path.join(
            self.waEnviron["services_path"], "default.cfg")
        defaultconfig = configManager.waServiceConfig(defaultcfgpath)
        if jsoncount == 5:
            servicedb = databaseManager.PgDB(
                self.json["user"],
                self.json["password"],
                self.json["dbname"],
                self.json["host"],
                self.json["port"])

        elif jsoncount == 0:
            defaultconnection = defaultconfig.get("connection")
            servicedb = databaseManager.PgDB(
                defaultconnection['user'],
                defaultconnection['password'],
                defaultconnection['dbname'],
                defaultconnection['host'],
                defaultconnection['port'])

        else:
            raise Exception("db parameters [service, user, password, dbname, "
                            "host, port] must be all or none provided")

        # verify that the schema does not exist
        sql = "SELECT count(*) from pg_namespace WHERE nspname = %s"
        par = (self.json["service"],)
        res = servicedb.select(sql, par)
        if len(res) == 1:
            pass
        else:
            raise Exception(
                "a schema '%s' already exist" % self.json["service"])

        # check if service folder does not exist: in case create it
        newservicepath = os.path.join(
            self.waEnviron["services_path"],
            self.json["service"])
        try:
            os.makedirs(newservicepath)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                raise Exception("Service %s already exist" % (
                    self.json["service"]))
            else:
                raise exc

        # create configuration file
        configfile = "%s.cfg" % os.path.join(
            self.waEnviron["services_path"],
            self.json["service"],
            self.json["service"])

        open(configfile, 'w').close()
        # create sensorML folder
        smldir = os.path.join(
            self.waEnviron["services_path"], self.json["service"], "sml")

        os.makedirs(smldir)
        # create virtual procedure path
        virtualdir = os.path.join(
            self.waEnviron["services_path"], self.json["service"], "virtual")

        os.makedirs(virtualdir)
        if db is True:
            try:
                #create schema
                sql = "CREATE SCHEMA %s" % self.json["service"]
                servicedb.executeInTransaction(sql)

                #set db path
                sql = "SET search_path = %s, public, pg_catalog" % (
                    self.json["service"])
                servicedb.executeInTransaction(sql, par)

                #create tableas and relations
                from walib import sqlschema
                defaultepsg = defaultconfig.get("geo")['istsosepsg']
                import sys
                if not "epsg" in self.json:
                    sql = sqlschema.createsqlschema.replace(
                        "$SRID", defaultepsg).replace(
                        "$schema", self.json["service"])
                else:
                    sql = sqlschema.createsqlschema.replace(
                        "$SRID", self.json['epsg'])

                    #set correct default EPSG of the new service
                    newconfig = configManager.waServiceConfig(
                        defaultcfgpath, configfile)

                    allowed = newconfig.get('geo')['allowedEPSG'].split(",")
                    if self.json['epsg'] in allowed:
                        newallowedepsg = ",".join(
                            [x for x in allowed if x != self.json['epsg']])
                        newconfig.put('geo', 'allowedEPSG', newallowedepsg)
                        newconfig.save()

                    newconfig.put('geo', 'istsosepsg', self.json['epsg'])
                    newconfig.save()

                servicedb.executeInTransaction(sql)

                servicedb.commitTransaction()

            except:
                servicedb.rollbackTransaction()
                raise

        # Setting proxy configuration
        from walib.istsos.services.configsections import serviceurl
        surl = configManager.waServiceConfig(defaultcfgpath, configfile)

        url = ''
        if self.waEnviron['server_port'] == '80':
            url = 'http://'
        else:
            url = 'https://'

        url = "%s%s%s/%s" % (
            url, self.waEnviron['server_name'],
            self.waEnviron['script_name'],
            self.json["service"])

        surl.put("serviceurl", "url", url)
        surl.save()

        self.setMessage("New service <%s> correctly created" % str(
            self.json["service"]))

    def executeDelete(self):
        """
        Method for executing a DELETE requests that erase a SOS service

            .. note::  This method delete:
                1. service folder,
                2. service configuration file
                3. C{sensorML} folder
                4. C{virtual procedures} folder
                5. a new schema with the same name of your service
                6. istSOS tables and relations in the new schema

            The POST must be in Json format with mandatory service key

            >>> {
                    "service" : "service_name"
                }
        """
        #check schemaname input
        if self.urlservicename is None:
            raise Exception("DELETE action without url service"
                            "name not supported")

        #validate schemaname against injection
        utils.preventInjection(self.urlservicename)

        #get database connection and initialize it
        defaultcfgpath = os.path.join(
            self.waEnviron["services_path"], "default.cfg")

        servicepath = os.path.join(
            self.waEnviron["services_path"], self.urlservicename)

        servicecfgpath = "%s.cfg" % os.path.join(
            self.waEnviron["services_path"],
            self.urlservicename,
            self.urlservicename)

        if not os.path.isdir(servicepath):
            raise Exception(
                "service [%s] does not exists." % self.urlservicename)

        if not os.path.isdir(os.path.join(self.waEnviron["services_path"],
                             self.urlservicename, "virtual")):
            raise Exception(
                "service [%s] misconfigured, missing <virtual> folder." % (
                    self.urlservicename))

        if not os.path.isdir(os.path.join(
                self.waEnviron["services_path"], self.urlservicename, "sml")):
            raise Exception(
                "service [%s] misconfigured, missing <sml> folder." % (
                    self.urlservicename))

        if not os.path.isfile(servicecfgpath):
            raise Exception(
                "service [%s] misconfigured, missing config file." % (
                    self.urlservicename))

        config = configManager.waServiceConfig(defaultcfgpath, servicecfgpath)
        connection = config.get("connection")
        servicedb = databaseManager.PgDB(
            connection['user'],
            connection['password'],
            connection['dbname'],
            connection['host'],
            connection['port']
        )
        #verify that the schema exist
        sql = "SELECT count(*) from pg_namespace WHERE nspname = %s"
        par = (self.urlservicename,)
        res = servicedb.select(sql, par)
        if len(res) == 1:
            pass

        else:
            raise Exception(
                "the db schema <<%s>> doesn't exist" % self.urlservicename)

        try:
            #drop schema
            sql = "DROP SCHEMA %s CASCADE" % self.urlservicename
            servicedb.executeInTransaction(sql)
            #remove service folder and subfolder contents
            shutil.rmtree(servicepath)
            servicedb.commitTransaction()

        except:
            servicedb.rollbackTransaction()
            raise

        self.setMessage("Service <%s> correctly deleted" % self.urlservicename)

    def executePut(self):
        """
        Method for executing a PUT requests that rename a SOS service

            .. note:: This method renames:
                1. create a new service folder,
                2. copy content from old to new service configuration file
                3. rename the databse schema
                4. delete old service files

            The POST must be in Json format with mandatory service key

            >>> {
                    "service" : "service_name"
                }
        """
        #check to be at service level without serviceID provided in url
        if self.urlservicename is None:
            raise Exception("PUT action with url service name not supported")

        #check that service name was provided
        if not "service" in self.json:
            raise Exception(
                "PUT action require the new service name sent within "
                "request body")

        #create a new service with new name
        try:
            self.executePost(db=False)
        except:
            raise

        #copy configuration file to new configuration file name
        try:
            defaultcfgpath = os.path.join(
                self.waEnviron["services_path"], "default.cfg")

            servicecfgpath = "%s.cfg" % os.path.join(
                self.waEnviron["services_path"], self.urlservicename,
                self.urlservicename)

            newservicecfgpath = "%s.cfg" % os.path.join(
                self.waEnviron["services_path"], self.json["service"],
                self.json["service"])

            of = open(servicecfgpath, "r")
            content = of.read()
            of.close()
            nf = open(newservicecfgpath, 'w')
            nf.write(content)
            nf.close()

        except:
            #remove new files
            shutil.rmtree(os.path.join(
                self.waEnviron["services_path"], self.json["service"]))
            raise Exception("cannot copy configuration file content")

        #rename database schema to new service name
        try:
            config = configManager.waServiceConfig(
                defaultcfgpath, servicecfgpath)
            connection = config.get("connection")
            servicedb = databaseManager.PgDB(
                connection['user'],
                connection['password'],
                connection['dbname'],
                connection['host'],
                connection['port']
            )
            sql = "ALTER SCHEMA %s RENAME TO %s" % (
                self.urlservicename, str(self.json["service"]))
            servicedb.executeInTransaction(sql)

        except Exception as tex:
            #remove new files
            shutil.rmtree(os.path.join(
                self.waEnviron["services_path"], self.json["service"]))
            raise tex

        #remove service folder and subfolder contents
        try:
            shutil.rmtree(os.path.join(
                self.waEnviron["services_path"], self.urlservicename))
        except:
            servicedb.rollbackTransaction()

        servicedb.commitTransaction()
        self.setMessage("service <%s> successfully renamed to <%s>" % (
            self.urlservicename, str(self.json["service"])))

    def executeGet(self):
        """
        Method for executing a GET requests that rename a SOS service

            .. note::  This method renames:
                1. service folder,
                2. service configuration file
                3. the databse schema

            The POST must be in Json format with mandatory service key

            >>> {
                    "service" : "service_name"
                }
        """
        #check to be at service level without serviceID provided in url
        if self.urlservicename is None:
            try:
                serviceslist = utils.getServiceList(
                    self.waEnviron["services_path"], listonly=False)

                if self.user and not self.user.isAdmin():
                    servicesAllowed = []
                    for item in serviceslist:
                        if self.user.allowedService(item['service']):
                            servicesAllowed.append(item)
                    serviceslist = servicesAllowed

            except Exception as ex:
                print >> sys.stderr, traceback.print_exc()
                raise ex

            self.setData(serviceslist)
            self.setMessage(
                "Services list successfully retrived: found [%s] services" % (
                    len(serviceslist)))

        else:
            try:
                serviceslist = utils.getServiceList(
                    self.waEnviron["services_path"], listonly=True)

                if not(self.urlservicename in serviceslist):
                    raise Exception("")

            except Exception as ex:
                print >> sys.stderr, traceback.print_exc()
                raise ex

            #get database connection and initialize it
            defaultcfgpath = os.path.join(
                self.waEnviron["services_path"], "default.cfg")

            servicecfgpath = "%s.cfg" % os.path.join(
                self.waEnviron["services_path"], self.urlservicename,
                self.urlservicename)

            config = configManager.waServiceConfig(
                defaultcfgpath, servicecfgpath)

            connection = config.get("connection")

            #test if connection is valid
            servicedb = databaseManager.PgDB(
                connection['user'],
                connection['password'],
                connection['dbname'],
                connection['host'],
                connection['port']
            )
            self.setData({
                "service": self.urlservicename,
                "user": connection['user'],
                #"password" : connection['password'],
                "password": "*************",
                "dbname": connection['dbname'],
                "host": connection['host'],
                "port": connection['port']
            })
            self.setMessage(
                "Informations of service <%s> successfully retrived" % (
                    self.urlservicename))


class waGetobservation(waResourceService):
    """class to handle SOS observations, support only the GET method"""
    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)

    def executeGet(self):
        """
        Method for executing a Get requests that create a new SOS procedure

        .. note::  This method return a Json object with
                   ObservationCollection members

        get the parameters:
        /istsos/services/{demo}/operations/{getobservation}/offerings/
            {temporary}/procedures/{P_BED&P_TRE}/observations/{rain}/
           eventtime/{last}

        The response is:
        >>> {
                "message" : "abcderfghilmnopqrstuvz",
                "total": 4,
                "data" : [
                    {
                        "samplingTime": {...},
                        "featureOfInterest": {...},
                        "observedProperty": {...},
                        "result": {...},
                        "procedure": {...}
                    },{
                        "samplingTime": {...},
                        "featureOfInterest": {...},
                        "observedProperty": {...},
                        "result": {...},
                        "procedure": {...}
                    },...
                ],
                "success": true
            }
        """
        try:
            offerings = self.pathinfo[6]
            procedures = self.pathinfo[8].replace("&", ",")
            observations = self.pathinfo[10].replace("&", ",")
            try:
                eventtime = [self.pathinfo[12], self.pathinfo[13]]
            except:
                eventtime = [self.pathinfo[12]]
        except:
            raise Exception("ERROR in pathinfo scanning")

        import lib.requests as requests

        headers = {}
        if 'HTTP_AUTHORIZATION' in self.waEnviron:
            headers['Authorization'] = self.waEnviron['HTTP_AUTHORIZATION']

        rparams = {
            "request": "GetObservation",
            "service": "SOS",
            "version": "1.0.0",
            "observedProperty": observations,
            "responseFormat": "application/json",
            "offering": offerings
        }

        if self.waEnviron['parameters'] and (
                'qualityIndex' in self.waEnviron['parameters']
                and 'False' in self.waEnviron['parameters']['qualityIndex']):
            rparams["qualityIndex"] = "False"

        else:
            rparams["qualityIndex"] = "True"

        if not procedures == "*":
            rparams.update({
                "procedure": procedures
            })

        if not eventtime[0] == "last":
            rparams.update({
                "eventTime": "/".join(eventtime)
            })

        if self.waEnviron['parameters'] and (
                'aggregatefunction' in self.waEnviron['parameters']):
            rparams.update({
                "aggregatefunction": (
                    self.waEnviron['parameters']["aggregatefunction"]),
                "aggregateinterval": (
                    self.waEnviron['parameters']["aggregateinterval"])
            })
            if 'aggregatenodata' in self.waEnviron['parameters']:
                rparams.update({
                    "aggregatenodata": (
                        self.waEnviron['parameters']["aggregatenodata"])
                })

            if 'aggregatenodataqi' in self.waEnviron['parameters']:
                rparams.update({
                    "aggregatenodataqi": (
                        self.waEnviron['parameters']["aggregatenodataqi"])
                })

        response = requests.get(
            self.serviceconf.serviceurl["url"],
            params=rparams,
            headers=headers
        )

        # build the response
        try:
            response.raise_for_status()
            obsjson = response.json()
            self.setData(obsjson["ObservationCollection"]["member"])
            self.setMessage("GetObservation requested successfully executed")
        except Exception as e:
            self.setException(
                "GetObservation request failed - Communication: "
                "%s %s - Response: %s" % (
                    response.status_code, e, response.content))


def parse_and_get_ns(file):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in et.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #   to different URI namespaces in different parts of the
                #   document. This exception serves as a reminder that this
                #   solution is not robust.  Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            if root is None:
                root = elem

    return et.ElementTree(root), ns


class waInsertobservation(waResourceService):
    """class to handle SOS observations, support only the GET method"""

    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)

    def executePost(self):
        """
        Method for executing a POST requests that insert new observations into
        a SOS procedure

        .. note::  The POST data shall be in JSON format as following:

        >>> {
            "ForceInsert" : "true",
            "Observation" : {
                "procedure": "urn:ogc:object:procedure:x-istsos:1.01.0:P_TRE",
                "AssignedSensorId" : "247df84cf4a0c2ebc632d08318d00cb3",
                "samplingTime": {
                    "beginPosition": "2012-01-01T13:00:00+01:00",
                    "endPosition": "2012-01-01T17:00:00+01:00"
                },
                "observedProperty": {
                    "CompositePhenomenon": {
                        "id": "comp_126",
                        "dimension": "2"
                    },
                    "component": [
                        "urn:ogc:def:parameter:x-istsos:1.01.0:time:iso8601",
                        "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"
                    ]
                },
                "featureOfInterest": {
                    "geom": (
                        "<gml:Point srsName='EPSG:21781'>"
                        "<gml:coordinates>717900,98520,342</gml:coordinates>"
                        "</gml:Point>"),
                    "name": "urn:ogc:object:feature:x-istsos:1.01.0:"
                            "station:Trevano"
                },
                "result": {
                    "DataArray": {
                        "elementCount": "2",
                        "values": [
                            [
                                "22012-01-01T14:00:00+01:00",
                                "10.000000"
                            ],
                            [
                                "2012-01-01T15:00:00+01:00",
                                "20.000000"
                            ]
                        ],
                        "field": [
                            {
                                "definition": "urn:ogc:def:parameter:x-istsos:"
                                              "1.01.0:time:iso8601",
                                "name": "Time"
                            },
                            {
                                "definition": "urn:ogc:def:parameter:x-istsos:"
                                              "1.0:meteo:air:rainfall",
                                "name": "air-rainfall",
                                "uom": "mm"
                            }
                        ]
                    }
                }
            }
        }
        """
        ns = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'sml': 'http://www.opengis.net/sensorML',
            'swe': 'http://www.opengis.net/swe',
            'xlink': 'http://www.w3.org/1999/xlink',
            'gml': 'http://www.opengis.net/gml',
            'sos': 'http://www.opengis.net/sos/1.0',
            'sa': 'http://www.opengis.net/sampling/1.0',
            'ogc': 'http://www.opengis.net/ogc',
            'om': 'http://www.opengis.net/om/1.0'
        }

        # map namespaces
        try:
            register_namespace = et.register_namespace
            for key in ns:
                register_namespace(key, ns[key])

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
                        traceback.print_exc(file=sys.stderr)

                for key in ns:
                    _namespace_map[ns[key]] = key

        #create xml request
        root = et.Element("{%s}InsertObservation" % ns['sos'])
        root.attrib["{%s}schemaLocation" % ns['xsi']] = (
            "http://schemas.opengis.net/sos/1.0.0/sosAll.xsd")
        root.attrib["version"] = "1.0.0"
        root.attrib["service"] = "SOS"

        AssignedSensorId = et.SubElement(
            root, "{%s}AssignedSensorId" % ns['sos'])
        AssignedSensorId.text = self.json["AssignedSensorId"]

        if "ForceInsert" in self.json:
            ForceInsert = et.SubElement(root, "{%s}ForceInsert" % ns['sos'])
            ForceInsert.text = self.json["ForceInsert"]

        Observation = et.SubElement(root, "{%s}Observation" % ns['om'])

        procedure = et.SubElement(Observation, "{%s}procedure" % ns['om'])
        procedure.attrib["{%s}href" % ns['xlink']] = (
            self.json["Observation"]["procedure"])

        samplingTime = et.SubElement(
            Observation, "{%s}samplingTime" % ns['om'])
        TimePeriod = et.SubElement(
            samplingTime, "{%s}TimePeriod" % ns['gml'])
        beginPosition = et.SubElement(
            TimePeriod, "{%s}beginPosition" % ns['gml'])
        beginPosition.text = (
            self.json["Observation"]["samplingTime"]["beginPosition"])
        endPosition = et.SubElement(
            TimePeriod, "{%s}endPosition" % ns['gml'])
        endPosition.text = (
            self.json["Observation"]["samplingTime"]["endPosition"])

        observedProperty = et.SubElement(
            Observation, "{%s}observedProperty" % ns['om'])
        CompositePhenomenon = et.SubElement(
            observedProperty, "{%s}CompositePhenomenon" % ns['swe'])
        CompositePhenomenon.attrib["dimension"] = (
            self.json["Observation"]["observedProperty"]
            )["CompositePhenomenon"]["dimension"]

        for comp in self.json["Observation"]["observedProperty"]["component"]:
            component = et.SubElement(
                CompositePhenomenon, "{%s}component" % ns['swe'])
            component.attrib["{%s}href" % ns['xlink']] = comp

        featureOfInterest = et.SubElement(
            Observation, "{%s}featureOfInterest" % ns['om'])
        featureOfInterest.attrib["{%s}href" % ns['xlink']] = (
            self.json["Observation"]["featureOfInterest"]["name"])

        result = et.SubElement(Observation, "{%s}result" % ns['om'])
        DataArray = et.SubElement(result, "{%s}DataArray" % ns['swe'])
        elementCount = et.SubElement(DataArray, "{%s}elementCount" % ns['swe'])
        value = et.SubElement(elementCount, "{%s}value" % ns['swe'])
        value.text = (
            self.json["Observation"]["result"]["DataArray"]["elementCount"])
        elementType = et.SubElement(DataArray, "{%s}elementType" % ns['swe'])
        elementType.attrib["name"] = "SimpleDataArray"
        DataRecord = et.SubElement(elementType, "{%s}DataRecord" % ns['swe'])
        DataRecord.attrib["definition"] = (
            "urn:ogc:def:dataType:x-istsos:1.0:timeSeries")
        for index, item in enumerate(
                self.json["Observation"]["result"]["DataArray"]["field"]):
            field = et.SubElement(DataRecord, "{%s}field" % ns['swe'])
            field.attrib["name"] = item["name"]
            if index == 0:
                Time = et.SubElement(field, "{%s}Time" % ns['swe'])
                Time.attrib["definition"] = item["definition"]
                if not item["definition"].find("time") > 0:
                    raise Exception("first element of DataRecord is not of "
                                    "type time")
            else:
                Quantity = et.SubElement(field, "{%s}Quantity" % ns['swe'])
                Quantity.attrib["definition"] = item["definition"]
                if "uom" in item:
                    uom = et.SubElement(Quantity, "{%s}uom" % ns['swe'])
                    uom.attrib["code"] = item["uom"]

        encoding = et.SubElement(DataArray, "{%s}encoding" % ns['swe'])
        TextBlock = et.SubElement(encoding, "{%s}TextBlock" % ns['swe'])
        TextBlock.attrib["tokenSeparator"] = ","
        TextBlock.attrib["blockSeparator"] = "@"
        TextBlock.attrib["decimalSeparator"] = "."

        values = et.SubElement(DataArray, "{%s}values" % ns['swe'])
        values.text = "@".join([",".join(row) for row in (
            self.json["Observation"]["result"]["DataArray"]["values"])])

        # PrettyPrint XML
        iostring = et.tostring(root, encoding="UTF-8")

        headers = {"Content-type": "text/xml"}
        if 'HTTP_AUTHORIZATION' in self.waEnviron:
            headers['Authorization'] = self.waEnviron['HTTP_AUTHORIZATION']

        response = requests.post(
            self.serviceconf.serviceurl["url"],
            data=iostring,
            headers=headers
        )
        data = response.text

        try:
            response.raise_for_status()
            if data.find("AssignedObservationId") > 0:
                self.setMessage("%s" % data)

            else:
                self.setException(
                    "Insert observations failed - Communication: %s %s - "
                    "Response: %s" % (response.status_code, e, response.text))

        except Exception as e:
            self.setException(
                "Insert observations failed - Communication: %s %s - Response:"
                " %s" % (response.status_code, e, response.text))


class waFastInsert(waResourceService):
    """
        class to handle fast insertion of observation, support only the
        POST method.

        Path example:
        http://localhost/istsos/wa/istsos/services/demo/operations/fastinsert

        Regular Time series example body:
        4759a210178a11e6a91c0800273cbaca;
        2017-03-13T14:40:15+0100;PT10M;
        0.2,18.30,69,4.3@0.4,18.80,73,4.1

        Irregular Time series example body:
        4759a210178a11e6a91c0800273cbaca;
        2017-03-13T14:40:15+0100,0.2,18.30,69,4.3@
        2017-03-13T14:40:15+0100,0.4,18.80,73,4.1

        (without line breaks)

        How exception are handled:
        - Wrong sampling time format: no insert
        - Sampling time before end position or after now: no insert
        - Wrong measure value (not a number): is a no data value

    """

    MODE_IRREGULAR = 1
    MODE_REGULAR = 2

    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron, None, False)
        self.servicename = self.pathinfo[2]
        if not self.pathinfo[-1] == "procedures" and len(self.pathinfo) > 4:
            self.procedurename = self.pathinfo[4]
        else:
            self.procedurename = None

    def executePost(self, db=True):
        if self.procedurename is None:
            raise Exception(
                "POST action without procedure name not allowed")

        now = datetime.now(iso.UTC)
        non_blocking_exceptions = []

        # Create data array
        data = self.waEnviron['wsgi_input'].split(";")

        # Assigned id always in the first position
        assignedid = data[0]

        if len(data) == 4:  # regular time series
            mode = self.MODE_REGULAR

        elif len(data) == 2:  # irregular time series
            mode = self.MODE_IRREGULAR

        else:
            raise Exception(
                "Body content wrongly formatted. Please read the docs.")

        try:
            conn = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port']
            )

            rows = conn.select(
                ("""
                    SELECT
                        procedures.id_prc,
                        proc_obs.id_pro,
                        proc_obs.constr_pro,
                        procedures.stime_prc,
                        procedures.etime_prc,
                        procedures.name_prc
                    FROM
                        %s.procedures,
                        %s.proc_obs
                    WHERE
                        proc_obs.id_prc_fk = procedures.id_prc
                """ % (self.servicename, self.servicename)) + """
                  AND
                    assignedid_prc = %s
                  ORDER BY
                    proc_obs.id_pro ASC;
                """,
                (
                    assignedid,
                )
            )

            if len(rows) == 0:
                raise Exception(
                    "Procedure with aid %s not found." % assignedid)

            id_prc = rows[0][0]
            name_prc = rows[0][5]
            bp = rows[0][3]
            bpu = False
            ep = rows[0][4]
            epu = False

            def check_sampling(sampling):

                # If the end position exists the new measures must be after
                if ep is not None and sampling_time < ep:
                    non_blocking_exceptions.append(
                        "Procedure %s, Sampling time (%s) "
                        "is before the end position (%s)" % (
                            name_prc,
                            sampling_time.isoformat(),
                            ep.isoformat())
                    )
                    return False

                # Check that the sampling time is before now
                if sampling_time > now:
                    non_blocking_exceptions.append(
                        "Procedure %s, Sampling time (%s) "
                        "is in the future (%s)" % (
                            name_prc,
                            sampling_time.isoformat(),
                            now.isoformat())
                    )
                    return False

                return True

            tmp_data = []
            if mode == self.MODE_REGULAR:

                try:
                    start = iso.parse_datetime(data[1])
                except Exception:
                    raise Exception(
                        "Procedure %s, Sampling time (%s) "
                        "wrong format" %
                        name_prc, data[1])

                try:
                    step = iso.parse_duration(data[2])
                except Exception:
                    raise Exception(
                        "Procedure %s, duration (%s) "
                        "wrong format" % (
                            name_prc, data[2]
                        )
                    )

                data = data[3].split("@")
                for idx in range(0, len(data)):

                    sampling_time = start + (step * idx)

                    if not check_sampling(sampling_time):
                        continue

                    tmp_data.append([
                        sampling_time.isoformat()
                    ] + data[idx].split(","))

            elif mode == self.MODE_IRREGULAR:
                data = data[1].split("@")
                for i in range(0, len(data)):
                    data[i] = data[i].split(",")

                    try:
                        try:
                            sampling_time = iso.parse_datetime(data[i][0])
                            if not check_sampling(sampling_time):
                                continue
                        except Exception:
                            raise Exception(
                                "Procedure %s, Sampling time (%s) "
                                "wrong format" % (
                                    name_prc, data[i][0]
                                )
                            )

                        tmp_data.append(data[i])

                    except Exception:
                        non_blocking_exceptions.append(
                            "Procedure %s, Sampling time (%s) "
                            "wrong format" % (
                                name_prc, data[1]
                            )
                        )
                        continue

            data = tmp_data

            op_cnt = len(rows)

            for observation in data:

                id_eti = conn.executeInTransaction(
                    ("""
                        INSERT INTO %s.event_time (id_prc_fk, time_eti)
                    """ % self.servicename) + """
                        VALUES (%s, %s::TIMESTAMPTZ) RETURNING id_eti;
                    """,
                    (
                        id_prc, observation[0]
                    )
                )

                if (bp is None) or (bp == '') or (
                        iso.parse_datetime(observation[0]) < bp):
                    bp = iso.parse_datetime(observation[0])
                    bpu = True

                if (ep is None) or (ep == '') or (
                        iso.parse_datetime(observation[0]) > ep):
                    ep = iso.parse_datetime(observation[0])
                    epu = True

                # check if procedure observations length is ok
                #   (-1 remove datetime from lenght of observations array)
                if op_cnt != (len(observation)-1):
                    non_blocking_exceptions.append(
                        "Procedure %s, Array length missmatch with procedures "
                        "observation number: %s" % (
                            name_prc, observation
                        )
                    )
                    continue

                for idx in range(0, op_cnt):
                    try:
                        conn.executeInTransaction(
                            ("""
                                INSERT INTO %s.measures(
                                    id_eti_fk,
                                    id_qi_fk,
                                    id_pro_fk,
                                    val_msr
                                )
                            """ % self.servicename) + """
                                VALUES (%s, 100, %s, %s);
                            """,
                            (
                                int(id_eti[0][0]),  # id_eti
                                int(rows[idx][1]),  # id_pro
                                float(observation[(idx+1)])
                            )
                        )
                    except Exception as ie:
                        non_blocking_exceptions.append(
                            "Procedure %s, %s" % (
                                name_prc, ie
                            )
                        )

            if bpu:
                conn.executeInTransaction(
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
                conn.executeInTransaction(
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

            conn.commitTransaction()

            # self.setData(ret)
            self.setMessage("Thanks for data")

            if len(non_blocking_exceptions) > 0:
                print >> sys.stderr, str(non_blocking_exceptions)

        except Exception as e:
            print >> sys.stderr, traceback.print_exc()
            #traceback.print_exc(file=sys.stderr)
            conn.rollbackTransaction()
            raise Exception(
                "Error in fast insert (%s): %s" % (type(e), e))
