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
from walib.resource import waResourceConfigurator
from walib import databaseManager

class waGeo(waResourceConfigurator):
    template = {
        "allowedepsg" : ["geo","allowedEPSG"],
        "istsosepsg" : ["geo","istsosepsg"],
        "xaxisname" : ["geo","xAxisName"],
        "yaxisname" : ["geo","yAxisName"],
        "zaxisname" : ["geo","zAxisName"]
    }

    def validate(self):
        
        sql = "SELECT * FROM spatial_ref_sys WHERE auth_srid IN %s"
        
        aepsgs = map( int, [ self.json["istsosepsg"] ] + self.json["allowedepsg"].split(",") )
        
        params = (tuple(aepsgs),)
        
        servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])
                
        res = servicedb.select(sql,params)
        
        if not len(res)==len(aepsgs):
            raise Exception("%s EPSG codes not valid in database srs list" %(list(set(aepsgs) - set([c[0] for c in res]) )))
        
        
        
        
        
        
        
        
        
        
