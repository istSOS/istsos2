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
from istSOS import sosException

def sosFactoryRender(response):
    
    res_type = str(response.__class__.__name__)
    
    if res_type == "GetCapabilitiesResponse":
        from istSOS.renderers import GCresponseRender
        return GCresponseRender.render(response)
    
    elif res_type == "DescribeSensorResponse":
        from istSOS.renderers import DSresponseRender
        return DSresponseRender.render(response)
    
    elif res_type == "observations":
        from istSOS.renderers import GOresponseRender
        return GOresponseRender.render(response)
    
    elif res_type == "foi":
        from istSOS.renderers import GFresponseRender
        return GFresponseRender.render(response)
    
    elif res_type == "InsertObservationResponse":
        from istSOS.renderers import IOresponseRender
        return IOresponseRender.render(response)
    
    elif res_type == "RegisterSensorResponse":
        from istSOS.renderers import RSresponseRender
        return RSresponseRender.render(response)
    
    elif res_type == "UpdateSensorDescriptionResponse":
        from istSOS.renderers import USDresponseRender
        return USDresponseRender.render(response)
   
    else:
        raise sosException.SOSException(1,str(response.__class__.__name__))


    

