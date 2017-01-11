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
sys.path.insert(0, path.abspath(path.dirname(__file__)))
import application_istsoslib
import application_walib
import application_wnslib    

def application(environ, start_response):

    path = environ['PATH_INFO'].strip()[1:].split("/")    
    
    if path[0] == 'wa':
        return application_walib.executeWa(environ, start_response)
        
    elif path[0] == 'wns':
        return application_wnslib.executeWns(environ, start_response)
        
    elif path[0] != '':
        return application_istsoslib.executeSos(environ, start_response)
        
    else:
        start_response('309 Redirect', [('Location','admin/')])
        return []



