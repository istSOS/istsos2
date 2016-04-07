# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# =============================================================================

__author__ = 'Massimiliano Cannata, Milan Antonovic'
__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__credits__ = []
__license__ = 'GPL2'
__version__ = '1.0'
__maintainer__ = 'Massimiliano Cannata, Milan Antonovic'
__email__ = 'geoservice@supsi.ch'

from walib.resource import waResourceConfigurator, waResourceService
import sys


class waMqtt(waResourceConfigurator):
    '''
    [mqtt]
    broker_url = localhost
    broker_port = 9083
    broker_topic = /istsos/updates/
    broker_user =
    broker_password =
    '''

    template = {
        "broker_url": ["mqtt", "broker_url"],
        "broker_port": ["mqtt", "broker_port"],
        "broker_topic": ["mqtt", "broker_topic"],
        "broker_user": ["mqtt", "broker_user"],
        "broker_password": ["mqtt", "broker_password"]
    }
