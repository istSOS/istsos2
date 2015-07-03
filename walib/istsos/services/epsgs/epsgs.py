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
from walib import resource, utils, databaseManager, configManager
from walib.resource import waResourceService
import sys, os
from lib import isodate

class waEpsgs(waResourceService):
    """class to handle SOS service objects, support GET and POST method"""
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        
    def executeGet(self):
        """
        Method for executing a GET requests that return a list of valid EPSG codes
                          
        """
        data = [{
            "name": self.serviceconf.geo["istsosepsg"]
        }]
        for epsg in self.serviceconf.geo["allowedEPSG"].split(","):
            data.append({
                "name": epsg
            })
        
        #self.setData( [ self.serviceconf.geo["istsosepsg"] ] + self.serviceconf.geo["allowedEPSG"].split(",") )
        self.setData(data)
        self.setMessage("List of valid EPSG codes of service <%s> successfully retrived" % self.service)
        
        
        
        
        
