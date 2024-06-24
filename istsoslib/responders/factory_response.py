# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
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

def sosFactoryResponse(sosFilter, pgdb):
    if sosFilter.version != '1.0.0':
        return sosException.SOSException(
            "InvalidRequest", "request",
            "\"version\": %s not supported" % (sosFilter.version)
        )

    if sosFilter.request == "getcapabilities":
        from istsoslib.responders import GCresponse
        return GCresponse.GetCapabilitiesResponse(sosFilter, pgdb)
    
    elif sosFilter.request == "describesensor":
        from istsoslib.responders import DSresponse
        return DSresponse.DescribeSensorResponse(sosFilter, pgdb)
    
    elif sosFilter.request == "getobservation":
        from istsoslib.responders import GOresponse
        return GOresponse.GetObservationResponse(sosFilter, pgdb)

    elif sosFilter.request == "getfeatureofinterest":
        from istsoslib.responders import GFresponse
        return GFresponse.foi(sosFilter, pgdb)

    # TODO: IGRAC DISABLES THIS
    # elif sosFilter.request == "insertobservation":
    #     from istsoslib.responders import IOresponse
    #     return IOresponse.InsertObservationResponse(sosFilter, pgdb)
    #
    # elif sosFilter.request == "registersensor":
    #     from istsoslib.responders import RSresponse
    #     return RSresponse.RegisterSensorResponse(sosFilter, pgdb)
    #
    # elif sosFilter.request == "updatesensordescription":
    #     from istsoslib.responders import USDresponse
    #     return USDresponse.UpdateSensorDescription(sosFilter, pgdb)

    else:
        raise sosException.SOSException("InvalidRequest", "request",
            "\"request\": %s not supported" % (sosFilter.request))
