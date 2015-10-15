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

File example:
=========================================================
TI	2014	006020	000010	HBTIa	04	Laveggio Segoma
Q	1	1	0	0	Pegel m
Q	2	3	0	0	Temperatur
Q	3	23	0	0	Spannung
D	6030	1	10	0.427	2	10	8.47	3	10	27.56

=========================================================

Single Observed property usage example:
    
sts = KernImporter('WT_LAV_RSV', {
        "tz": "+02:00",
        "observations": {
            "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
            "column": 6
        }
    },
    'http://localhost/istsos', 'pippo',
    "istsos/test/scripts/data/in", 'HBTIa-04_*',
    "istsos/test/scripts/data/out",
    True)
sts.execute()


Multiple Observed property usage example:

sts = KernImporter('WT_LAV_RSV', {
        "tz": "+02:00",
        "observations": [{
            "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
            "column": 6
        },{
            "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
            "column": 7
        }]
    },
    'http://localhost/istsos', 'pippo',
    "istsos/test/scripts/data/in", 'HBTIa-04_*',
    "istsos/test/scripts/data/out",
    True)
sts.execute()

"""

from scripts import raw2csv
from datetime import datetime
from datetime import timedelta
from lib.pytz import timezone
import traceback

class KernImporter(raw2csv.Converter):
    def __init__(self, procedureName, config, url, service, inputDir, 
                 fileNamePattern, outputDir=None, qualityIndex=False, 
                 exceptionBehaviour={}, user=None, password=None, debug=False, 
                 csvlength=5000, filenamecheck=None, archivefolder = None):
        self.config = config        
        raw2csv.Converter.__init__(self, procedureName, url, service,
            inputDir, fileNamePattern, outputDir,
            qualityIndex, exceptionBehaviour, user, password, debug, csvlength, filenamecheck, archivefolder)
        
        '''d1 = self.getDSEndPosition() - timedelta(minutes=-10080)  # one week behind
        d2 = datetime(year=dt.year,month=1,day=1)
        
        perfect_pattern = "%s_%s" % (str(d1.year)[-2:], ((d1-d2).total_seconds()/60))'''
        
    def minutesdate(self, year, minutes):
        d1 = datetime(year=int(year),month=1,day=1)
        d1 = (d1 + timedelta(minutes=int(minutes)))
        if "tz" in self.config:
            d1 = self.getDateTimeWithTimeZone(d1, self.config["tz"])
        return d1
    
    def skipFile(self, name):
        upDate = name.split('.')[0].split('_') # HBTIa-14_12_183730_10
        year = datetime.strptime(upDate[-3],'%y').year # 12 -> 2012
        mins = upDate[-2] # 183730
        
        upDate = self.minutesdate(year,mins)
        if self.getDSEndPosition() != None and (
                isinstance(self.getDSEndPosition(), datetime) and  
                upDate <= self.getDSEndPosition()):
            return True
        return False
    
    def parse(self, fileObj, fileName):
        
        isHead = False
        isData = False
        cnt = 0
        for line in fileObj.readlines():
            cnt = cnt+1
            try:
                # Special characters https://it.wikipedia.org/wiki/Carattere_di_controllo#Tavole
                
                # SOH indica una riga di intestazione con la data di inizio dei dati
                if line.find('\x01TI')>=0:
                    line = line.replace('\x01','')
                    isHead = True
                else:
                    isHead = False
                    
                # STX indica l'inizio di un blocco con i dati
                if line.find('\x02')>=0:
                    line = line.replace('\x02','')
                    isData = True
                
                # ETX indica la fine del blocco con i dati 
                if line.find('\x03')>=0:
                    line = line.replace('\x03','')
                    isData = False
                    
                # EOT indica la fine del file
                if line.find('\x04')>=0:
                    line = line.replace('\x04','')
                    break
                
                line = line.split()
                
                if isHead:
                    # Estrazione dell'anno e i minuti dalla riga di intestazione
                    #          \/       \/
                    # ['TI', '2012', '183721', '000000', 'HBTIa', '14', 'KERN', 'TL-1', 'SN:557']
                    year = datetime.strptime(line[1],'%Y').year
                    startMinutes = line[2]
                
                if isData and line[0] in ['D','d','o']:
                    dataMinutes = line[1]

                    # Controllo del capodanno
                    if int(startMinutes)>int(dataMinutes):
                        year = year + 1
                        
                    d = self.minutesdate(year,dataMinutes)
                    
                    #d = datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, 
                    #    d.microsecond, tzinfo=timezone("CET"))
                    
                    self.setEndPosition(d)
                    
                    val = {}
                    
                    if type(self.config["observations"]) == type([]):
                        for obs in self.config["observations"]:
                            val[obs['observedProperty']]=line[obs['column']]
                    else:
                        val[self.config["observations"]['observedProperty']]=line[self.config["observations"]['column']]
                        
                    self.addObservation(
                        raw2csv.Observation(d,val)
                    )
                   
            except Exception as e:
                self.log("%s:%s\n Line: %s" % (fileName,cnt,line))
                self.log(traceback.print_exc())
                raise e
