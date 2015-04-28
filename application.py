# -*- coding: utf-8 -*-
# istsos WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
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

import sys
from os import path
sys.path.insert(0, path.abspath(path.dirname(__file__)))

import pprint
pp = pprint.PrettyPrinter(indent=4)


def application(environ, start_response):
    path = environ['PATH_INFO'].strip()[1:].split("/")
    if path[0] == 'wa':
        return executeWa(environ, start_response)
    elif path[0] == 'wns':
        return executeWns(environ, start_response)
    else:
        return executeSos(environ, start_response)


def executeSos(environ, start_response):
    import sys
    import traceback
    import waconf2sos as cfg
    sosConfig = cfg.istsosConfig(environ)

    if not sosConfig.istsos_librarypath=="" or sosConfig.istsos_librarypath==None:
        sys.path.insert(0, sosConfig.istsos_librarypath)

    from istsoslib import sosDatabase
    from istsoslib import sosException

    try:
        #===============================
        # CALL istsos AND PRODUCE RESPONSE
        #===============================
        # call istsos to manage the request and generate the response
        pgdb = sosDatabase.PgDB(sosConfig.connection["user"],
                           sosConfig.connection["password"],
                           sosConfig.connection["dbname"],
                           sosConfig.connection["host"],
                           sosConfig.connection["port"])


        from istsoslib.filters import factory_filters as FF
        from istsoslib.responders import factory_response as FR
        from istsoslib.renderers import factory_render as FRe

        req_filter = FF.sosFactoryFilter(environ, sosConfig)
        response = FR.sosFactoryResponse(req_filter, pgdb)
        render = FRe.sosFactoryRender(response, sosConfig)
        try:
            content_type = req_filter.responseFormat
        except:
            content_type = 'application/xml; charset=utf-8'

        #===============================
        # SEND RESPONSE
        #===============================
        # HTTP response code and message
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', content_type),
                            ('Content-Length', str(len(render.encode('utf-8'))))]
                            
        #Content-Disposition: attachment; filename="'.basename($file).'"'                    
        if str(environ['REQUEST_METHOD']).upper()=='GET':
            rect = parse_qs(environ['QUERY_STRING'])
            requestObject = {}
            for key in rect.keys():
                requestObject[key.lower()] = rect[key][0]
            if requestObject.has_key("attachment"):
                response_headers.append(("Content-Disposition", "attachment; filename=%s" % requestObject["attachment"]))
                            
        # send response header
        start_response(status, response_headers)
        #send response body
        return [render.encode('utf-8')]

    except sosException.SOSException, e:
        print >> sys.stderr, traceback.print_exc()
        response_body = e.ToXML()
        # HTTP response code and message
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', 'application/xml; charset=utf-8'),
                            ('Content-Length', str(len(response_body.encode('utf-8'))))]
        # send response header
        start_response(status, response_headers)
        # send response
        return [response_body.encode('utf-8')]

    except Exception, e:
        print >> sys.stderr, traceback.print_exc()
        othertext = traceback.format_exception(*sys.exc_info())
        if sosConfig.debug:
            response_body = "%s" % (sosException.SOSException("NoApplicableCode",None,e.__class__.__name__, [e, othertext]),)
        else:
            response_body = "%s" % (sosException.SOSException("NoApplicableCode",None,"istSOS internal error",["Please activate debug level for more details"]))
        # HTTP response code and message
        status = '200 OK'
        # prepare response header
        response_headers = [('Content-Type', 'application/xml; charset=utf-8'),
                            ('Content-Length', str(len(response_body.encode('utf-8'))))]
        # send response header
        start_response(status, response_headers)
        # send response
        return [response_body.encode('utf-8')]

    return


def executeWa(environ, start_response):

    from urlparse import parse_qs
    import config
    import traceback
    from walib import resourceFactory as factory
    import logging, logging.config, logging.handlers

    #----logging--------------------------------------------------------------------------
    formatter = logging.Formatter('%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
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
        logger.setLevel(logging.UNSET)
    #--------------------------------------------------------------------------------------

    #----setting environment variables-----------
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
        "errorlog_path" : config.errorlog_path
    }
    #print >> sys.stderr, "\n\nENVIRON: %s" % pp.pprint(waEnviron)

    try:

        try:
            op = None
            op = factory.initResource(waEnviron)

            try:
                if op.response['success']:

                    method = str(environ['REQUEST_METHOD']).upper()
                    # Data RETRIEVAL
                    if method == "GET":
                        op.executeGet()

                    # Data UPDATE
                    elif method == "POST":
                        op.executePost()

                    # Data INSERT
                    elif method == "PUT":
                        op.executePut()

                    # Data DELETE
                    elif method == "DELETE":
                        op.executeDelete()

                    else:
                        raise Exception("HTTP method %s not supported" % waEnviron["method"])

                    if 'log' in op.response:
                        logger.info("Executing %s on %s: %s" % (waEnviron["method"],
                                            environ['PATH_INFO'],str(op.response['log']) ))

                    if 'message' in op.response:
                        logger.info("Executing %s on %s: %s" % (waEnviron["method"],
                                            environ['PATH_INFO'],str(op.response['message']) ))



            except Exception as exe:
                print >> sys.stderr, traceback.print_exc()
                logger.error("Executing %s on %s: %s" % (waEnviron["method"],
                                 environ['PATH_INFO'],str(exe)))
                #op.setException("Executing %s on %s: %s" % (method, environ['PATH_INFO'], exe))
                op.setException(str(exe))

        except Exception as exe:
            print >> sys.stderr, traceback.print_exc()
            logger.error("On initialization %s on %s: %s" % (waEnviron["method"],
                                 environ['PATH_INFO'],str(exe)))
            from walib import resource
            op = resource.waResource(waEnviron)
            #op.setException("On initialization: %s" % exe)
            op.setException(str(exe))

        try:
            wsgi_response = op.getResponse()
        except Exception as exe:
            print >> sys.stderr, traceback.print_exc()
            logger.error("Executing %s on %s: %s" % (waEnviron["method"],
                                 environ['PATH_INFO'],str(exe)))
            op.setException("Error converting response to json")

        wsgi_mime = "application/json"

    except Exception as e:
        print >> sys.stderr, traceback.print_exc()
        logger.error("Executing %s on %s: %s" % (waEnviron["method"],
                                 environ['PATH_INFO'],str(e)))
        wsgi_response = str(e)
        wsgi_mime = 'text/plain'
        wsgi_status = '400 Bad Request'

    wsgi_headers = [
        ('Content-Type', "%s; charset=utf-8" % wsgi_mime),
        ('Content-Length', str(len(wsgi_response)))
    ]
    start_response(wsgi_status, wsgi_headers)
    return [wsgi_response]


def executeWns(environ, start_response):

    from urlparse import parse_qs
    from wnslib import resourceFactory
    import config

    wsgi_response = "Hello istSOS WNS"
    wsgi_mime = 'text/plain'
    wsgi_status = '200 OK'

    wnsEnviron = {
        "path": environ['PATH_INFO'][3:],
        "method": str(environ['REQUEST_METHOD']).upper(),
        "pathinfo": environ['PATH_INFO'].strip()[4:].split("/"),
        "wsgi_input": environ['wsgi.input'].read(int(environ["CONTENT_LENGTH"])) if environ.get("CONTENT_LENGTH") else None,
        "url_scheme": environ['wsgi.url_scheme'],
        "http_host": environ['HTTP_HOST'] if environ.get('HTTP_HOST') else None,
        "server_name": environ['SERVER_NAME'],
        "server_port": environ['SERVER_PORT'],
        "script_name": environ['SCRIPT_NAME'] if environ.get('SCRIPT_NAME', '') else None,
        "parameters": parse_qs(environ['QUERY_STRING']) if environ.get('QUERY_STRING') else None,
        "services_path": config.services_path,
    }

    method = str(environ['REQUEST_METHOD']).upper()
    op = resourceFactory.initResource(wnsEnviron)

    try:
        if method == "GET":
            op.executeGet()
        elif method == "PUT":
            op.executePut()
        elif method == "POST":
            op.executePost()
        elif method == "DELETE":
            op.executeDelete()
        else:
            raise Exception("HTTP method %s not supported" % method)
        wsgi_response = op.getResponse()
        wsgi_mime = "application/json"

    except Exception as e:
        wsgi_response = str(e)
        wsgi_mime = 'text/plain'
        wsgi_status = '400 Bad Request'

    wsgi_headers = [
        ('Content-Type', "%s; charset=utf-8" % wsgi_mime),
        ('Content-Length', str(len(wsgi_response)))
    ]
    start_response(wsgi_status, wsgi_headers)
    return [wsgi_response]
