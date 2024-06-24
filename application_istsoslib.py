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

import sys
import os
from os import path
import traceback
import waconf2sos
from urllib.parse import parse_qs
import config

sys.path.insert(0, path.abspath(path.dirname(__file__)))

from istsoslib.filters import factory_filters as FF
from istsoslib.responders import factory_response as FR
from istsoslib.renderers import factory_render as FRe


def executeSos(environ, start_response):

    try:
        from istsoslib import sosDatabase
        from istsoslib import sosException

        try:
            sosConfig = waconf2sos.istsosConfig(environ)

        except sosException.SOSException as ise:
            raise ise

        except Exception as ex:
            raise sosException.SOSException(
                "NoApplicableCode", "", str(ex)
            )

        if not sosConfig.istsos_librarypath == "" or (
                sosConfig.istsos_librarypath is None):
            sys.path.insert(0, sosConfig.istsos_librarypath)

        pgdb = sosDatabase.PgDB(
            os.environ["GROUNDWATER_DATABASE_USER"],
            os.environ["GROUNDWATER_DATABASE_PASSWORD"],
            os.environ["GROUNDWATER_DATABASE"],
            os.environ["GROUNDWATER_DATABASE_HOST"],
            os.environ["GROUNDWATER_DATABASE_PORT"]
        )

        req_filter = FF.sosFactoryFilter(environ, sosConfig)

        # Checking authorizations
        if not sosConfig.user.allowedService(sosConfig.schema):
            raise sosException.SOSException(
                "NoApplicableCode", "",
                "You are not authorized to access the "
                "'%s' instance" % sosConfig.schema)

        elif req_filter.request in ['insertobservation', 'registersensor']:
            # If hybrid mode enable check authorizations
            if config.hybrid and (not 'HTTP_AUTHORIZATION' in environ):
                raise sosException.SOSException(
                    "NoApplicableCode", "",
                    "In hybrid mode, you are not authorized to "
                    "execute %s requests on this server" % req_filter.request)

            # Only Admin, Network Managers and Data Manager con execute
            # insertobservation or registersensor
            elif not sosConfig.user.isAdmin() and (
                    not sosConfig.user.isNetworkManager()) and (
                    not sosConfig.user.isDataManager()):
                raise sosException.SOSException(
                    "NoApplicableCode", "",
                    "You are not authorized to execute %s "
                    "requests on this server" % req_filter.request)

        response = FR.sosFactoryResponse(req_filter, pgdb)
        render = FRe.sosFactoryRender(response, sosConfig)

        try:
            content_type = req_filter.responseFormat

        except:
            content_type = 'application/xml; charset=utf-8'

        status = '200 OK'
        response_headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(render)))
        ]

        if str(environ['REQUEST_METHOD']).upper() == 'GET':
            rect = parse_qs(environ['QUERY_STRING'])
            requestObject = {}
            for key in list(rect.keys()):
                requestObject[key.lower()] = rect[key][0]
            if "attachment" in requestObject:
                response_headers.append(
                    ("Content-Disposition",
                     "attachment; filename=%s" % requestObject["attachment"])
                )

        start_response(status, response_headers)
        return [render]

    except sosException.SOSException as e:
        print(traceback.print_exc(), file=sys.stderr)
        response_body = e.ToXML()
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'application/xml; charset=utf-8'),
            ('Content-Length', str(len(response_body.encode('utf-8'))))
        ]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]

    except Exception as e:
        print(traceback.print_exc(), file=sys.stderr)
        othertext = traceback.format_exception(*sys.exc_info())
        if sosConfig.debug:
            response_body = "%s" % (
                sosException.SOSException(
                    "NoApplicableCode",
                    None,
                    e.__class__.__name__, [e, othertext]),)
        else:
            response_body = "%s" % (
                sosException.SOSException(
                    "NoApplicableCode",
                    None,
                    "istSOS internal error",
                    ["Please activate debug level for more details"]
                )
            )
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'application/xml; charset=utf-8'),
            ('Content-Length', str(len(response_body.encode('utf-8'))))
        ]
        start_response(status, response_headers)
        return [response_body.encode('utf-8')]

    return []
