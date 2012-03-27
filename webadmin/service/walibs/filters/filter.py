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

import sys, pprint
from walibs.waError import waError
import sosConfig
import simplejson

class waFilter():
    """filter class to handle request types; it verify that the mandatory 
    request, service and version parameetrs are provided"""

    def __init__(self,method,content_type,syslang,charset,request):
        self.method = method
        self.charset = charset
        self.lang = None
        self.req_type = None
        self.req_content_type = content_type
        self.service = None
        self.version = None
        self.request = None
        self.typename = None
        self.outputformat = None
        self.data = None
        self.robj = None
        #-------------------------------#
        if method == "POST":
            #print >> sys.stderr, "TYPE: %s" % repr(content_type)
            if content_type.find("application/json")!=-1 or content_type.find("text/x-json")!=-1:
                self.req_type = "json"
                import json
                try:
                    self.robj = json.loads(request)
                except Exception as e:
                    raise waError.waException(1,lang=syslang,mesg="json")
                
                #control language parameter - OPTIONAL
                if self.robj.has_key("lang"):
                    #check language type is unicode
                    if not isinstance(self.robj["lang"],type(u"")):
                        raise waError.waException(9001,lang=syslang,mesg="lang")
                    #check language value
                    if self.robj["lang"].upper() in waConfig.accepted_lang:
                        self.lang = self.pme_robj["lang"].upper()
                    else:
                        raise waError.waException(9002,lang=syslang,mesg="lang")
                else:
                    #check language value
                    if syslang.upper() in waConfig.accepted_lang:
                        self.lang = syslang.upper()
                    else:
                        self.lang = waConfig.accepted_lang[0].upper()
                       
                #control service parameter - MANDATORY
                if self.robj.has_key("service"):
                    #check service type
                    if not isinstance(self.robj["service"],type(u"")):
                        raise waError.waException(9001,lang=self.lang,mesg="service")
                    #check service value
                    if self.robj["service"].lower() == waConfig.accepted_service:
                        self.service = self.robj["service"] 
                    else:
                        raise waError.waException(9002,lang=self.lang,mesg="service")
                else:
                    raise waError.waException(9003,lang=self.lang,mesg="service")
                
                #control version parameter - MANDATORY
                if self.robj.has_key("version"):
                    #check version type
                    if not isinstance(self.robj["version"],type(u"")):
                        raise waError.waException(9001,lang=self.lang,mesg="version")
                    #check version value
                    if self.robj["version"].lower() in waConfig.accepted_versions:
                        self.version = self.robj["version"] 
                    else:
                        raise waError.waException(9002,lang=self.lang,mesg="version")
                else:
                    raise waError.waException(9003,lang=self.lang,mesg="version")    
                
                #control request parameter - MANDATORY
                if self.robj.has_key("request"):
                    #check request type
                    if not isinstance(self.robj["request"],type(u"")):
                        raise waError.waException(9001,lang=self.lang,mesg="request")
                    #check request value
                    if self.robj["request"].lower() in waConfig.accepted_requests:
                        self.request = self.robj["request"] 
                    else:
                        raise waError.waException(9002,lang=self.lang,mesg="request")
                else:
                    raise waError.waException(9003,lang=self.lang,mesg="request")
               
               
                #control outputFormat parameter - OPTIONAL
                if self.has_key("outputformat"):
                    #check outputformat type
                    if not isinstance(self.robj["outputformat"],type(u"")):
                        raise waError.waException(9001,lang=self.lang,mesg="outputformat")
                    #check outputformat value
                    if self.robj["outputformat"].lower() in waConfig.accepted_outputFormats.keys():
                        self.outputformat = waConfig.accepted_outputFormats[self.pme_robj["outputformat"].lower()]
                    else:
                        raise waError.waException(9002,lang=self.lang,mesg="outputformat")
                else:
                    self.outputformat = waConfig.accepted_outputFormats[waConfig.accepted_outputFormats.keys()[0]]
               
               
                #control request typename
                if self.robj.has_key("typename"):
                    #check typename type
                    if not isinstance(self.robj["typename"],type(u"")):
                        raise waError.waException(9001,lang=self.lang,mesg="typename")
                    #check typename value
                    if self.robj["typename"].lower() in waConfig.accepted_typenames:
                        self.typename = self.robj["typename"] 
                    else:
                        raise waError.waException(9002,lang=self.lang,mesg="typename")
                
                else:
                    raise waError.waException(9003,lang=self.lang,mesg="typename")
                
            #--- if the format of the request is not implemeneted ---    
            else:
                raise waError.waException(9000,lang=self.lang,mesg="request-content-type")
            
        #-------------------------------#    
        elif self.method == "GET":
            raise waError.waException(9000,lang=syslang,mesg=method)
            
        #-------------------------------#    
        else:
            raise waError.waException(9000,lang=syslang,mesg="request-method %s" %(method))
    
    def __str__(self):
        return "method: %s, lang: %s, req_type: %s, service: %s, version: %s, request: %s, typename: %s, robj: %s " % (self.method, self.lang, self.req_type, self.service, 
            self.version, self.request, self.typename, self.pme_robj)


