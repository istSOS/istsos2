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
"""

Usage example:

# File example: test/scripts/data/in/campbell/LUGANO.dat
# =====================================
# 101,2013,276,400,13.86,19.77,13.46,89.1,983
# 101,2013,276,410,13.86,19.71,13.32,90.8,984
# 101,2013,276,420,13.86,19.61,13.12,92.1,984
# 101,2013,276,430,13.86,19.5,12.96,93.8,984
# 99,2013,276,436,43
# 101,2013,276,440,13.86,19.37,12.64,94.6,984
# 101,2013,276,450,13.86,19.22,12.56,95.4,984
# 101,2013,276,500,13.86,19.08,12.44,95.6,984
# 101,2013,276,510,13.86,18.94,12.4,96.2,984
# 101,2013,276,520,13.86,18.8,12.23,96.4,984
# =====================================

lugano = CampbellImporter('T_LUGANO', {
        "tz": "+02:00",
        "rowid": "99",
        "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
        "column": 6,
        "date": [1,2,3,4]
    }, 'http://localhost/istsos', 'demo',
    "test/scripts/data/in", 'LUGANO.dat', 
    "test/scripts/data/out",
    debug=True)

lugano.execute();
    
"""

from datetime import datetime
from datetime import timedelta
from os import path
from scripts import raw2csv

class CampbellImporter(raw2csv.Converter):
    
    
    def __init__(self, procedureName, config, url, service, 
                 inputDir, fileNamePattern, outputDir=None, 
                 qualityIndex=False, exceptionBehaviour={}, 
                 user=None, password=None, debug=False, 
                 csvlength=5000, filenamecheck=None, archivefolder = None):
        """
        CampbellImporter constructor
        
        @param config: procedure specific configuration
        @type config: C{dictionary}
        
        Tick example 1: {
            "rowid": "99",
            "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
            "value": "0.2",
            "date": [1,2,3,4]
        }
        
        Temperature example 2: {
            "rowid": "101",
            "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
            "column": 4,
            "date": [1,2,3]
        }
        """
        self.config = config
        if not "date" in config:
            self.config['date']=[1,2,3]
        raw2csv.Converter.__init__(self, procedureName, url, service,
            inputDir, fileNamePattern, outputDir,
            qualityIndex, exceptionBehaviour, user, password, debug, csvlength, filenamecheck, archivefolder)
    
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
        
        ret = (datetime(y, 1, 1, h, m, s, 0) + timedelta(days=(d-dDiff)))
        
        if "tz" in self.config:
            ret = self.getDateTimeWithTimeZone(ret, self.config["tz"])
            
        return ret
    
    def parse(self, fileObj, name):
        lines = fileObj.readlines()
        lineCounter = 0
        for line in lines:
            lineCounter = lineCounter + 1
            s = line.strip(' \t\n\r')
            arr = s.split(",")
            if s != '' and len(arr)>0:
                
                date = self.getDate(arr[self.config['date'][0]],arr[self.config['date'][1]],arr[self.config['date'][2]])
                self.setEndPosition(date)
                
                if str(arr[0]) == str(self.config['rowid']):
                    
                    if len(self.config['date'])==3:
                        date = self.getDate(arr[self.config['date'][0]],arr[self.config['date'][1]],arr[self.config['date'][2]])
                    elif len(self.config['date'])==4:
                        date = self.getDate(arr[self.config['date'][0]],arr[self.config['date'][1]],arr[self.config['date'][2]],arr[self.config['date'][3]])
                    else:
                        raise raw2csv.IstSOSError("Date configuration mismatch.")
                        
                    self.setEndPosition(date)
                    
                    values = {}
                    
                    if "column" in self.config:
                        # It happens that some lines are cutted so the line is skipped
                        try:
                            arr[self.config["column"]]
                        except:
                            print "Error in line %s: %s" % (lineCounter, arr)
                            continue
                        values[self.config["observedProperty"]] = arr[self.config["column"]]
                    else:
                        values[self.config["observedProperty"]] = float(self.config["value"])
                    
                    self.addObservation(
                        raw2csv.Observation(date, values)
                    )
                    

class TLuganoImporter(CampbellImporter):
    def __init__(self):
        raw2csv.Converter.__init__(self, 'T_LUGANO', 
            'http://localhost/istsos', 'demo',
            path.normpath("%s/test/scripts/data/in" % path.abspath(".")), 'LUGANO.dat', 
            path.normpath("%s/test/scripts/data/out" % path.abspath(".")),
            debug=True)
    def parse(self, fileObj, name):
        self.customParse(fileObj, name, '101', {
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature": 6
        })
        
class PLuganoImporter(CampbellImporter):
    def __init__(self):
        raw2csv.Converter.__init__(self, 'P_LUGANO', 
            'http://localhost/istsos', 'demo',
            path.normpath("%s/test/scripts/data/in" % path.abspath(".")), 'LUGANO.dat', 
            path.normpath("%s/test/scripts/data/out" % path.abspath(".")),
            debug=True)
    def parse(self, fileObj, name):
        self.customParse(fileObj, name, '99', {
            "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall": "0.2"
        }, [1,2,3,4])

