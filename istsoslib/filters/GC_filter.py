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

from istsoslib.filters import filter as f
from istsoslib import sosException

class sosGCfilter(f.sosFilter):
    """filter object for a GetCapabalities request

    This is an extension of the base filter class (sosFilter) to accept
    GetCapabilities request and add specific parameters

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        sections (list): the requested sections names, if not provided the default value is *["all"]*
    """
    
    def __init__(self,sosRequest,method,requestObject,sosConfig):
        f.sosFilter.__init__(self,sosRequest,method,requestObject,sosConfig)
        
        if method == "GET":
            
            self.sections = None
            
            if requestObject.has_key("section"):
                self.sections = requestObject["section"].lower().split( "," )
                
            if requestObject.has_key("sections"):
                self.sections = requestObject["sections"].lower().split( "," )
                
            if self.sections:                
                for s in self.sections:
                    if self.version == '2.0.0':
                        if s not in sosConfig.parameters["GC_Section_2_0_0"]:
                            err_txt = "Allowed parameter \"section\" values are: " + ",".join(sosConfig.parameters["GC_Section"])
                            raise sosException.SOSException("InvalidParameterValue","section",err_txt)
                        
                    else:
                        if s not in sosConfig.parameters["GC_Section"]:
                            err_txt = "Allowed parameter \"section\" values are: " + ",".join(sosConfig.parameters["GC_Section"])
                            raise sosException.SOSException("InvalidParameterValue","section",err_txt)
                        
            else:
                self.sections=["all"]
                
        if method == "POST":
            
            if requestObject.nodeType == requestObject.ELEMENT_NODE:
                #-------SECTIONS-------------
                self.sections=[]
                sects=requestObject.getElementsByTagName('section')
                
                if len(sects) > 0:
                    for sect in sects:
                        for val in sect.childNodes:
                            if val.nodeType == val.TEXT_NODE and str(val.data).lower() in sosConfig.parameters["GC_Section"]:
                                self.sections.append(str(val.data).lower())
                            else:
                                err_txt = "Allowed parameter \"section\" values are: " + ",".join(sosConfig.parameters["GC_Section"])
                                raise sosException.SOSException("InvalidParameterValue","sections",err_txt)
                                
                else:
                    self.sections = ["all"]
            





