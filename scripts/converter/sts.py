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

@todo to be enhanced, it is a little bit hardcoded :(

Usage example:
    
# File example: test/scripts/data/in/sts/100190_WTemp.csv
# =====================================
# 100190 Maggia;WTemp ˚C
# 2013-11-24 00:00:00;4.67401
# 2013-11-24 00:10:00;4.67672
# 2013-11-24 00:20:01;4.67909
# 2013-11-24 00:30:00;4.67354
# 2013-11-24 00:40:01;4.68056
# 2013-11-24 00:50:00;4.67847
# 2013-11-24 01:00:00;4.67735
# 2013-11-24 01:10:00;4.67884
# 2013-11-24 01:20:01;4.67987
# 2013-11-24 01:30:00;4.68368
# =====================================

sts = testConverter.StsImporter('A_MAR_MAR2', {
        "tz": "+04:30"
    },
    'http://localhost/istsos', 'pippo', 
    "test/scripts/data/in", '100640_mWC.csv', 
    "test/scripts/data/out"
)
sts.execute()
    
"""

from scripts import raw2csv
from datetime import datetime

class StsImporter(raw2csv.Converter):
            
    def __init__(self, procedureName, config, url, service, inputDir, 
                 fileNamePattern, outputDir=None, qualityIndex=False, 
                 exceptionBehaviour={}, user=None, password=None, debug=False, 
                 csvlength=5000, filenamecheck=None, archivefolder = None):                     
        self.config = config
        raw2csv.Converter.__init__(self, procedureName, url, service, inputDir, 
            fileNamePattern, outputDir, qualityIndex, 
            exceptionBehaviour, user, password, debug, 
            csvlength, filenamecheck, archivefolder)
            
        
    def parse(self, fileObj, fileName):
        
        skipline = fileName.split("_")[0]
        
        dateformat = "%Y-%m-%d %H:%M:%S"
        
        # STS procedures have only one observed property
        op = self.getDefinitions()[1] 
        cnt = 0
        linetmp = ''
        try: 
            for line in fileObj.readlines():
                cnt = cnt+1
                linetmp = line
                
                if line.find(skipline)>-1 or line.find('data')>-1 or len(line)==0:
                    continue
                
                pair = line.split(";")
                
                if len(pair)!=2:
                  continue
                
                try:
                    data = datetime.strptime(pair[0], dateformat)
                except Exception as e:
                    continue
            
                val = {
                    op: pair[1]
                }
                        
                data = datetime.strptime(pair[0], dateformat)
                if "tz" in self.config:
                    data = self.getDateTimeWithTimeZone(data, self.config["tz"])
                
                # Removing seconds from date
                data = datetime(
                    data.year, data.month, data.day, data.hour, 
                    data.minute, 0, tzinfo=data.tzinfo)
                            
                    
                self.setEndPosition(data)
                self.addObservation(
                    raw2csv.Observation(data, val)
                )
                
        except Exception as e:
            raise Exception("Error at row: %s:%s\n%s" % (cnt,linetmp,e))

