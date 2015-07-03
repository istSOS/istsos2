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
from lib import isodate as iso

def render(RS,sosConfig):
    r = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    r += "<sos:RegisterSensorResponse\n"
    r += "     xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n"
    r += "     xsi:schemaLocation=\"http://schemas.opengis.net/sos/1.0.0/sosAll.xsd\"\n"
    r += "     xmlns:sos=\"http://www.opengis.net/sos/1.0\">\n"
    r += "<AssignedSensorId>"
    r += "%s" %(RS.assignedSensorId)
    r += "</AssignedSensorId>\n"
    r += "</sos:RegisterSensorResponse>"
    return r
