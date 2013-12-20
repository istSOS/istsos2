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
from istsoslib.filters import filter as f
from istsoslib import sosException

def getElemTxt(node):
    if node.hasChildNodes():
        val = node.firstChild
        if val.nodeType == val.TEXT_NODE:
            return str(val.data)
        else:
            err_txt = "get node text value: \"%s\" is not of type TEXT" %(node.nodeName)
            raise Exception(err_txt)
    else:
            err_txt = "get node text value: \"%s\" has no child node" %(node.nodeName)
            raise Exception(err_txt)
        
def getElemAtt(node,att):
    if att in node.attributes.keys():
        return str(node.getAttribute(att))
    else:
        err_txt = "get node attribute value: \"%s\"has no \"%s\" attribute" %(node.nodeName,att)
        raise Exception(err_txt)
    
def get_name_from_urn(stringa,urnName,sosConfig):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1:
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise Exception(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name 

class sosGFfilter(f.sosFilter):
    "filter object for a GetFeatureOfInterest request"
    def __init__(self,sosRequest,method,requestObject,sosConfig):
        f.sosFilter.__init__(self,sosRequest,method,requestObject,sosConfig)
        #**************************
        if method == "GET":
            #---FeatureOfInterest
            if not requestObject.has_key("featureofinterestid"):
                raise sosException.SOSException("MissingParameterValue","FeatureOfInterestId","Parameter \"FeatureOfInterestId\" is required with multiplicity 1")
            else:
                self.featureOfInterest = get_name_from_urn(requestObject["featureofinterestid"],"feature",sosConfig) #one-many ID
            #---srsName
            if requestObject.has_key("srsName"):
                self.srsName = get_name_from_urn(requestObject["srsName"],"refsystem",sosConfig)
                if not self.srsName in sosConfig.parameters["GO_srs"]:
                    raise sosException.SOSException("OptionNotSupported","srsName","Supported \"srsName\" valueas are: " + ",".join(sosConfig.parameters["GO_srs"]))
            else:
                self.srsName = sosConfig.parameters["GO_srs"][0]
        if method == "POST":
            #---FeatureOfInterest
            fets = requestObject.getElementsByTagName('FeatureOfInterestId')
            if len(fets)==1:
                try:
                    self.featureOfInterest = get_name_from_urn(getElemAtt(fets[0],"xlink:href"),"feature",sosConfig)
                except:
                    try:
                        self.featureOfInterest = get_name_from_urn(getElemTxt(fets[0]),"feature",sosConfig)
                    except:
                        err_txt = "XML parsing error (get value: FeatureOfInterestId)"
                        raise sosException.SOSException("NoApplicableCode",None,err_txt)
            else:
                err_txt = "parameter \"FeatureOfInterestId\" is mandatory with multiplicity 1"
                if len(fets)==0:
                    raise sosException.SOSException("MissingParameterValue","FeatureOfInterestId",err_txt)
                else:
                    raise sosException.SOSException("NoApplicableCode",None,err_txt)

            #---srsName
            srss = requestObject.getElementsByTagName('srsName')
            if len(srss) ==1:
                self.srsName = get_name_from_urn(getElemTxt(srss[0]),"refsystem",sosConfig)
                if not self.srsName in sosConfig.parameters["GO_srs"]:
                    raise sosException.SOSException("OptionNotSupported","srsName","Supported \"srsName\" valueas are: " + ",".join(sosConfig.parameters["GO_srs"]))
            elif len(srss) == 0:
                self.srsName = sosConfig.parameters["GO_srs"][0]
            else:
                err_txt = "parameter \"srsName\" is optional with multiplicity 1"
                raise sosException.SOSException("NoApplicableCode",None,err_txt)
            
