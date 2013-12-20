# -*- coding: utf-8 -*-
# istsos Istituto Scienze della Terra Sensor Observation Service
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

#import sosConfig
from istsoslib import sosException

class sosFilter():
    "SOS request filters, set request, service and version"
    #self.request = None
    #self.service = None
    #self.version = None
    def __init__(self,sosRequest,method,requestObject,sosConfig):
        #--------REQUEST-----------
        self.request = sosRequest
        self.sosConfig = sosConfig
        #*****************
        if method == "GET":
            #--------SERVICE------------
            if requestObject.has_key("service"):
                self.service = requestObject["service"]
                if self.service not in sosConfig.parameters["service"]:
                    raise sosException.SOSException("InvalidParameterValue","service","\"service\": %s not supported" %(self.service))
            else:
                raise sosException.SOSException("MissingParameterValue","service","\"service\" parameter is mandatory")
            #---------VERSION NEGOTIATION -----------
            if self.request=="getcapabilities":
                if requestObject.has_key("AcceptVersions"):
                    AcceptVersions = requestObject["AcceptVersions"].split(",")
                    AcceptVersions.sort()
                    self.version = None
                    for version in AcceptVersions:
                        if version in sosConfig.parameters["version"]:
                            self.version=version
                            break
                    if not self.version:
                        raise sosException.SOSException("VersionNegotiationFailed",None,"Any of the accepted versions are supported by this server")
                else:
                    self.version = sosConfig.parameters["version"][0]
            else:
                #---------VERSION-----------
                if requestObject.has_key("version"):
                    self.version = requestObject["version"]
                    if self.version not in sosConfig.parameters["version"]:
                        raise sosException.SOSException("InvalidParameterValue","version","\"version\": %s not supported" %(self.version))
                else:
                    raise sosException.SOSException("MissingParameterValue","version","\"version\" parameter is mandatory")
        #********************
        if method == "POST":
            from xml.dom import minidom
            if not type(requestObject)==type("pp"):                            
                #--------SERVICE------------
                if "service" in requestObject.attributes.keys():
                    self.service = str(requestObject.getAttribute("service"))
                    if self.service not in sosConfig.parameters["service"]:
                        raise sosException.SOSException("InvalidParameterValue","service","\"service\": %s not supported" %(self.service))
                else:
                    raise sosException.SOSException("MissingParameterValue","service","\"service\" parameter is mandatory")
                #---------VERSION NEGOTIATION -----------                        
                if self.request=="getcapabilities":
                    AcceptVersions = requestObject.getElementsByTagName('AcceptVersions')
                    if len(AcceptVersions)>1:
                        raise sosException.SOSException("InvalidParameterValue","AcceptVersions","AcceptVersions multiplicity is 1" %(self.version))
                    elif len(AcceptVersions)==1:
                        VersionsObj = requestObject.getElementsByTagName('Version')
                        versions = [ str(val.firstChild.data) for val in VersionsObj]
                        versions.sort()
                        self.version = None
                        for version in versions:
                            if version in sosConfig.parameters["version"]:
                                self.version=version
                                break
                        if not self.version:
                            raise sosException.SOSException("VersionNegotiationFailed",None,"Any of the accepted versions are supported by this server")
                    else:
                        self.version = sosConfig.parameters["version"][0]
                else:
                    #---------VERSION-----------
                    if "version" in requestObject.attributes.keys():
                        self.version = str(requestObject.getAttribute("version"))
                        if self.version not in sosConfig.parameters["version"]:
                            raise sosException.SOSException("InvalidParameterValue","version","\"version\": %s not supported" %(self.version))
                    else:
                        self.version = sosConfig.parameters["version"][0]

            
