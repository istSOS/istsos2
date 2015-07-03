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
import psycopg2 # @TODO the right library
import psycopg2.extras
import os

#import sosConfig
from istsoslib import sosDatabase
from istsoslib import sosException
#import mx.DateTime.ISO
from lib import isodate as iso

def get_name_from_urn(stringa,urnName,sosConfig):
    a = stringa.split(":")
    name = a[-1]
    urn = sosConfig.urn[urnName].split(":")
    if len(a)>1 and not name=="iso8601":
        for index in range(len(urn)-1):
            if urn[index]==a[index]:
                pass
            else:
                raise Exception("Urn \"%s\" is not valid: %s."%(a,urn))
    return name

class UpdateSensorDescriptionResponse:
    #self.assignedObservationId
    def __init__(self,filter,pgdb):
        
        #check assigned sensor id
        sql  = "SELECT id_prc, name_prc FROM %s.procedures WHERE assignedid_prc='%s'" %(filter.sosConfig.schema,get_name_from_urn(filter.assignedSensorId,"sensor",filter.sosConfig))
        try:
            prc = pgdb.select(sql)[0]
        except:
            raise sosException.SOSException("InvalidParameterValue","assignedSensorId","assignedSensorId: '%s' is not valid!" %(filter.assignedSensorId))
    
        #----------------------------------------
        # create SensorML for inserted procedure
        #----------------------------------------
        
        f = open(filter.sosConfig.sensorMLpath + filter.procedure + ".xml", 'w')
        
        xml_pre = """<SensorML xmlns:sml="http://www.opengis.net/sensorML/1.0.1"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:swe="http://www.opengis.net/swe/1.0.1"
          xmlns:gml="http://www.opengis.net/gml"
          xmlns:xlink="http://www.w3.org/1999/xlink"
          xsi:schemaLocation="http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd"
          version="1.0.1">
  <member xlink:arcrole="urn:ogc:def:process:OGC:detector">"""
 
        xml_ascii = filter.xmlSensorDescription.toxml().encode('ascii','ignore')
        
        xml_post = "  </member>\n</SensorML>"
        
        f.write(xml_pre + xml_ascii + xml_post)
        f.close()
        
        self.procedure = prc["name_prc"]
        
    
    
    
    
    
    
