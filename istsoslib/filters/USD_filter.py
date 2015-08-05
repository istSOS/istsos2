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
from filter_utils import get_name_from_urn, getElemTxt, getElemAtt

class sosUSDfilter(f.sosFilter): 
    """filter object for an updateSensorDescription request

    Attributes:
        request (str): the request submitted
        service (str): the name of the service requested
        version (str): the version of the service
        assignedSensorId (str): the assigned sensor ID
        xmlSensorDescription (str): the XML representation of the senor description
    """

    def __init__(self,sosRequest,method,requestObject,sosConfig):
        f.sosFilter.__init__(self,sosRequest,method,requestObject,sosConfig)
        #**************************
        if method == "GET":
            raise sosException.SOSException("NoApplicableCode",None,"registerSensor request support only POST method!")
            
        if method == "POST":
            
            #---assignedSensorId
            asid = requestObject.getElementsByTagName('AssignedSensorId')
            if len(asid)==1:
                    self.assignedSensorId = getElemTxt(asid[0])
            else:
                raise sosException.SOSException("MissingParameterValue","AssignedSensorId","AssignedSensorId parameter is mandatory with multiplicity 1")
            
            #---SensorDescription            
            sd = requestObject.getElementsByTagName('SensorDescription')
            if len(sd)==1:
                self.xmlSensorDescription = sd[0]
            else:
                raise sosException.SOSException("MissingParameterValue","SensorDescription","SensorDescription parameter is mandatory with multiplicity 1")
                
                
                
                
                
                
