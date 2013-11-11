# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
#---------------------------------------------------------------------------
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
#---------------------------------------------------------------------------
# Created on Mon Nov 11 11:05:41 2013
#---------------------------------------------------------------------------
"""
description:
    
"""

from datetime import datetime
from datetime import timedelta
from os import path
from scripts import importer


class CampbellImporter(importer.Importer):
            
    def getDate(self, year, day, hour, second=None):
        # Parsing date with year, days from 1 January and hours in integers
        y = int(year)
        d = int (day)
        h = m = s = 0
        dDiff = 1
        if(len(hour) == 1):
            m = int(hour[0])
        elif(len(hour) == 2):
            m = int(hour[0] + hour[1])
        elif(len(hour) == 3):
            h = int(hour[0])
            m = int(hour[1] + hour[2])
        elif(len(hour) == 4):
            h = int(hour[0] + hour[1])
            if h == 24:
                h = 0
                dDiff = 0
            m = int(hour[2] + hour[3])
        if second!=None:
            s = int(second)
        return (datetime(y, 1, 1, h, m, s, 0) + timedelta(days=(d-dDiff)))
    
    def customParse(self, fileObj, name, column, observation):
        
        for line in fileObj.readlines():
            arr = line.strip(' \t\n\r').split(",")            
            if len(arr)>0:
                date = self.getDate(arr[1],arr[2],arr[3])
                self.setEndPosition(date)
                if arr[0] == column:
                    values = {}
                    for obs in observation.keys():
                        values[obs] = arr[observation[obs]]
                    self.addObservation(
                        importer.Observation(date, values)
                    )
    
class TLuganoImporter(CampbellImporter):
    
    def __init__(self):
        importer.Importer.__init__(self, 'T_LUGANO', 
            'http://localhost/istsos', 'demo',
            path.normpath("%s/test/scripts/data" % path.abspath(".")), 'T_LUGANO.dat', 
            path.normpath("%s/test/scripts/data" % path.abspath(".")),
            debug=True)
    
    def parse(self, fileObj, name):
        self.customParse(fileObj, name, '101', {
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature": 6
        })
        
class PLuganoImporter(CampbellImporter):
    
    def __init__(self):
        importer.Importer.__init__(self, 'T_LUGANO', 
            'http://localhost/istsos', 'demo',
            path.normpath("%s/test/scripts/data" % path.abspath(".")), 'T_LUGANO.dat', 
            path.normpath("%s/test/scripts/data" % path.abspath(".")),
            debug=True)
    
    def parse(self, fileObj, name):
        self.customParse(fileObj, name, '101', {
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature": 6
        })
