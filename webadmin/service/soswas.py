# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2011 Massimiliano Cannata, Milan Antonovic
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

#from mod_python import util, apache, psp
import urllib
import cStringIO
import traceback
import decimal

#import pmeDatabase
from cgi import parse_qs, escape

sys.path.append(path.abspath(path.dirname(__file__)))
from walibs import language

sys.path.append(path.abspath(wac.sosConfigPath))
import sosConfig

import waConfig, waDatabase

#from walibs.pmeError import pme_error, pmeRendererError
#from walibs.filters import pmeFactoryFilter
#from walibs.responders import pmeFactoryResponder
#from pmelibs.renderers import pmeFactoryRenderer

import waConfig
import pprint, traceback

def application(environ, start_response):
    #root_path = path.abspath(path.dirname(__file__))
    #sys.path.append(root_path)

    exception = (0,"")
    
    #===============================
    # READ REQUEST
    #===============================
    # read the request method and, content-type, language and request
    method = str(environ['REQUEST_METHOD']).upper()
    content_type = environ.get('CONTENT_TYPE', '')
    syslang = language.preferred_language(environ.get("HTTP_ACCEPT_LANGUAGE", "en"))
    charset = language.preferred_encoding(environ.get("HTTP_ACCEPT_CHARSET", "UTF-8"))
    environ['wsgi.charset'] = 'utf-8'
    encode = ""
    request = None    
    
    try:   
        
        #===============================
        # MANAGE REQUEST PATH
        #===============================
        if environ['PATH_INFO']=="/upload":
            #-----            
        
        elif method=="GET":
            request_str = parse_qs(environ['QUERY_STRING'])
            request = {}
            for key in request_str.keys():
                request[key] = request_str[key][0]
        
        
        elif method=="POST":
            #=============================================
            # Request body extraction from environ object
            #=============================================
            request = environ['wsgi.input'].read(-1) 
            
            pgdb=waDatabase.PgDB(   waConfig.connection['user'],
                                    waConfig.connection['password'],
                                    waConfig.connection['dbname'],
                                    waConfig.connection['host'],
                                    waConfig.connection['port']
                                )
            
    
        
        wsgi_response = response.encode('utf-8')
        wsgi_mime = response.mime
    
    except Exception as e:
        #===============================
        # SET RESPONSE CONTENT & TYPE
        #===============================
        print >> sys.stderr, traceback.print_exc()
        wsgi_response = pmeRendererError.renderError(e).decode('utf-8')
        wsgi_mime = content_type
        print >> sys.stderr, str(e)
    
    #===============================
    # SEND RESPONSE
    #===============================
    # HTTP response code and message
    status = '200 OK'
    # prepare response header
    wsgi_headers = [('Content-Type', wsgi_mime),
                        ('Content-Length', str(len(wsgi_response)))]
    # send response header
    start_response(status, wsgi_headers)
    #send response body
    return [wsgi_response]
    
    
