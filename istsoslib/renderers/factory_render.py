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

def sosFactoryRender(response,sosConfig):
    
    res_type = str(response.__class__.__name__)
    
    if res_type == "GetCapabilitiesResponse":
        from istsoslib.renderers import GCresponseRender
        if response.version == '2.0.0':
            return GCresponseRender.render_2_0_0(response, sosConfig)
            
        else:
            return GCresponseRender.render(response, sosConfig)
    
    elif res_type == "DescribeSensorResponse":
        from istsoslib.renderers import DSresponseRender
        if response.version == '2.0.0':
            return DSresponseRender.render_2_0_0(response, sosConfig)
            
        else:
            return DSresponseRender.render(response,sosConfig)
    
    elif res_type in ["GetObservationResponse", "GetObservationResponse_2_0_0"]:
        from istsoslib.renderers import GOresponseRender
        return GOresponseRender.render(response, sosConfig)
    
    elif res_type == "foi":
        from istsoslib.renderers import GFresponseRender
        return GFresponseRender.render(response, sosConfig)
    
    elif res_type == "InsertObservationResponse":
        from istsoslib.renderers import IOresponseRender
        return IOresponseRender.render(response, sosConfig)
    
    elif res_type == "RegisterSensorResponse":
        from istsoslib.renderers import RSresponseRender
        return RSresponseRender.render(response, sosConfig)
    
    elif res_type == "UpdateSensorDescriptionResponse":
        from istsoslib.renderers import USDresponseRender
        return USDresponseRender.render(response, sosConfig)
   
    else:
        raise sosException.SOSException("InvalidRequest", "request", 
            "\"request\": %s not supported" %(str(response.__class__.__name__)))
        


    

