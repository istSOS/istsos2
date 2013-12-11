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

Single Observed property usage example:
    
sts = KernImporter('WT_LAV_RSV', {
        "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
        "column": 6
    },
    'http://localhost/istsos', 'pippo',
    "istsos/test/scripts/data/in", 'HBTIa-04_*',
    "istsos/test/scripts/data/out",
    True)
sts.execute()


Multiple Observed property usage example:

sts = KernImporter('WT_LAV_RSV', [{
        "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
        "column": 6
    },{
        "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
        "column": 7
    }],
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
    def __init__(self, procedureName, config, url, service, inputDir, fileNamePattern, outputDir, debug):
        self.config = config
        raw2csv.Converter.__init__(self, procedureName, url, service,
            inputDir, fileNamePattern, outputDir,
            debug=debug)
            
    def minutesdate(self, year, minutes):
        d1 = datetime(year=int(year),month=1,day=1)
        return (d1 + timedelta(minutes=int(minutes)))
        
    def parse(self, fileObj, fileName):
        
        upDate = fileName.split('.')[0].split('_') # HBTIa-14_12_183730_10
        year = datetime.strptime(upDate[-3],'%y').year # 12 -> 2012
        mins = upDate[-2] # 183730
        
        upDate = self.minutesdate(year,mins)
        upDate = datetime(
                    upDate.year, upDate.month, upDate.day, upDate.hour, 
                    upDate.minute, upDate.second, tzinfo=timezone("CET"))
        
        if self.getDSEndPosition() != None and (isinstance(self.getDSEndPosition(), datetime) and  upDate <= self.getDSEndPosition()):
            if self.debug:
                print " > Skipping file update: %s - endPosition = %s" % (upDate, self.getDSEndPosition())
            return
        
        isHead = False
        isData = False
        cnt = 0
        for line in fileObj.readlines():
            cnt = cnt+1
            try:
                # indica una riga di intestazione con la data di inizio dei dati
                if line.find('\x01TI')>=0:
                    line = line.replace('\x01','')
                    isHead = True
                else:
                    isHead = False
                    
                # inidica l'inizio di un blocco con i dati
                if line.find('\x02')>=0:
                    line = line.replace('\x02','')
                    isData = True
                
                # inidica la fine del blocco con i dati 
                if line.find('\x03')>=0:
                    line = line.replace('\x03','')
                    isData = False
                    
                # inidica la fine del file
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

                    # Controllo del capo d'anno
                    if int(startMinutes)>int(dataMinutes):
                        year = year + 1
                        
                    d = self.minutesdate(year,dataMinutes)
                    d = datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, 
                        d.microsecond, tzinfo=timezone("CET"))
                    
                    self.setEndPosition(d)
                    
                    val = {}
                    
                    if type(self.config) == type([]):
                        for conf in self.config:
                            val[conf['observedProperty']]=line[conf['column']]
                    else:
                        val[self.config['observedProperty']]=line[self.config['column']]
                        
                    self.addObservation(
                        raw2csv.Observation(d,val)
                    )
                   
            except Exception as e:
                print "%s-%s:%s" % (fileName,cnt,line)
                print traceback.print_exc()
                raise e