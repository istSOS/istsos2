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
from istsoslib import sosException

class sosFilter():
    """SOS request base filters

    Intercept the request and extract user inputs preferences

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
    """
    
    def __init__(self, sosRequest, method, requestObject, sosConfig):
        """Init sosFilter class"""
        
        self.request = sosRequest
        if self.request == '':
            raise sosException.SOSException("MissingParameterValue", "request", "Missing 'request' parameter")
            
        self.sosConfig = sosConfig
        if method == "GET":
            
            # OGC 12-006/REQ 5: http://www.opengis.net/spec/SOS/2.0/req/core/gc-version
            if self.request=="getcapabilities":
                if requestObject.has_key("acceptversions"):
                    AcceptVersions = requestObject["acceptversions"].split(",")
                    AcceptVersions.sort()
                    self.version = None
                    
                    for version in AcceptVersions:
                        if version in sosConfig.parameters["version"]:
                            self.version=version
                            break
                        
                    if not self.version:
                        raise sosException.SOSException("VersionNegotiationFailed",None,"Any of the accepted versions are supported by this server")
                        
                else:
                    self.version = sosConfig.parameters["default_version"]
                    
            else:
                
                # OGC 12-006/REQ 2: http://www.opengis.net/spec/SOS/2.0/req/core/request-version
                if requestObject.has_key("version"):
                    self.version = requestObject["version"]
                    if self.version == '':
                        raise sosException.SOSException("MissingParameterValue", "version", "Missing 'version' parameter")
                        
                    if self.version not in sosConfig.parameters["version"]:
                        raise sosException.SOSException("InvalidParameterValue","version","\"version\": %s not supported" %(self.version))
                        
                else:
                    raise sosException.SOSException("MissingParameterValue","version","\"version\" parameter is mandatory")
                    
            # OGC 12-006/REQ 1: http://www.opengis.net/spec/SOS/2.0/req/core/request-service
            if requestObject.has_key("service"):
                self.service = requestObject["service"]
                if self.service == '':
                    raise sosException.SOSException("MissingParameterValue", "service", "Missing 'service' parameter")
                    
                if self.service not in sosConfig.parameters["service"]:
                    raise sosException.SOSException("InvalidParameterValue","service","\"service\": %s not supported" %(self.service))
                    
            else:
                raise sosException.SOSException("MissingParameterValue","service","\"service\" parameter is mandatory")
                
                    
        if method == "POST":
            
            if not type(requestObject)==type(""):     
                       
                # OGC 12-006/REQ 1: http://www.opengis.net/spec/SOS/2.0/req/core/request-service
                if "service" in requestObject.attributes.keys():
                    self.service = str(requestObject.getAttribute("service"))
                    if self.service not in sosConfig.parameters["service"]:
                        raise sosException.SOSException("InvalidParameterValue","service","\"service\": %s not supported" %(self.service))
                        
                else:
                    raise sosException.SOSException("MissingParameterValue","service","\"service\" parameter is mandatory")
                            
                # OGC 12-006/REQ 5: http://www.opengis.net/spec/SOS/2.0/req/core/gc-version
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
                    
                    # OGC 12-006/REQ 2: http://www.opengis.net/spec/SOS/2.0/req/core/request-version
                    if "version" in requestObject.attributes.keys():
                        self.version = str(requestObject.getAttribute("version"))
                        if self.version not in sosConfig.parameters["version"]:
                            raise sosException.SOSException("InvalidParameterValue","version","\"version\": %s not supported" %(self.version))
                            
                    else:
                        self.version = sosConfig.parameters["default_version"]
                        