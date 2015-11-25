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
import sys

class waProvider(waResourceConfigurator):
    '''
    [provider]
    contactCountry = Switzerland
    providerName = Istituto Scienze della Terra
    contactCity = Lugano
    contactAdminArea = Canton Ticino
    contactVoice = +4179123456
    contactEmail = clark.kent@superman.com
    contactDeliveryPoint = Via Cippili
    contactName = Pinco Pallino
    contactPostalCode = 6900
    contactPosition = Data manager
    providerSite = http://istgeo.ist.supsi.ch
    contactFax = +4179123459
    '''
    
    template = {
        "providername" : ["provider","providerName"],
        "providersite" : ["provider","providerSite"],
        "contactname" : ["provider","contactName"],
        "contactposition" : ["provider","contactPosition"],
        "contactdeliverypoint" : ["provider","contactDeliveryPoint"],
        "contactpostalcode" : ["provider","contactPostalCode"],
        "contactcity" : ["provider","contactCity"],
        "contactadminarea" : ["provider","contactAdminArea"],
        "contactcountry" : ["provider","contactCountry"],
        "contactvoice" : ["provider","contactVoice"],
        "contactfax" : ["provider","contactFax"],
        "contactemail" : ["provider","contactEmail"]
    }
    
    def checkAuthorization(self):
        pass

