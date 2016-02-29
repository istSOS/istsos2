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

def get_fake_ds(procedure, sosConfig):
    return sosDSfilter("describesensor", "GET", {
        "service": "SOS",
        "version": "1.0.0",
        "outputformat": sosConfig.parameters["DS_outputFormats"][0],
        "procedure": procedure
    }, sosConfig)

class sosDSfilter(f.sosFilter):
    """
    filter object for a DescribeSensor request

    This is an extension of the base filter class (sosFilter) to accept
    DescribeSensor request and add specific parameters

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        outputFormat (str): the outputFormat
        procedure (str): the name of the procedure to be described
    """
    def __init__(self, sosRequest, method, requestObject, sosConfig):
        f.sosFilter.__init__(self, sosRequest, method, requestObject, sosConfig)
        
        if method == "GET":
            self.outputFormat = None
            self.procedure = None
            
            if self.version == '2.0.0':
                # OUTPUTFORMAT
                if requestObject.has_key("proceduredescriptionformat"):
                    if requestObject["proceduredescriptionformat"] == '':
                        raise sosException.SOSException("MissingParameterValue", "proceduredescriptionformat", "Missing 'proceduredescriptionformat' parameter")
                        
                    if requestObject["proceduredescriptionformat"] in sosConfig.parameters["DS_outputFormats_2_0_0"]:
                        self.outputFormat = requestObject["proceduredescriptionformat"]
                        
                    else:
                        raise sosException.SOSException(
                            "InvalidParameterValue",
                            "procedureDescriptionFormat",
                            "Supported \"procedureDescriptionFormat\" values are: " + ",".join(sosConfig.parameters["DS_outputFormats_2_0_0"]))
                        
                else:
                    raise sosException.SOSException("MissingParameterValue","procedureDescriptionFormat","Parameter \"procedureDescriptionFormat\" is mandatory")
            
            else:
                # OUTPUTFORMAT
                if requestObject.has_key("outputformat"):
                    if requestObject["outputformat"] in sosConfig.parameters["DS_outputFormats"]:
                        self.outputFormat = requestObject["outputformat"]
                        
                    else:
                        err_txt = "Supported \"outputFormat\" values are: " + ",".join(sosConfig.parameters["DS_outputFormats"])
                        raise sosException.SOSException("InvalidParameterValue","outputFormat",err_txt)
                        
                else:
                    raise sosException.SOSException("MissingParameterValue","outputFormat","Parameter \"outputFormat\" is mandatory")
            
            # PROCEDURES
            if requestObject.has_key("procedure"):
                if requestObject["procedure"] == '':
                    raise sosException.SOSException("MissingParameterValue", "procedure", "Missing 'procedure' parameter")
                    
                prc = requestObject["procedure"].split(":")
                self.procedure = prc[-1]
                if len(prc)>1:
                    prc[-1]=""
                    
                    if ":".join(prc)==sosConfig.urn["procedure"]:
                        pass
                    
                    else:
                        err_txt = "Supported \"procedure\" urn is: " + sosConfig.urn["procedure"]
                        err_txt += "\n passed: " + ":".join(prc)
                        raise sosException.SOSException("InvalidParameterValue","procedure",err_txt)
                        
            else:
                raise sosException.SOSException("MissingParameterValue","procedure","Parameter \"procedure\" is mandatory with multiplicity 1")
        
        if method == "POST":
            self.outputFormat = None
            self.procedure = None
            
            # OUTPUTFORMAT
            if "outputFormat" in requestObject.attributes.keys():
                self.outputFormat = str(requestObject.getAttribute("outputFormat"))
                if self.outputFormat not in sosConfig.parameters["DS_outputFormats"]:
                    err_txt = "Allowed \"outputFormat\" values are: " + ",".join(sosConfig.parameters["DS_outputFormats"])
                    raise sosException.SOSException("InvalidParameterValue","outputFormat",err_txt)
                    
            else:
                err_txt = "Parameter \"outputFormat\" is mandatory"
                raise sosException.SOSException("MissingParameterValue","outputFormat","Parameter \"outputFormat\" is mandatory")
            
            # PROCEDURES
            procs=requestObject.getElementsByTagName('procedure')
            if len(procs) > 0:
                if len(procs) < 2:
                    
                    val = procs[0].firstChild
                    if val.nodeType == val.TEXT_NODE:
                        """
                        self.procedure = str(val.data)
                        """
                        prc = str(val.data).split(":")
                        if len(prc)>1:
                            if prc[0:-1] == filter(None,sosConfig.urn["procedure"].split(":")):
                                pass
                            else:
                                err_txt = "Supported \"procedure\" urn is: " + sosConfig.urn["procedure"]
                                raise sosException.SOSException("InvalidParameterValue","procedure",err_txt)
                        self.procedure = prc[-1]
                        
                    else:
                        err_txt = "XML parsing error (get value: procedure)"
                        raise sosException.SOSException("MissingParameterValue","procedure","Parameter \"procedure\" is mandatory with multiplicity 1",err_txt)
                
                else:
                    err_txt = "Allowed only ONE parameter \"procedure\""
                    raise sosException.SOSException("IvalidParameterValue","procedure",err_txt)
            
            else:
                err_txt = "Parameter \"procedure\" is mandatory"
                raise sosException.SOSException("MissingParameterValue","procedure","Parameter \"procedure\" is mandatory with multiplicity 1")

