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
from walib.resource import waResourceService

class waConfigsections(waResourceService):
    """
    Implementation of the configsection GET operation 
    (if non configsection setted all the sections are returned)
    """
    def executeGet(self):
        data = {}
        for section in self.serviceconf.sections:
            if section == "connection":
                from walib.istsos.services.configsections import connection
                sect = connection.waConnection(self.waEnviron)
                data[section] = sect.executeGet()
            if section == "identification":
                from walib.istsos.services.configsections import identification
                sect = identification.waIdentification(self.waEnviron)
                data[section] = sect.executeGet()
            if section == "geo":
                from walib.istsos.services.configsections import geo
                sect = geo.waGeo(self.waEnviron)
                data[section] = sect.executeGet() 
            if section == "getobservation":
                from walib.istsos.services.configsections import getobservation
                sect = getobservation.waGetobservation(self.waEnviron)
                data[section] = sect.executeGet()
            if section == "provider":
                from walib.istsos.services.configsections import provider
                sect = provider.waProvider(self.waEnviron)
                data[section] = sect.executeGet()
            if section == "serviceurl":
                from walib.istsos.services.configsections import serviceurl
                sect = serviceurl.waServiceurl(self.waEnviron)
                data[section] = sect.executeGet()
            if section == "urn":
                from walib.istsos.services.configsections import urn
                sect = urn.waUrn(self.waEnviron)
                data[section] = sect.executeGet()
        self.setData(data)
        self.setMessage("List of sections successfully returned")
        
    def executePut(self):
        import json
        for section in self.json:
            if section == "connection":
                from walib.istsos.services.configsections import connection
                self.waEnviron['wsgi_input'] = json.dumps(self.json[section])
                sect = connection.waConnection(self.waEnviron)
                sect.executePut()
            if section == "identification":
                from walib.istsos.services.configsections import identification
                self.waEnviron['wsgi_input'] = json.dumps(self.json[section])
                sect = identification.waIdentification(self.waEnviron)
                sect.executePut()
            if section == "geo":
                from walib.istsos.services.configsections import geo
                self.waEnviron['wsgi_input'] = json.dumps(self.json[section])
                sect = geo.waGeo(self.waEnviron)
                sect.executePut() 
            if section == "getobservation":
                from walib.istsos.services.configsections import getobservation
                self.waEnviron['wsgi_input'] = json.dumps(self.json[section])
                sect = getobservation.waGetobservation(self.waEnviron)
                sect.executePut()
            if section == "provider":
                from walib.istsos.services.configsections import provider
                self.waEnviron['wsgi_input'] = json.dumps(self.json[section])
                sect = provider.waProvider(self.waEnviron)
                sect.executePut()
            if section == "serviceurl":
                from walib.istsos.services.configsections import serviceurl
                self.waEnviron['wsgi_input'] = json.dumps(self.json[section])
                sect = serviceurl.waServiceurl(self.waEnviron)
                sect.executePut()                
        
        self.setMessage("Configuration Sections successfully updated")

