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

def sosFactoryRender(response,sosConfig):
    
    res_type = str(response.__class__.__name__)
    
    if res_type == "GetCapabilitiesResponse":
        from istsoslib.renderers import GCresponseRender
        return GCresponseRender.render(response,sosConfig)
    
    elif res_type == "DescribeSensorResponse":
        from istsoslib.renderers import DSresponseRender
        return DSresponseRender.render(response,sosConfig)
    
    elif res_type == "observations":
        from istsoslib.renderers import GOresponseRender
        return GOresponseRender.render(response,sosConfig)
    
    elif res_type == "foi":
        from istsoslib.renderers import GFresponseRender
        return GFresponseRender.render(response,sosConfig)
    
    elif res_type == "InsertObservationResponse":
        from istsoslib.renderers import IOresponseRender
        return IOresponseRender.render(response,sosConfig)
    
    elif res_type == "RegisterSensorResponse":
        from istsoslib.renderers import RSresponseRender
        return RSresponseRender.render(response,sosConfig)
    
    elif res_type == "UpdateSensorDescriptionResponse":
        from istsoslib.renderers import USDresponseRender
        return USDresponseRender.render(response,sosConfig)
   
    else:
        raise sosException.SOSException("InvalidRequest","request","\"request\": %s not supported" %(str(response.__class__.__name__)))
        


    

