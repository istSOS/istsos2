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
from walib import databaseManager
from walib.resource import waResourceService

class waSystemTypes(waResourceService):
    """
    Class to execute istsos/services/{serviceName}/systemtypes
    """

    def executeGet(self):
    
        if self.service == "default":
            raise Exception("uoms operation can not be done for default service instance.")
            
        else:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
                
            sql = """ 
                SELECT 
                  id_oty, name_oty, desc_oty
                FROM 
                  %s.obs_type 
                ORDER BY id_oty""" % self.service
            
            res = servicedb.select(sql)
            
            data = []
            
            if len(res)>0:
                for i in range(0,len(res)):
                    data.append(
                        {
                            "id": res[i]['id_oty'],
                            "name" : res[i]['name_oty'],
                            "description" : res[i]['desc_oty']
                        }
                    )
                self.setMessage("System type of service <%s> successfully retrived" % self.service)
            else:
                self.setMessage("There are not any system type in the %s database. This data is static and must be present. Contact the istSOS administrator." % self.service)
            
            self.setData(data)
        
            