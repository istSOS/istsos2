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
from inspect import stack
import pprint
import tempfile
from operator import methodcaller
pp = pprint.PrettyPrinter(indent=4)

try:
    sys.path.insert(0, path.abspath("."))
    from lib.pytz import timezone
    import lib.requests as requests
    import lib.isodate as iso
except ImportError as e:
    print "\nError loading internal libs:\n >> please run the script from the istSOS root folder.\n\n"
    print str(e)
    raise e


class DebugConverter(dict):

    def log(self, message):
        raise Exception("addMessage must be overwritten")

    def addMessage(self, message):
        raise Exception("addMessage must be overwritten")

    def addWarning(self, message):
        raise Exception("addWarning must be overwritten")

    def addException(self, message):
        raise Exception("addException must be overwritten")

    def addConverter(self, converter):
        if not hasattr(self,'converters'):
            self.converters = {}
        self.converters[converter.name] = converter

class Converter():
    def __init__(self, name, url, service, folderIn, pattern, folderOut=None,
            qualityIndex=False, exceptionBehaviour={},
            user=None, password=None, debug=False,
            csvlength=5000,
            filenamecheck = None, archivefolder = None):
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
        ...
        filenamecheck = {
            'dateformat': '12_%Y-%m-%d_%H%M%S.dat',
            'datetz': '+01:00',
            'replace': ['_P','_M'],
            'timedelta': timedelta(days=1)
        }
        """
        # Can be used to speedup directory reading doinng it only once
        #  > "folderIn" and "pattern" must be identical

        self.fileArray = None
        self.name = name
        self.url = url
        self.service = service
        self.folderIn = folderIn
        self.pattern = pattern

        # Messages collected during processing
        self.messages = []
        self.warnings = []
        self.exceptions = []

        self.debugfile = False
        self.debugConverter = False
        if debug == 'file':
            self.debug = False
            try:
                self.debugfile = open(
                    os.path.join(self.folderOut, "log.txt"), "w")
            except Exception as e:
                self.log(str(e))
                self.debug = True
                self.debugfile = False

        elif isinstance(debug, DebugConverter):
            self.debugConverter = debug
            self.debugConverter.addConverter(self)
        else:
            self.debug = debug

        self.addMessage("%s initialization" % name)


        self.req = requests.session()

        self.folderOut = folderOut if folderOut is not None else tempfile.mkdtemp()

        self.qualityIndex = qualityIndex
        self.user = user
        self.password = password
        self.auth = (self.user, self.password) if (self.user != None and self.password != None) else None


        self.archivefolder = archivefolder

        # Used inf the function "skipFile"
        self.fndtz = '+01:00'
        self.fntd = self.fnre = self.fndf = None
        if type(filenamecheck) == type({}):
            if 'dateformat' in filenamecheck:
                self.fndf = filenamecheck['dateformat']
            if 'datetz' in filenamecheck:
                self.fndtz = filenamecheck['datetz']
            if 'replace' in filenamecheck:
                self.fnre = filenamecheck['replace']
            if 'timedelta' in filenamecheck:
                if not isinstance(filenamecheck['timedelta'], timedelta):
                    raise InitializationError("filenamecheck configuration contains a timedelta attribute, it shall be and instance of datetime.timedelta.")
                self.fntd = filenamecheck['timedelta']

        # >>> year = timedelta(days=365)

        # Array where Observation are stored during the parse operation
        self.observations = []
        self.observationsCheck = {}
        self.describe = None
        self.endPosition = None

        self.log("%s initialized." % self.name)

        # Single loop execution information
        self.executing = {
            'file': None
        }

        # Load describeSensor from istSOS WALib (http://localhost/istsos/wa/istsos/services/demo/procedures/T_LUGANO)
        self.loadSensorMetadata()

    def getName(self):
      return self.name

    def __del__(self):
        self.log(" > End of conversion 4 %s. Bye bye.. ;)" % self.name)
        if self.debugfile:
            self.debugfile.flush()
            self.debugfile.close()
            self.debug = True
            self.debugfile = False
            self.log("  > Debug file closed..")
        if self.archivefolder:
            self.archive()
        # Deleting temporary working directory
        for root, dirs, files in os.walk(self.folderOut, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.folderOut)

    def log(self, message):
        if self.debugConverter:
            self.debugConverter.log(message)
        elif self.debug:
            print message
        if self.debugfile:
            self.debugfile.write("%s\n" % message)


    def addMessage(self, message):
        self.log(message)
        m = {
            "time": datetime.now(),
            "stack": stack(),
            "text": message
        }
        if self.debugConverter:
            self.debugConverter.addMessage(m)
        else:
          self.messages.append(m)

    def addWarning(self, message):
        m = {
            "time": datetime.now(),
            "stack": stack(),
            "text": message
        }
        if self.debugConverter:
            self.debugConverter.addWarning(m)
        else:
          self.warnings.append(m)

    def addException(self, message):
        m = {
            "time": datetime.now(),
            "stack": stack(),
            "text": message
        }
        if self.debugConverter:
            self.debugConverter.addException(m)
        else:
          self.exceptions.append(m)

    def parse(self, fileObj, name=None):
        raise Exception("This function must be overwritten")

    def getDateFromFileName(self, name):
        if not self.fndf: # Skip this filename check
            raise Exception("File name date format not set")
        n = name
        if type(self.fnre) == type([]):
            for rep in self.fnre:
                n = n.replace(rep,'')

        return self.getDateTimeWithTimeZone(
            datetime.strptime(n, self.fndf), self.fndtz
        )


    def skipFile(self, name):
        """
        Usually the date of data transmission is inserted into the file name.
        This function checks if the file is already registered, comparing the
        sampling time with the date of trasmission which shall be after
        the endPosition.

        To enable this check, self.fndf

        Some examples:
            Filename / Date Format
            12_2014-01-17_135000_M.dat / 12_%Y-%m-%d_%H%M%S_M.dat

        """
        if not self.fndf: # Skip this filename check
            return False

        ep = self.getDSEndPosition()
        if ep == None:
            return False

        '''n = name
        if type(self.fnre) == type([]):
            for rep in self.fnre:
                n = n.replace(rep,'')

        dt = self.getDateTimeWithTimeZone(
            datetime.strptime(n, self.fndf), self.fndtz
        )
        '''
        dt = self.getDateFromFileName(name)
        print dt, ep
        if self.fntd:
            dt = dt + self.fntd
        if ep is not None and ep < dt:
            return False
        print " ok skip.."
        return True

    def getDateTimeWithTimeZone(self, dt, tz):
        dt = dt.replace(tzinfo=timezone('UTC'))
        offset = tz.split(":")
        return dt - timedelta(hours=int(offset[0]), minutes=int(offset[1]))

    def csv2istsos(self):
        from scripts import csv2istsos
        csv2istsos.execute({
              'u': self.url,
              's': self.service,
              'wd': self.folderOut,
              'p': [self.name],
              'user': self.user,
              'password': self.password
          }, conf = {
              'logger': self.debugConverter if isinstance(self.debugConverter,DebugConverter) else self,
              'description': self.describe
        })

    def istsos2istsos(self, ssrv, durl=None, function=None, resolution=None, nodataValue=None, nodataQI=None):
        from scripts import istsos2istsos
        istsos2istsos.execute({
            'v': True,
            'lm': True,
            'procedure': self.name,
            'surl': durl if durl is not None else self.url,
            'ssrv': self.service,
            'dsrv': ssrv,
            'function': function if function is not None else None,
            'resolution': resolution if resolution is not None else None,
            'nodataValue': nodataValue if nodataValue is not None else None,
            'nodataQI': nodataQI if nodataQI is not None else None,
            'user': self.user,
            'pwd': self.password
        },self)

    def archive(self):

        import zipfile

        # Creating zip archive
        archive = zipfile.ZipFile(
            os.path.join(self.archivefolder, "%s_%s.zip" % (
                self.name,
                datetime.utcnow().strftime("%Y%m%d%H%M%S"))
            ), "w") # Open the zip file for writing

        for root, dirs, files in os.walk(self.folderOut):
            for f in files:
                # adding files to zip archive
                archive.write(os.path.join(root, f),f)

        archive.close()


    def execute(self, fileArray=None):

        self.observations = []
        self.observationsCheck = {}
        self.endPosition = None

        # Load and Check folderIn + pattern and sort alfabetically
        if fileArray != None:
          self.fileArray = fileArray

        elif self.fileArray == None:
          self.fileArray = self.prepareFiles()

        falen = len(self.fileArray)
        proclen = falen

        for fileObj in self.fileArray:
            if self.skipFile(os.path.split(fileObj)[1]):
                self.log(" > Skipping file %s" % os.path.split(fileObj)[1])
                proclen = proclen - 1
                continue
            self.log(" > Working on file %s" % os.path.split(fileObj)[1])
            self.executing = {
                "file": fileObj
            }
            dat = open(fileObj,'rU')
            try:
                self.parse(dat,os.path.split(fileObj)[1])
                dat.close()
            except Exception as e:
                self.log(" !! Error while parsing file: %s" % os.path.split(fileObj)[1])
                dat.close()
                raise e

        self.addMessage("Files (processed/total): %s/%s" % (proclen,falen))
        self.addMessage("Parsed %s observations" % len(self.observations))

        if falen > 5000:
            self.addWarning("Reading folder slow, the '(%s)' folder contains %s files" % (self.folderIn,falen))

        # Validating array of observations
        self.validate()

        # Checking acquisition delay
        if self.isDelayExceeding():
            self.addWarning("%s, acquisition Time Resolution (%s %s) exceeded by %s" % (
              self.getName(), self.capability['value'], self.capability['uom'], str(self.getDelayExceeding())))

        self.addMessage(" > Last observation; %s" % self.getIOEndPosition())

        # Save the CSV file in text/csv;subtype='istSOS/2.0.0'
        if self.isEmpty(): # The procedure is registered but no observations are still inserted
            self.save()
            return True
        elif isinstance(self.getIOEndPosition(), datetime) and self.getIOEndPosition() > self.getDSEndPosition():
            self.save()
            return True
        else:
            self.log("Nothing to save")
            return False


    def loadSensorMetadata(self):
        """
        Uses WALib to get the DescribeSensor document
        """
        # Loading the sensor description document using a DescribeSensor request
        self.log(" > Loading Describe Sensor")

        res = self.req.get("%s/wa/istsos/services/%s/procedures/%s" % (
                self.url,
                self.service,
                self.name
            ),
            auth=self.auth,
            verify=False
        )
        json = res.json()
        if json['success']==False:
            raise IstSOSError ("Description of procedure %s can not be loaded: %s" % (self.name, json['message']))
        self.describe = json['data']

        self.obsindex = []
        for out in self.describe['outputs']:
            if (out['definition'].find(":qualityIndex")>=0) and (self.qualityIndex==False):
                continue
            self.obsindex.append(out['definition'])

        self.acquisitionTimeResolution = None
        if 'capabilities' in self.describe:
            for capability in self.describe['capabilities']:
                if capability['definition'] == 'urn:x-ogc:def:classifier:x-istsos:1.0:acquisitionTimeResolution':
                    self.capability = capability
                    if capability['uom'] == 'd':
                        self.acquisitionTimeResolution = timedelta(days=float(capability['value']))
                    elif capability['uom'] == 'h':
                        self.acquisitionTimeResolution = timedelta(hours=float(capability['value']))
                    elif capability['uom'] == 'min':
                        self.acquisitionTimeResolution = timedelta(minutes=float(capability['value']))
                    elif capability['uom'] == 's':
                        self.acquisitionTimeResolution = timedelta(seconds=float(capability['value']))
                    elif capability['uom'] == 'ms':
                        self.acquisitionTimeResolution = timedelta(milliseconds=float(capability['value']))
                    elif capability['uom'] == 'µs':
                        self.acquisitionTimeResolution = timedelta(microseconds=float(capability['value']))
                    break

        self.addMessage("ST[%s-%s]" % (self.getDSBeginPosition(),self.getDSEndPosition()))

    def getAcquisitionTimeResolution(self):
        return self.acquisitionTimeResolution

    def getDelay(self):
        end = self.getIOEndPosition()
        if not end:
            end = self.getDSEndPosition()
            if end:
                return self.getDateTimeWithTimeZone(datetime.utcnow(),'00:00') - end
        else:
            return self.getDateTimeWithTimeZone(datetime.utcnow(),'00:00') - end
        return None

    def isDelayExceeding(self):
        delay = self.getDelay()
        if delay!=None and self.getAcquisitionTimeResolution()!=None and delay > self.getAcquisitionTimeResolution():
            return True
        return False

    def getDelayExceeding(self):
        delay = self.getDelay()
        if delay!=None and self.getAcquisitionTimeResolution()!=None:
            return delay - self.getAcquisitionTimeResolution()
        return timedelta()

    def getDSBeginPosition(self):
        if u'constraint' in self.describe['outputs'][0]:
            return iso.parse_datetime(self.describe['outputs'][0]['constraint']['interval'][0])
        return None

    def getDSEndPosition(self):
        if u'constraint' in self.describe['outputs'][0]:
            return iso.parse_datetime(self.describe['outputs'][0]['constraint']['interval'][1])
        return None

    def isEmpty(self):
        if self.getDSBeginPosition() == None and self.getDSEndPosition() == None:
            return True
        elif self.getDSBeginPosition() == self.getDSEndPosition():
            return True
        return False

    def getDefinitions(self):
        ret = []
        for key in self.describe['outputs']:
            ret.append(key['definition'])
        return ret

    def getIOEndPosition(self):
        return self.endPosition

    def setEndPosition(self, endPosition):
        if isinstance(endPosition, datetime) and endPosition.tzinfo is not None:
            self.endPosition = endPosition
        else:
            raise IstSOSError("If you are setting the endPosition you shall use a datetime object with timezone")

    def prepareFiles(self):
        """
        Check if folder exist, and if file exist. And if there is at least one file. > Raise Exception
        """

        self.log(" > Checking folder input (%s)" % self.folderIn)

        if not os.path.isdir(self.folderIn):
            msg = "Input folder (%s) does not exist" % self.folderIn
            self.addException(msg)
            raise FileReaderError (msg)

        files = filter(path.isfile, glob.glob(os.path.join(self.folderIn, "%s" % (self.pattern))))

        if not self.fndf: # Default sort
            files.sort()
        else:
            #print "Sorting by date in file name"
            fs = {}
            for f in files:
                fs[self.getDateFromFileName(os.path.split(f)[1])] = f
            fa = sorted(fs)
            files = []
            for f in fa:
                files.append(fs[f])

        #print files



        self.log(" > %s %s found" % (len(files), "Files" if len(files)>1 else "File"))

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
                raise ObservationError("Observation (%s) is not observed by procedure %s." % (o,self.name))

        # Check if duplicate dates are present
        if observation.getEventime() in self.observationsCheck:
            # If the date is already present and the data added are different then it laounch an exception
            if str(self.observationsCheck[observation.getEventime()]) != str(observation):
                msg = "Observation (%s: %s) is already present in the file (%s)." % (self.name, observation, self.executing['file'])
                self.addException(msg)
                raise RedundacyError(msg)
            else:
                self.addWarning("Identical observation (%s: %s) has been already processed (file %s), skipping." % (self.name, observation, self.executing['file']))
        else:
            self.observations.append(observation)
            self.observationsCheck[observation.getEventime()]=observation

    def save(self):
        """
        Save the collected observation in the text/csv;subtype=istSOS/2.0.0

        with a file name composed of
          - name procedure
          - underscore _
          - datetime in UTC
          - extension (.dat)
        """
        self.log("End position: %s" % self.getIOEndPosition())
        if len(self.observations)>0:
            if self.getIOEndPosition() == None:
                f = open(os.path.join(self.folderOut,"%s_%s.dat" %(
                    self.name,

                    datetime.strftime(self.observations[-1].getEventime().astimezone(timezone('UTC')), "%Y%m%d%H%M%S%f"))), 'w')
            else:
                if self.getIOEndPosition() < self.observations[-1].getEventime():
                    raise IstSOSError("End position (%s) cannot be before the last observation event time (%s)" % (
                        self.getIOEndPosition(), self.observations[-1].getEventime()))
                f = open(os.path.join(self.folderOut,"%s_%s.dat" %(
                    self.name,
                    datetime.strftime(self.getIOEndPosition().astimezone(timezone('UTC')), "%Y%m%d%H%M%S%f"))), 'w')
            f.write("%s\n" % ",".join(self.obsindex))
            #self.observations.sort(key=lambda x: x.__eventime, reverse=True)
            #self.observations = sorted(self.observations, key=lambda observation: observation.__eventime)
            self.observations = sorted(self.observations, key=methodcaller('getEventime'))
            for o in self.observations:
                f.write("%s\n" % o.csv(",",self.obsindex))
        else:
            # End position is used to advance the sampling time in cases where
            # there is a "no data" observation (rain)
            self.addMessage("No data, but end position updated")
            if self.getIOEndPosition() == None:
                raise IstSOSError("The file has no observations, if this happens, you shall use the setEndPosition function to set the endPosition manually")
            f = open(os.path.join(self.folderOut,"%s_%s.dat" % (
                self.name,
                datetime.strftime(self.getIOEndPosition().astimezone(timezone('UTC')), "%Y%m%d%H%M%S%f"))), 'w')
            f.write("%s\n" % ",".join(self.obsindex))

        f.flush()
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
        self.__eventime = None
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
        if isinstance(eventime, datetime) and eventime.tzinfo is not None:
            self.__eventime = eventime
        else:
            raise TypeError, ('eventime arg.: it must be a Datetime Object with timezone. [%s]' % eventime)
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
