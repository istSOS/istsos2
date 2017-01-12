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

import sys
from os import path
import traceback
import waconf2sos as cfg
from urlparse import parse_qs
import config
from walib import resourceFactory as factory
import walib.users as user
import logging, logging.config, logging.handlers

def executeWa(environ, start_response):

    # Initializing logging
    '''formatter = logging.Formatter('%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
    log_filename = path.join(config.errorlog_path,"wa.log")
    handler = logging.handlers.RotatingFileHandler(filename=log_filename, maxBytes = 1024*1024, backupCount = 20)
    handler.setFormatter(formatter)
    logger = logging.getLogger('istsos')

    if len(logger.handlers)==0:
        logger.addHandler(handler)

    elif len(logger.handlers)==1 and type(logger.handlers[0])==type(handler):
        pass

    else:
        for h in logger.handlers:
            logger.removeHandler(h)

        logger.addHandler(handler)

    if config.errorlog_level == "INFO":
        logger.setLevel(logging.INFO)

    elif config.errorlog_level == "ERROR":
        logger.setLevel(logging.ERROR)

    else:
        logger.setLevel(logging.UNSET)'''

    # Setting environment variables
    wsgi_response = "Hello istSOS"
    wsgi_mime = 'text/plain'
    wsgi_status = '200 OK'

    waEnviron = {
        "path" : environ['PATH_INFO'][3:],
        "method" : str(environ['REQUEST_METHOD']).upper(),
        "pathinfo" : environ['PATH_INFO'].strip()[4:].split("/"),
        "wsgi_input" : environ['wsgi.input'].read(int(environ["CONTENT_LENGTH"])) if environ.get("CONTENT_LENGTH") else None,
        "url_scheme" : environ['wsgi.url_scheme'],
        "http_host" : environ['HTTP_HOST'] if environ.get('HTTP_HOST') else None,
        "server_name" : environ['SERVER_NAME'],
        "server_port" : environ['SERVER_PORT'],
        "script_name" : environ['SCRIPT_NAME'] if environ.get('SCRIPT_NAME', '') else None,
        "query_string" : environ['QUERY_STRING'] if environ.get('QUERY_STRING') else None,
        "parameters": parse_qs(environ['QUERY_STRING']) if environ.get('QUERY_STRING') else None,
        "services_path" : config.services_path,
        "istsos_path" : config.istsoslib_path,
        "errorlog_path" : config.errorlog_path,
        "user": user.getUser(environ)
    }

    # Passing the basic authentication header in waEnviron
    #   Shall be used in istSOS lib request from walib
    if 'HTTP_AUTHORIZATION' in environ:
        waEnviron['HTTP_AUTHORIZATION'] = environ['HTTP_AUTHORIZATION']

    try:

        try:
            op = None
            op = factory.initResource(waEnviron)

            try:
                if op.response['success']:
                    method = str(environ['REQUEST_METHOD']).upper()

                    if method == "GET": # Data RETRIEVAL
                        op.executeGet()

                    elif method == "POST": # Data UPDATE
                        op.executePost()

                    elif method == "PUT": # Data INSERT
                        op.executePut()

                    elif method == "DELETE": # Data DELETE
                        op.executeDelete()

                    else:
                        raise Exception("HTTP method %s not supported" % waEnviron["method"])

                    '''if 'log' in op.response:
                        logger.info(
                            "Executing %s on %s: %s" % (
                                waEnviron["method"],
                                environ['PATH_INFO'], str(op.response['log'])
                            )
                        )

                    if 'message' in op.response:
                        logger.info(
                            "Executing %s on %s: %s" % (
                                waEnviron["method"],
                                environ['PATH_INFO'], str(op.response['message'])
                            )
                        )'''

            except Exception as exe:
                print >> sys.stderr, traceback.print_exc()
                '''logger.error(
                    "Executing %s on %s: %s" % (
                        waEnviron["method"],
                        environ['PATH_INFO'], str(exe)
                    )
                )'''
                op.setException(str(exe))

        except Exception as exe:
            print >> sys.stderr, traceback.print_exc()
            '''logger.error(
                "On initialization %s on %s: %s" % (
                    waEnviron["method"],
                    environ['PATH_INFO'], str(exe)
                )
            )'''
            from walib import resource
            op = resource.waResource(waEnviron)
            op.setException(str(exe))

        wsgi_mime = "application/json"

        try:
            wsgi_response = op.getResponse()
            wsgi_mime = op.getMime()

        except Exception as exe:
            print >> sys.stderr, traceback.print_exc()
            '''logger.error(
                "Executing %s on %s: %s" % (
                    waEnviron["method"],
                    environ['PATH_INFO'], str(exe)
                )
            )'''
            op.setException("Error converting response to json")

    except Exception as e:
        print >> sys.stderr, traceback.print_exc()
        '''logger.error(
            "Executing %s on %s: %s" % (
                waEnviron["method"],
                environ['PATH_INFO'], str(e)
            )
        )'''
        wsgi_response = str(e)
        wsgi_mime = 'text/plain'
        wsgi_status = '400 Bad Request'

    wsgi_headers = [
        ('Content-Type', "%s; charset=utf-8" % wsgi_mime),
        ('Content-Length', str(len(wsgi_response)))
    ]
    start_response(wsgi_status, wsgi_headers)
    return [wsgi_response]
