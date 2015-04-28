#  -*- coding: utf-8 -*-
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
import application as app
pp = pprint.PrettyPrinter(indent=4)

def application(environ, start_response):
    path = environ['PATH_INFO'].strip()[1:].split("/")
    if path[0]=='wa':
        return executeWa(environ, start_response)
    elif path[0] == 'wns':
        return executeWns(environ, start_response)
    else:
        return executeSos(environ, start_response)
    '''
    else:
        response_body = "istSOS requests not supported for read only users"
        start_response('404 Not Found', 
            [
                ('Content-Type', 'text/plain; charset=utf-8'),
                ('Content-Length', str(len(response_body)))
            ]
        )
        return [response_body.encode('utf-8')]'''


def executeSos(environ, start_response):
    
    method = str(environ['REQUEST_METHOD']).upper()
    # Data RETRIEVAL
    if method != "GET":
        response_body = '{"success": false, "message": "HTTP method %s not supported", "method": "%s"}' % (method,method)
        start_response('200 OK', 
            [
                ('Content-Type', 'application/json; charset=utf-8'),
                ('Content-Length', str(len(response_body)))
            ]
        )
        return [response_body.encode('utf-8')]
    else:
        return app.executeSos(environ, start_response)

def executeWa(environ, start_response):
    
    method = str(environ['REQUEST_METHOD']).upper()
    # Data RETRIEVAL
    if method != "GET":
        response_body = '{"success": false, "message": "HTTP method %s not supported", "method": "%s"}' % (method,method)
        start_response('200 OK', 
            [
                ('Content-Type', 'application/json; charset=utf-8'),
                ('Content-Length', str(len(response_body)))
            ]
        )
        return [response_body.encode('utf-8')]
    else:
        return app.executeWa(environ, start_response)
        

def executeWns(environ, start_response):
    
    method = str(environ['REQUEST_METHOD']).upper()
    # Data RETRIEVAL
    if method != "GET":
        response_body = '{"success": false, "message": "HTTP method %s not supported", "method": "%s"}' % (method,method)
        start_response('200 OK', 
            [
                ('Content-Type', 'application/json; charset=utf-8'),
                ('Content-Length', str(len(response_body)))
            ]
        )
        return [response_body.encode('utf-8')]
    else:
        return app.executeWns(environ, start_response)
        

