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

class waConnection(waResourceConfigurator):
    template = {
        "user": ["connection","user"],
        "password": ["connection","password"],
        "host": ["connection","host"],
        "port": ["connection","port"],
        "dbname": ["connection","dbname"]
    }

    def executePut(self):
        from walib.utils import validatedb
        test = validatedb(self.json["user"],self.json["password"],self.json["dbname"],
                                    self.json["host"],self.json["port"],self.service)
        waResourceConfigurator.executePut(self)

class waValidatedb(waResourceService):
    """
    Implementation of the operation/validatedb GET operation
    """
    def validateGet(self):
        from walib.utils import validatedb
        test = validatedb(self.serviceconf.connection["user"],
                         self.serviceconf.connection["password"],
                         self.serviceconf.connection["dbname"],
                         self.serviceconf.connection["host"],
                         self.serviceconf.connection["port"],
                         self.service)
    
    def executeGet(self):
        """
        Test the connection parameters in the server/service configuration
        """
        self.validateGet()
        self.setMessage("Configured connection parameters successfully tested")
