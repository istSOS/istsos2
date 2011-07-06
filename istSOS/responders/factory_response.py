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

def sosFactoryResponse(sosFilter,pgdb):
    
    if sosFilter.request == "getcapabilities":
        from istSOS.responders import GCresponse
        return GCresponse.GetCapabilitiesResponse(sosFilter,pgdb)
    
    elif sosFilter.request == "describesensor":
        from istSOS.responders import DSresponse
        return DSresponse.DescribeSensorResponse(sosFilter,pgdb)
    
    elif sosFilter.request == "getobservation":
        from istSOS.responders import GOresponse
        return GOresponse.observations(sosFilter,pgdb)
    
    elif sosFilter.request == "getfeatureofinterest":
        from istSOS.responders import GFresponse
        return GFresponse.foi(sosFilter,pgdb)
    
    elif sosFilter.request == "insertobservation":
        from istSOS.responders import IOresponse
        return IOresponse.InsertObservationResponse(sosFilter,pgdb)
    
    elif sosFilter.request == "registersensor":
        from istSOS.responders import RSresponse
        return RSresponse.RegisterSensorResponse(sosFilter,pgdb)
    
    elif sosFilter.request == "updatesensordescription":
        from istSOS.responders import USDresponse
        return USDresponse.UpdateSensorDescription(sosFilter,pgdb)
   
    else:
        raise sosException.SOSException(1,"\"request\": %s not supported" %(self.request))


    

