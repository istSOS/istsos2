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
from walib.resource import waResourceConfigurator, waResourceService
import sys

class waUrn(waResourceConfigurator):
    template = {
        "property" : ["urn","property"],
        "offering" : ["urn","offering"],
        "sensor" : ["urn","sensor"],
        "phenomena" : ["urn","phenomena"],
        "feature" : ["urn","feature"],
        "sensorType" : ["urn","sensorType"],
        "process" : ["urn","process"],
        "role" : ["urn","role"],
        "refsystem" : ["urn","refsystem"],
        "dataType" : ["urn","dataType"],
        "time" : ["urn","time"],
        "keywords" : ["urn","keywords"],
        "identifier" : ["urn","identifier"],
        "parameter" : ["urn","parameter"],
        "procedure" : ["urn","procedure"]
    }
    
    def executeGet(self):
        """
        Execute operation GET for on service configuration sections
        """
        data = {
            'default': True
        }
        identification = self.serviceconf.get("identification")
        authority = identification["authority"]
        urnversion = identification["urnversion"]
        for key in self.template:
            temp = self.serviceconf.get(self.template[key][0])
            
            if not temp.has_key(self.template[key][1]):
                raise Exception("Configuration error: value \"%s\" not present in section \"%s\", check your template settings!" % (self.template[key][1],self.template[key][0]))
            
            #---SUBSTITUTED---------------------------------------------------
            #data[key] = temp[self.template[key][1]].replace(
            #                                "@identification-authority@",authority
            #                                ).replace("@urnversion@",urnversion)
            #---BY------------------------------------------------------------------
            data[key] = temp[self.template[key][1]]
            #-----------------------------------------------------------------------            
        for s in self.sections:
            data['default'] = data['default'] and self.serviceconf.get(s)["default"]
        self.setData(data)
        self.setMessage("Information successfully retrived")
        return data

    def executePost(self):
        raise Exception("%s.executePost method is not implemented!" % self.__class__.__name__)
        
    def executePut(self):
        raise Exception("%s.executePut method is not implemented!" % self.__class__.__name__)
        
    def executeDelete(self):
        raise Exception("%s.executeDelete method is not implemented!" % self.__class__.__name__)
        
    
    
    
    
