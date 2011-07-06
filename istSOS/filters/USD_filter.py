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
from istSOS.filters import filter as f
from istSOS import sosException
from osgeo import ogr

def getElemTxt(node):
    if node.hasChildNodes():
        val = node.firstChild
        if val.nodeType == val.TEXT_NODE:
            return str(val.data)
        else:
            err_txt = "get node text value: \"%s\" is not of type TEXT" %(node.nodeName)
            raise sosException.SOSException(1,err_txt)
    else:
            err_txt = "get node text value: \"%s\" has no child node" %(node.nodeName)
            raise sosException.SOSException(1,err_txt)
        
def getElemAtt(node,att):
    if att in node.attributes.keys():
        return str(node.getAttribute(att))
    else:
        None
        #err_txt = "get node attribute value: \"%s\"has no \"%s\" attribute" %(node.nodeName,att)
        #raise sosException.SOSException(1,err_txt)

def get_name_from_urn(stringa,urnName):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1:
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise sosException.SOSException(1,"Urn \"%s\" is not valid: %s."%(a,urn))
    return name 

class sosUSDfilter(f.sosFilter): 
    "filter object for an updateSensorDescription request"
    """
    self.assignedSensorId = None
    self.xmlSensorDescription = None
    """

    def __init__(self,sosRequest,method,requestObject):
        f.sosFilter.__init__(self,sosRequest,method,requestObject)
        #**************************
        if method == "GET":
            raise sosException.SOSException(2,"registerSensor request support only POST method!")
            
        if method == "POST":
            
            #---assignedSensorId
            asid = requestObject.getElementsByTagName('AssignedSensorId')
            if len(asid)==1:
                    self.assignedSensorId = getElemTxt(asid[0])
            else:
                raise sosException.SOSException(1,"AssignedSensorId parameter is mandatory with multiplicity 1")
            
            #---SensorDescription            
            sd = requestObject.getElementsByTagName('SensorDescription')
            if len(sd)==1:
                self.xmlSensorDescription = sd[0]
            else:
                raise sosException.SOSException(1,"SensorDescription parameter is mandatory with multiplicity 1")
                
                
                
                
                
                
