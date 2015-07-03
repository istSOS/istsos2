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
from walib import resource, utils, databaseManager, configManager
import sys, os
import xml.etree.ElementTree as ET
import urllib2


class waIstsos(resource.waResourceAdmin):
    def __init__(self, waEnviron):
        resource.waResourceAdmin.__init__(self,waEnviron)
        pass

class waStatus(waIstsos):
    """
    Class to execute /istsos/operations/serverstatus
    """
    def __init__(self, waEnviron):
        waIstsos.__init__(self,waEnviron)
        pass  
    def executeGet(self):
        """
        Execute GET request investigating set-up services
                      
        @note: This method creates a C{self.data} object in the form of a list of
        dictionaries as below:
            
        >>> template = {"service" : None, 
                        "offerings" : None,
                        "procedures" : None,
                        "observedProperties" : None,
                        "featuresOfInterest" : None,
                        "getCapabilities" : None,
                        "describeSensor" : None,
                        "getObservations" : None,
                        "registerSensor" : None,
                        "insertObservation" : None,
                        "getFeatureOfInterest" : None,
                        "availability" : "up"
                        } 
        """
        services = utils.getServiceList(self.waconf.paths["services"],listonly=True)
        data = []
        for service in services:
            srv = {}
            srv["service"] = service
            
            #get service configuration
            #-------------------------------------------------------------------
            defaultcfgpath = os.path.join(self.waconf.paths["services"],"default.cfg")
            servicecfgpath = os.path.join(self.waconf.paths["services"],service,service)+".cfg"
            config = configManager.waServiceConfig(defaultcfgpath,servicecfgpath)
            
            #test if service is active (check answer to GetCapabilities)
            #-------------------------------------------------------------------
            if config.serviceurl["default"] == True:
                urlget = config.serviceurl["url"] + "/" + service
            else:
                urlget = config.serviceurl["url"]
            
            request = "?request=getCapabilities&section=serviceidentification&service=SOS"
                        
            srv["availability"] = utils.verifyxmlservice(urlget+request)
            
            #test if connection is valid
            #-------------------------------------------------------------------
            connection = config.get("connection")
            try:
                servicedb = databaseManager.PgDB(connection['user'],
                                            connection['password'],
                                            connection['dbname'],
                                            connection['host'],
                                            connection['port']
                )
                srv["database"] = "active"
            except:
                srv["database"] = "not connectable"
                srv["offerings"] = None
                srv["procedures"] = None
                srv["observedProperties"] = None
                srv["featuresOfInterest"] = None
            try:
                #count offerings
                #-------------------------------------------------------------------
                srv["offerings"] = len(utils.getOfferingNamesList(servicedb,service))
            except:
                srv["offerings"] = None
                
            try:
                #count procedures
                #-------------------------------------------------------------------
                srv["procedures"] = len(utils.getProcedureNamesList(servicedb,service,offering=None))
            except:
                srv["procedures"] = None
            
            try:
                #count observed properties
                #-------------------------------------------------------------------
                srv["observedProperties"] = len(utils.getObsPropNamesList(servicedb,service,offering=None))
            except:
                srv["observedProperties"] = None
                
            try:
                #count features of interest
                #-------------------------------------------------------------------
                srv["featuresOfInterest"] = len(utils.getFoiNamesList(servicedb,service,offering=None))
            except:
                srv["featuresOfInterest"] = None
            
            #get available requests
            #-------------------------------------------------------------------
            requests_ON = config.parameters["requests"].split(",")
            for operation in ["getcapabilities","describesensor","getobservation",
                                "getfeatureofinterest","insertobservation","registersensor"]:
                if operation in requests_ON:
                    srv[operation]=True
                else:
                    srv[operation]=False
            data.append(srv)
        self.setData(data)
        self.setMessage("Serverstatus request successfully executed")
            
             
        
class waLog(waIstsos):
    def __init__(self, waEnviron):
        waIstsos.__init__(self,waEnviron)
        pass  
        
class waAbout(waIstsos):

    def __init__(self, waEnviron):
        waIstsos.__init__(self,waEnviron)
        
    def executeGet(self):
        from istsoslib import sos_version
        #from walib import wa_version
        import lib.requests as requests
        
        try:
            import lib.requests as requests
            response = requests.get("http://istsos.googlecode.com/svn/wiki/currentversion.wiki")
            data = {}
            try:
                response.raise_for_status()
                
                lastVersion = response.json()
                data["istsos_version"] = str(sos_version.version)
                data["latest_istsos_version"] = str(lastVersion["istsos_version"])
                data["latest_istsos_changelog"] = str(lastVersion["istsos_changelog"])
                data["download_url"] = "http://code.google.com/p/istsos/downloads/list"
                
                vnum_your_sos = int(data["istsos_version"].replace(".",""))
                vnum_last_sos = int(data["latest_istsos_version"].replace(".",""))
                
                if vnum_last_sos > vnum_your_sos:
                    data["istsos_message"] = "A new istsos version is available, check out the download page"
                    data["istsos_update"] = True
                else:
                    data["istsos_message"] = "You have the latest istsos version installed"
                    data["istsos_update"] = False
                
                self.setData(data)
                self.setMessage("istSOS \"About\" information successfully retrived")
                
            except Exception as e:
                
                print >> sys.stderr, "Exception: %s" %  e
                
                data["istsos_version"] = str(sos_version.version)
                data["latest_istsos_version"] = ""
                data["latest_istsos_changelog"] = ""
                data["download_url"] = "http://code.google.com/p/istsos/downloads/list"
                
                data["istsos_message"] = "updates not found"
                data["istsos_update"] = False
                
                self.setData(data)
                self.setMessage("Checking for updates failed")
                
        except:
            self.setException("Error in retriving information")
        
class waValidatedb(waIstsos):
    def __init__(self, waEnviron):
        waIstsos.__init__(self,waEnviron)
        
    def executePost(self):
        from walib.utils import validatedb
        res={}
        try:
            test_conn = validatedb(self.json["user"],self.json["password"],self.json["dbname"],
                                    self.json["host"],self.json["port"])
            res["database"] = "active"
        except:
            res["database"] = "inactive"
        self.setData(res)
        self.setMessage("Database validation request successfully executed")
        
class waInitialization(waIstsos):
    def __init__(self, waEnviron):
        waIstsos.__init__(self,waEnviron)
        
    def executeGet(self):
        try:
            os.path.isdir(self.waconf.paths["istsos"])
        except:
            error = "istsos lib not found at path %s" % self.waconf.paths["istsos"]
            print >> sys.stderr, error
        try:
            os.path.isdir(self.waconf.paths["services"])
        except:
            error = "services lib not found at path %s" % self.waconf.paths["services"]
            print >> sys.stderr, error
        defaultcfgpath = os.path.join(self.waconf.paths["services"],"default.cfg")
        try:
            os.path.isfile(defaultcfgpath)
        except:
            error = "default service configuration file at path %s" % defaultcfgpath
            print >> sys.stderr, error
        config = configManager.waServiceConfig(defaultcfgpath)
    
        self.setData({"level" : config.initialization["level"]})
        if int(config.initialization["level"]) == 0:
            self.setMessage("Your istsos has not been initializated jet")
        else:
            self.setMessage("Your istsos has been initializated")
            
    def executePut(self):
        defaultcfgpath = os.path.join(self.waconf.paths["services"],"default.cfg")
        config = configManager.waServiceConfig(defaultcfgpath)
        config.put("initialization","level",self.json["level"])
        config.save()
        self.setMessage("Initializatuion level successfully recorded")


            
            
            
          
        
    







