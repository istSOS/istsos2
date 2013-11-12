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
    
    def customParse(self, fileObj, name, column, conf, dateConf=[1,2,3]):
        for line in fileObj.readlines():
            arr = line.strip(' \t\n\r').split(",")            
            if len(arr)>0:
                
                date = self.getDate(arr[dateConf[0]],arr[dateConf[1]],arr[dateConf[2]])
                self.setEndPosition(date)
                
                if arr[0] == column:
                    
                    if len(dateConf)==3:
                        date = self.getDate(arr[dateConf[0]],arr[dateConf[1]],arr[dateConf[2]])
                    elif len(dateConf)==4:
                        date = self.getDate(arr[dateConf[0]],arr[dateConf[1]],arr[dateConf[2]],arr[dateConf[3]])
                    else:
                        raise importer.IstSOSError("Date configuration mismatch.")
                    self.setEndPosition(date)
                    
                    values = {}
                    for obs in conf.keys():
                        if type(conf[obs])==type(""):
                            values[obs] = float(conf[obs])
                        else:
                            values[obs] = arr[conf[obs]]
                    self.addObservation(
                        importer.Observation(date, values)
                    )
    
class TLuganoImporter(CampbellImporter):
    def __init__(self):
        importer.Importer.__init__(self, 'T_LUGANO', 
            'http://localhost/istsos', 'demo',
            path.normpath("%s/test/scripts/data" % path.abspath(".")), 'LUGANO.dat', 
            path.normpath("%s/test/scripts/data" % path.abspath(".")),
            debug=True)
    def parse(self, fileObj, name):
        self.customParse(fileObj, name, '101', {
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature": 6
        })
        
class PLuganoImporter(CampbellImporter):
    def __init__(self):
        importer.Importer.__init__(self, 'P_LUGANO', 
            'http://localhost/istsos', 'demo',
            path.normpath("%s/test/scripts/data" % path.abspath(".")), 'LUGANO.dat', 
            path.normpath("%s/test/scripts/data" % path.abspath(".")),
            debug=True)
    def parse(self, fileObj, name):
        self.customParse(fileObj, name, '99', {
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall": "0.2"
        }, [1,2,3,4])
