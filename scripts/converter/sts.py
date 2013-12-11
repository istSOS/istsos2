# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2013 Milan Antonovic, Massimiliano Cannata
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

Usage example:
    
sts = testConverter.StsImporter('A_MAR_MAR2', 
    'http://localhost/istsos', 'pippo', 
    "istsos/test/scripts/data/in", '100640_mWC.csv', 
    "istsos/test/scripts/data/out",
sts.execute()
    
"""

from scripts import raw2csv
from datetime import datetime
from lib.pytz import timezone

class StsImporter(raw2csv.Converter):
    def __init__(self, procedureName, url, service, inputDir, fileNamePattern, outputDir, debug):
        raw2csv.Converter.__init__(self, procedureName, url, service,
            inputDir, fileNamePattern, outputDir,
            debug=debug)
        
    def parse(self, fileObj, fileName):
        
        dateformat = "%Y-%m-%d %H:%M:%S"
        op = self.getDefinitions()[1]
        
        for line in fileObj.readlines():
            
            if line.find('100640')>-1 or line.find('100190')>-1:
                continue
            
            pair = line.split(";")
            
            val = {
                op: pair[1]
            }
            
            data = datetime.strptime(pair[0], dateformat)
            data = datetime(
                    data.year, data.month, data.day, data.hour, 
                    data.minute, 0, tzinfo=timezone("CET"))
            
            self.setEndPosition(data)
            self.addObservation(
                raw2csv.Observation(data, val)
            )