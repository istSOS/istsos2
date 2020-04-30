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

# File example: test/scripts/data/in/ott/A_LIS_MON.dat
# =====================================
# 0LIS_MON_A;0002;20200421;093000;10.9
# 0LIS_MON_A;0002;20200421;094000;10.9
# 0LIS_MON_A;0002;20200421;095000;10.9
# 0LIS_MON_A;0002;20200421;100000;10.9
# 0LIS_MON_A;0002;20200421;101000;10.9
# 0LIS_MON_A;0002;20200421;102000;10.9
# 0LIS_MON_A;0002;20200421;103000;10.9
# 0LIS_MON_A;PBAT;20200421;090000;1392
# 0LIS_MON_A;PBAT;20200421;100000;1406
# 0LIS_MON_A;RSSI;20200421;090000;2
# 0LIS_MON_A;RSSI;20200421;100000;5
# 0LIS_MON_A;UBAT;20200421;090000;3.56
# 0LIS_MON_A;UBAT;20200421;100000;3.61
# =====================================

from scripts.converter import ecolog

alismon = ecolog.Ecolog1k('A_LIS_MON', {
        "tz": "+02:00",
        "rowid": ['0002', 1], # value, column index 
        "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
        "column": 4,
        "date": 2,
        "time": 3,
        "tz": '+02:00',
    }, 'http://localhost/istsos', 'demo',
    "test/scripts/data/in/ott", 'A_LIS_MON.dat', 
    "/var/log/istsos/",
    debug=True
)

# parse raw data
if alismon.execute():
    # insert observations
    alismon.csv2istsos()

"""

from datetime import datetime
from datetime import timedelta
from os import path
from scripts import raw2csv
from types import FunctionType
import traceback

class Ecolog1k(raw2csv.Converter):

    def __init__(self, procedureName, config, url, service, 
                 inputDir, fileNamePattern, outputDir=None, 
                 qualityIndex=False, exceptionBehaviour={}, 
                 user=None, password=None, debug=False, 
                 csvlength=5000, filenamecheck=None, archivefolder = None):
        """
        Ott EkoLog1000 constructor
        """

        max_index = 0

        if config:
            self.config = config
        else:
            raise Exception("config param is mandatory")

        if not "rowid" in config:
            raise Exception("rowid config param is mandatory")

        if not "column" in config:
            raise Exception("column config param is mandatory")

        max_index = max(max_index, self.config['column'])

        #  Check date config
        if not "date" in config:
            self.config['date'] = 2

        max_index = max(max_index, self.config['date'])

        if not "date_frm" in config:
            self.config['date_frm'] = '%Y%m%d'

        if not "time" in config:
            self.config['time'] = 3

        max_index = max(max_index, self.config['time'])

        if not "time_frm" in config:
            self.config['time_frm'] = '%H%M%S'

        if not "tz" in config:
            self.config['tz'] = '+02:00' # Default sensors time @SUPSI :)

        self.max_index = max_index

        raw2csv.Converter.__init__(
            self, procedureName, url, service,
            inputDir, fileNamePattern, outputDir,
            qualityIndex, exceptionBehaviour,
            user, password, debug, csvlength,
            filenamecheck, archivefolder,
            extra={
                "disable_identical_warning": True,
                "disable_redundancy_error": True
            }
        )

    def parseDate(self, row):

        # Extract date
        date_str = row[self.config['date']]

        # Extract time
        time_str = row[self.config['time']]

        # Preparing date string
        dt = "%s %s" % (date_str, time_str)

        # Preparing time string
        frm = "%s %s" % (
            self.config['date_frm'],
            self.config['time_frm']
        )

        # parsing into datetime object
        d = datetime.strptime(dt, frm)

        # Adding timezone info
        d = self.getDateTimeWithTimeZone(d, self.config["tz"])
        
        # if then function added, execute the function on datetime object
        # if "then" in self.config["datetime"] and (
        #         isinstance(self.config["datetime"]["then"], FunctionType)):
        #     d = self.config["datetime"]["then"](d)

        return d

    def parse(self, fileObj, name):
        try:
            lines = fileObj.readlines()
            lineCounter = 0
            for line in lines:

                lineCounter = lineCounter + 1

                s = line.strip(' \t\n\r')

                row = s.split(";")

                if s != '' and len(row)>=(self.max_index+1):

                    date = self.parseDate(row)
                    
                    if str(row[self.config['rowid'][1]]) == str(self.config['rowid'][0]):

                        self.setEndPosition(date)
                        
                        values = {}
                        value = row[self.config["column"]]

                        if value.find('[') >= 0:
                            value = '-999.9'

                        values[
                            self.config["observedProperty"]
                        ] = value
                        
                        self.addObservation(
                            raw2csv.Observation(date, values)
                        )

        except Exception as ex:
            traceback.print_exc()
            raise ex