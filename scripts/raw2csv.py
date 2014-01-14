# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2013 Massimiliano Cannata, Milan Antonovic
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
    
    Base class to be extended by specialized implementation to 
    handle different raw source files.
    
"""

import sys
import os
from os import path
import glob
from datetime import datetime
from datetime import timedelta
import decimal
import pprint
pp = pprint.PrettyPrinter(indent=4)

try:
    sys.path.insert(0, path.abspath("."))
    from lib.pytz import timezone
    import lib.requests as requests
    import lib.isodate as iso
except ImportError as e:
    print "\nError loading internal libs:\n >> please run the script from the istSOS root folder.\n\n"
    raise e
    
class Converter():
    req = requests.session()
    def __init__(self, name, url, service, folderIn, pattern, folderOut, qualityIndex=False, exceptionBehaviour={}, user=None, password=None, debug=False, csvlength=5000):
        """
        Info:        
        
        name: procedure name
        url: url of the istSOS service
        service: service instance name
        folderIn: folder where raw data are stored (file:///home/pippo/rawdata)
        pattern: name of the raw data file (can contains wildcard *, eg: "T_TRE_*.dat")
        folderOut: folder where the formatted istSOS type files are created
        qualityIndex: force a quality index value for all the observed properties
        exceptionBehaviour: example {
            "RedundacyError": "overwrite",
            "StrictTimeSeriesError": "raise"
        }
        user and password: if user and password are required
        """
        self.name = name
        self.url = url
        self.service = service
        self.url = url
        self.service = service
        self.folderIn = folderIn
        self.pattern = pattern
        self.folderOut = folderOut
        self.qualityIndex = qualityIndex
        self.user = user
        self.password = password
        self.auth = (self.user, self.password) if (self.user != None and self.password != None) else None
        self.debug = debug
        
        # Array where Observation are stored during the parse operation
        self.observations = []
        self.observationsCheck = {}
        self.describe = None
        self.endPosition = None
        
        if self.debug:
            print "%s initialized." % self.name
            
        # Load describeSensor from istSOS WALib (http://localhost/istsos/wa/istsos/services/demo/procedures/T_LUGANO)
        self.loadSensorMetadata()
        
        
    def parse(self, fileObj, name=None):
        raise Exception("This function must be overwritten")
    
    def getDateTimeWithTimeZone(self, dt, tz):
        dt = dt.replace(tzinfo=timezone('UTC'))
        offset = tz.split(":")
        return dt - timedelta(hours=int(offset[0]), minutes=int(offset[1]))
    
    def execute(self):
        
        self.observations = []
        self.observationsCheck = {}
        self.endPosition = None
        
        # Load and Check folderIn + pattern and sort alfabetically
        fileArray = self.prepareFiles()
            
        for fileObj in fileArray:
            if self.debug:
                print " > working on file %s" % os.path.split(fileObj)[1]
            self.parse(open(fileObj,'rU'),os.path.split(fileObj)[1])
        
        if self.debug:
            print " > Parsed %s observations" % len(self.observations)
        
        # Validating array of observations
        self.validate()
        
        # Save the CSV file in text/csv;subtype='istSOS/2.0.0'
        if isinstance(self.getIOEndPosition(), datetime) and self.getIOEndPosition() > self.getDSEndPosition():
            self.save()
        else:
            if self.debug:
                print " > Nothing to save"
        
        return
        
    
    def loadSensorMetadata(self):
        """
        Uses WALib to get the DescribeSensor document
        """
        # Loading the sensor description document using a DescribeSensor request
        if self.debug:
            print " > Loading Describe Sensor"
        res = self.req.get("%s/wa/istsos/services/%s/procedures/%s" % (
                self.url,
                self.service,
                self.name
            ), 
            prefetch=True, 
            auth=self.auth, 
            verify=False
        )
        if res.json['success']==False:
            raise IstSOSError ("Description of procedure %s can not be loaded: %s" % (self.name, res.json['message']))
        self.describe = res.json['data']
        
        if self.debug:
            print self.describe
                
        
        self.obsindex = []
        for out in self.describe['outputs']:
            if (out['definition'].find(":qualityIndex")>=0) and (self.qualityIndex==False):
                continue
            self.obsindex.append(out['definition'])
            
    def getDSBeginPosition(self):
        if u'constraint' in self.describe['outputs'][0]:
            return iso.parse_datetime(self.describe['outputs'][0]['constraint']['interval'][0])
        else:
            return None
        
    def getDSEndPosition(self):
        if u'constraint' in self.describe['outputs'][0]:
            return iso.parse_datetime(self.describe['outputs'][0]['constraint']['interval'][1])
        else:
            return None
    
    def getDefinitions(self):
        ret = []
        for key in self.describe['outputs']:
            ret.append(key['definition'])
        return ret
    
    def getIOEndPosition(self):
        return self.endPosition
        
    def setEndPosition(self, endPosition):
        if isinstance(endPosition, datetime):
            self.endPosition = endPosition
        else:
            raise IstSOSError("If you are setting the endPosition manually you shall use a datetime object")
    
    def prepareFiles(self):
        """
        Check if folder exist, and if file exist. And if there is at least one file. > Raise Exception
        """
        
        if self.debug:
            print " > Checking folder input (%s)" % self.folderIn
        
        if not os.path.isdir(self.folderIn):
            raise FileReaderError ( "Input folder (%s) does not exist" % self.folderIn)
        
        files = filter(path.isfile, glob.glob(os.path.join(self.folderIn, "%s" % (self.pattern))))
        files.sort()
        
        if self.debug:
            print " > %s %s found" % (len(files), "Files" if len(files)>1 else "File")
            
        return files
        
    def validate(self):
        pass
    
    def addObservation(self, observation):
        """
        Validity check and raise exceptions (raise RedundacyError or manage)
        
        try:
            importer.Converter.addObservation(self,observation)
        except RedundacyError as e:
            if "RedundacyError" in self.exceptionBehaviour:
                pass
            else:
                raise e
        pass
        """
        # Check if Observed property are observed by this procedure
        obs = observation.getObservedProperties()
        for o in obs:
            if not o in self.obsindex:
                raise ObservationError("Observation (%s) is not observed by this procedure." % (o))
        
        if observation.getEventime() in self.observationsCheck:
            raise RedundacyError("Observation (%s) is already present in the file." % (observation))
            
        self.observations.append(observation)
        self.observationsCheck[observation.getEventime()]=observation
    
    def save(self):
        """
        Save the collected observation in the text/csv;subtype=istSOS/2.0.0
        """
        if len(self.observations)>0:            
            if self.endPosition == None:
                f = open(os.path.join(self.folderOut,"%s_%s.dat" %(
                    self.name,
                    datetime.strftime(self.observations[-1].getEventime(), "%Y%m%d%H%M%S"))), 'w')
            else:
                if self.endPosition < self.observations[-1].getEventime():
                    raise IstSOSError("End position (%s) cannot be before the last observation event time (%s)" % (self.endPosition, self.observations[-1].getEventime()))
                f = open(os.path.join(self.folderOut,"%s_%s.dat" %(
                    self.name,
                    datetime.strftime(self.observations[-1].getEventime(), "%Y%m%d%H%M%S"))), 'w')
            f.write("%s\n" % ",".join(self.obsindex))
            for o in self.observations:
                f.write("%s\n" % o.csv(",",self.obsindex))
        else:
            if self.endPosition == None:
                raise IstSOSError("The file has no observations, if this can happens, you shall use the setEndPosition function to set the endPosition manually")
            f = open(os.path.join(self.folderOut,"%s_%s.dat" %(
                self.name,
                datetime.strftime(self.endPosition, "%Y%m%d%H%M%S"))), 'w')
            f.write("%s\n" % ",".join(self.obsindex))
        f.close()
        
class InitializationError(Exception):
    pass
        
class RedundacyError(Exception):
    pass

class IstSOSError(Exception):
    pass

class FileReaderError(Exception):
    pass

class ObservationError(Exception):
    pass
    

class Observation:
    "Single Measure"
    fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
    def __init__(self, eventime, values):
        self.setEventime(eventime)
        self.setValue(values)
        pass

    def getValue(self):
        return self.__value

    def setValue(self, values):
        if type(values) == type({}):
            self.__value = {}
            for s in values:
                v = float(values[s])
                # Controllo vinculo valore numerico
                if isinstance(v, (int, long, float, decimal.Decimal)):
                    self.__value[s]= v
                else:
                    raise TypeError, ('Observations.setValue( %s ): it must be Numeric') % values
                    
    def getObservedProperties(self):
        return self.__value.keys()
                    
    def getEventime(self):
        return self.__eventime

    def setEventime(self, eventime):
        if isinstance(eventime, datetime):
            self.__eventime = eventime
        else:
            raise TypeError, ('eventime arg.: it must be a Datetime Object. [%s]' % eventime)
        pass
    
    def setObservedValue(self,obs,value):
        self.__value[obs] = value

    def getObservedValue(self,obs):
        return self.__value[obs]

    def __str__(self):
        vals = []
        tmp = self.getValue()
        for t in tmp:
            vals.append("%s" % tmp[t])
        return self.getEventime().strftime(self.fmt) + " | %s" % " | ".join(vals)
    
    def __cmp__(self, other):
        if self.getEventime() > other.getEventime():
            return 1
        elif self.getEventime() == other.getEventime():
            return 0
        else: # self.setEventime() < other.setEventime():
            return -1

    def __eq__(self, other):
        if other == None:
            return False
        elif self.getEventime() == other.getEventime():
            return True
        else:
            return False

    def __ne__(self, other):
        if other == None:
            return True
        elif self.getEventime() == other.getEventime():
            return False
        else:
            return True
            
    def csv(self, separator=",", pattern=None):
        vals = []
        if pattern != None:
            for p in pattern:
                if (p.rfind('iso8601') == -1): 
                    vals.append(str(self.getObservedValue(p)))
        else:
            vs = self.getValue()
            for key, value in vs.items():
                vals += [str(value)]
        return "%s%s%s" % (self.getEventime().strftime(self.fmt), separator, separator.join(vals))
