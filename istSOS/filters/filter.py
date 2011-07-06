# istSOS Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
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

import sosConfig
from istSOS import sosException

class sosFilter():
    "SOS request filters, set request, service and version"
    #self.request = None
    #self.service = None
    #self.version = None
    def __init__(self,sosRequest,method,requestObject):
        #--------REQUEST-----------
        self.request = sosRequest
        #*****************
        if method == "GET":
            #--------SERVICE------------
            if requestObject.has_key("service"):
                self.service = requestObject["service"]
                if self.service not in sosConfig.parameters["service"]:
                    raise sosException.SOSException(1,"\"service\": %s not supported" %(self.service))
            else:
                self.service = sosConfig.parameters["service"][0]
            #---------VERSION-----------
            if requestObject.has_key("version"):
                self.version = requestObject["version"]
                if self.version not in sosConfig.parameters["version"]:
                    raise sosException.SOSException(1,"\"version\": %s not supported" %(self.version))
            else:
                self.version = sosConfig.parameters["version"][0]
        #********************
        if method == "POST":
            from xml.dom import minidom
            #--------SERVICE------------
            if "service" in requestObject.attributes.keys():
                self.service = str(requestObject.getAttribute("service"))
                if self.service not in sosConfig.parameters["service"]:
                    raise sosException.SOSException(1,"\"service\": %s not supported" %(self.service))
            else:
                self.service = sosConfig.parameters["service"][0]
            #---------VERSION-----------
            if "version" in requestObject.attributes.keys():
                self.version = str(requestObject.getAttribute("version"))
                if self.version not in sosConfig.parameters["version"]:
                    raise sosException.SOSException(1,"\"version\": %s not supported" %(self.version))
            else:
                self.version = sosConfig.parameters["version"][0]


            
