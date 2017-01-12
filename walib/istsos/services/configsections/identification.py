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
from walib.resource import waResourceConfigurator, waResourceService

class waIdentification(waResourceConfigurator):
    '''
    [identification]
    keywords = SOS,IST,SUPSI
    abstract = hydro-meteorological monitoring network
    authority = x-ist
    urnversion = 1.0
    fees = NONE
    accessConstrains = NONE
    title = IST Sensor Observation Service
    '''
    template = {
            "title" : ["identification","title"],
            "abstract" : ["identification","abstract"],
            "authority" : ["identification","authority"],
            "urnversion" : ["identification","urnversion"],
            "fees" : ["identification","fees"],
            "keywords" : ["identification","keywords"],
            "accessconstrains" : ["identification","accessConstrains"]
    }

