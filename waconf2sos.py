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

from walib import resource
import walib.users as user
import config


class istsosConfig():
    def __init__(self, environ):
        waEnviron = {
            "path": environ['PATH_INFO'],
            "method": str(environ['REQUEST_METHOD']).upper(),
            "pathinfo": environ['PATH_INFO'].strip()[1:].split("/"),
            "url_scheme": environ['wsgi.url_scheme'],
            "http_host": environ['HTTP_HOST'] if (
                environ.get('HTTP_HOST')) else None,
            "server_name": environ['SERVER_NAME'],
            "server_port": environ['SERVER_PORT'],
            "script_name": environ['SCRIPT_NAME'] if (
                environ.get('SCRIPT_NAME', '')) else None,
            "query_string": environ['QUERY_STRING'] if (
                environ.get('QUERY_STRING')) else None,
            "services_path": config.services_path,
            "istsos_path": config.istsoslib_path
        }

        self.user = user.getUser(environ)
        serviceobj = resource.waResourceService(
            waEnviron, waEnviron["pathinfo"][-1], loadjson=False)

        # Passing the basic authentication header in waEnviron
        #   shall be used in istSOS lib request from walib
        if 'HTTP_AUTHORIZATION' in environ:
            waEnviron['HTTP_AUTHORIZATION'] = environ['HTTP_AUTHORIZATION']

        self.debug = config.debug

        self.istsos_librarypath = serviceobj.waconf.paths["istsos"]

        self.connection = {
            "user": serviceobj.serviceconf.connection["user"],
            "password": serviceobj.serviceconf.connection["password"],
            "host": serviceobj.serviceconf.connection["host"],
            "dbname": serviceobj.serviceconf.connection["dbname"],
            "port": serviceobj.serviceconf.connection["port"],
        }

        self.schema = serviceobj.service
        self.authority = serviceobj.serviceconf.identification["authority"]
        self.urnversion = serviceobj.serviceconf.identification["urnversion"]
        self.version = serviceobj.serviceconf.parameters["version"]
        self.default_version = serviceobj.serviceconf.serviceType[
            "default_version"]

        self.istsosepsg = serviceobj.serviceconf.geo["istsosepsg"]
        self.x_axis = serviceobj.serviceconf.geo["xAxisName"]
        self.y_axis = serviceobj.serviceconf.geo["yAxisName"]
        self.z_axis = serviceobj.serviceconf.geo["zAxisName"]
        self.sos_allowedEPSG = [self.istsosepsg] + (
            serviceobj.serviceconf.geo["allowedEPSG"].split(","))

        self.sensorMLpath = serviceobj.sensormlpath
        self.virtual_processes_folder = serviceobj.virtualpath

        self.aggregate_nodata = serviceobj.serviceconf.getobservation[
            "aggregate_nodata"]
        self.maxGoPeriod = serviceobj.serviceconf.getobservation[
            "maxGoPeriod"]
        self.strictogc = serviceobj.serviceconf.getobservation[
            "strictOGC"]
        self.aggregate_nodata_qi = serviceobj.serviceconf.getobservation[
            "aggregate_nodata_qi"]
        self.default_qi = serviceobj.serviceconf.getobservation[
            "default_qi"]
        self.correct_qi = serviceobj.serviceconf.getobservation[
            "correct_qi"]
        self.stat_qi = serviceobj.serviceconf.getobservation[
            "stat_qi"]
        self.transactional_log = serviceobj.serviceconf.getobservation[
            "transactional_log"]

        self.serviceUrl = {
            "get": serviceobj.serviceconf.serviceurl["url"],
            "post": serviceobj.serviceconf.serviceurl["url"]
        }

        self.serviceIdentification = {
            "title": serviceobj.serviceconf.identification[
                "title"],
            "abstract": serviceobj.serviceconf.identification[
                "abstract"],
            "keywords": serviceobj.serviceconf.identification[
                "keywords"].split(","),
            "fees": serviceobj.serviceconf.identification[
                "fees"],
            "accessConstrains": serviceobj.serviceconf.identification[
                "accessConstrains"]
        }

        self.serviceProvider = {
            "providerName": serviceobj.serviceconf.provider["providerName"],
            "providerSite": serviceobj.serviceconf.provider["providerSite"],
            "serviceContact": {
                "individualName": serviceobj.serviceconf.provider[
                    "contactName"],
                "positionName": serviceobj.serviceconf.provider[
                    "contactPosition"],
                "contactInfo": {
                    "voice": serviceobj.serviceconf.provider[
                        "contactVoice"],
                    "fax": serviceobj.serviceconf.provider[
                        "contactFax"],
                    "deliveryPoint": serviceobj.serviceconf.provider[
                        "contactDeliveryPoint"],
                    "city": serviceobj.serviceconf.provider[
                        "contactCity"],
                    "administrativeArea": serviceobj.serviceconf.provider[
                        "contactAdminArea"],
                    "postalCode": serviceobj.serviceconf.provider[
                        "contactPostalCode"],
                    "country": serviceobj.serviceconf.provider[
                        "contactCountry"],
                    "email": serviceobj.serviceconf.provider[
                        "contactEmail"]
                }
            }
        }

        self.urn = {
            "phenomena": serviceobj.serviceconf.urn["phenomena"],
            "dataType": serviceobj.serviceconf.urn["dataType"],
            "parameter": serviceobj.serviceconf.urn["parameter"],
            "process": serviceobj.serviceconf.urn["process"],
            "identifier": serviceobj.serviceconf.urn["identifier"],
            "keywords": serviceobj.serviceconf.urn["keywords"],
            "sensor": serviceobj.serviceconf.urn["sensor"],
            "procedure": serviceobj.serviceconf.urn["procedure"],
            "sensorType": serviceobj.serviceconf.urn["sensorType"],
            "property": serviceobj.serviceconf.urn["property"],
            "feature": serviceobj.serviceconf.urn["feature"],
            "role": serviceobj.serviceconf.urn["role"],
            "offering": serviceobj.serviceconf.urn["offering"],
            "refsystem": serviceobj.serviceconf.urn["refsystem"],
            "time": serviceobj.serviceconf.urn["time"]
        }

        self.parameters = {
            "service": ["SOS"],
            "version": serviceobj.serviceconf.serviceType[
                "version"].split(","),
            "default_version": serviceobj.serviceconf.serviceType[
                "default_version"],
            "requests": serviceobj.serviceconf.parameters[
                "requests"].split(","),
            "GC_Section": serviceobj.serviceconf.parameters[
                "GC_Section"].split(","),
            "GC_Section_2_0_0": serviceobj.serviceconf.parameters[
                "GC_Section_2_0_0"].split(","),
            "DS_outputFormats": serviceobj.serviceconf.parameters[
                "DS_outputFormats"].split(","),
            "DS_outputFormats_2_0_0": serviceobj.serviceconf.parameters[
                "DS_outputFormats_2_0_0"].split(","),
            "GO_srs": self.sos_allowedEPSG,
            "GO_timeFormats": serviceobj.serviceconf.parameters[
                "GO_timeFormats"].split(","),
            "GO_responseFormat": serviceobj.serviceconf.parameters[
                "GO_responseFormat"].split(","),
            "GO_responseFormat_2_0_0": serviceobj.serviceconf.parameters[
                "GO_responseFormat_2_0_0"].split(","),
            "GO_resultModel": serviceobj.serviceconf.parameters[
                "GO_resultModel"].split(","),
            "GO_responseMode": serviceobj.serviceconf.parameters[
                "GO_responseMode"].split(",")
        }

        self.parGeom = {
            "x": serviceobj.serviceconf.parGeom["x"].split(","),
            "y": serviceobj.serviceconf.parGeom["y"].split(","),
            "z": serviceobj.serviceconf.parGeom["z"].split(",")
        }

        self.foiGeometryType = {
            "gml:Point": serviceobj.serviceconf.foiGeometryType["Point"],
            "gml:Polygon": serviceobj.serviceconf.foiGeometryType["Polygon"],
            "gml:Box": serviceobj.serviceconf.foiGeometryType["Box"]
        }

        self.serviceType = {
            "codespace": serviceobj.serviceconf.serviceType["codespace"],
            "value": serviceobj.serviceconf.serviceType["value"],
            "version": serviceobj.serviceconf.serviceType["version"],
        }

        self.mqtt = {
            "broker_url": serviceobj.serviceconf.mqtt["broker_url"],
            "broker_port": serviceobj.serviceconf.mqtt["broker_port"],
            "broker_topic": serviceobj.serviceconf.mqtt["broker_topic"],
            "broker_user": serviceobj.serviceconf.mqtt["broker_user"],
            "broker_password": serviceobj.serviceconf.mqtt["broker_password"]
        }

        self.service = "SOS"
        self.version = "1.0.0"
