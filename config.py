# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
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

from os import path
services_path = path.join(path.dirname(path.abspath(__file__)), "services")
istsoslib_path = path.join(path.dirname(path.abspath(__file__)), "istsoslib")
istsoswalib_path = path.join(path.dirname(path.abspath(__file__)), "walib")
errorlog_path = path.join(path.dirname(path.abspath(__file__)), "logs")
errorlog_level = "INFO"
#==================================================================================
# if you have to move some of "istsoslib" "walib" or "service" folder
# in a different location you have to override the above paths
# with the correct new absolute paths
#==================================================================================
