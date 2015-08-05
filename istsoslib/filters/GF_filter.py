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
from filter_utils import get_name_from_urn, getElemAtt, getElemTxt


class sosGFfilter(f.sosFilter):
    """filter object for a GetFeatureOfInterest request

    This is an extension of the base filter class (sosFilter) to accept
    GetFeatureOfInterest request and add specific parameters

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        featureOfInterest (str): the FeatureOfInterestId
        srsName (str): the desired EPSG code of results, if missing the default istSOS reference system is used

    """
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
            if requestObject.has_key("srsname"):
                self.srsName = get_name_from_urn(requestObject["srsname"],"refsystem",sosConfig)
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
            
