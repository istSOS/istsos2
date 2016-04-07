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
import sys, os
from walib import configManager
from walib import utils as ut
from istsoslib import sosException

class ServiceNotFound(Exception):
    def __init__(self, message, service):
        Exception.__init__(self, message)
        self.service = service

class waResource(object):
    """
    Base class for istSOS Web Admin REST operations
    """

    def __init__(self, waEnviron,loadjson=True):
        """
        Initialize resource object
        @param waEnviron: waEnviron variable see L(wa)
        @type waEnviron: C{dictionary}
        """
        self.user = False
        if 'user' in waEnviron:
            self.user = waEnviron['user']

        self.response = {
            "success": True,
            "message": ""
        }
        self.waEnviron = waEnviron
        self.method = waEnviron['method']
        self.pathinfo = waEnviron['pathinfo']
        self.json = None
        self.postRequest = None
        if self.method in ["POST","PUT"] and loadjson==True:
            import json
            self.json = ut.encodeobject(json.loads(waEnviron['wsgi_input']))

    def checkAuthorization(self):
        return True

    def validateGet(self):
        """ base method to validate GET request """
        raise Exception("%s.validateGet method is not implemented!" % self.__class__.__name__)

    def validatePost(self):
        """ base method to validate POST request """
        raise Exception("%s.validatePost method is not implemented!" % self.__class__.__name__)

    def validatePut(self):
        """ base method to validate PUT request """
        raise Exception("%s.validatePut method is not implemented!" % self.__class__.__name__)

    def validateDelete(self):
        """ base method to validate DELETE request """
        raise Exception("%s.validateDelete method is not implemented!" % self.__class__.__name__)

    def executeGet(self):
        """ base method to execute GET request """
        raise Exception("%s.executeGet method is not implemented!" % self.__class__.__name__)

    def executePost(self):
        """ base method to execute POST request """
        raise Exception("%s.executePost method is not implemented!" % self.__class__.__name__)

    def executePut(self):
        """ base method to execute PUT request """
        raise Exception("%s.executePut method is not implemented!" % self.__class__.__name__)

    def executeDelete(self):
        """ base method to execute DELETE request """
        raise Exception("%s.executeDelete method is not implemented!" % self.__class__.__name__)

    def getResponse(self):
        import json
        #return json.dumps(self.response, ensure_ascii=False)
        return json.dumps(self.response)

    def getMime(self):
        return "application/json"

    def setData(self,data):
        """ Set data in response """
        self.response['data'] = data
        self.response['total'] = len(data) if type(data)==type([]) else 0

    def setMessage(self,msg):
        """ Set message in response """
        self.response['message'] = msg

    def setException(self,msg):
        """ Set exception message in response """
        self.response['message']    = msg
        self.response['resource']   = self.__class__.__name__
        self.response['method']     = self.waEnviron["method"]
        self.response['path']       = self.waEnviron["path"]
        self.response['success']    = False

    def setLog(self,log):
        """ set message in log """
        self.response['log'] = log

class waResourceAdmin(waResource):
    """
    Extension class of istSOS Web Admin REST operations that manages Wab Admin Configuration
    """
    def __init__(self, waEnviron,loadjson=True):
        waResource.__init__(self,waEnviron,loadjson)
        class waconf():
            def __init__(self):
                self.paths = {}
        self.waconf = waconf()
        self.waconf.paths["services"] = waEnviron["services_path"]
        self.waconf.paths["istsos"] = waEnviron["istsos_path"]

        #self.waconf = configManager.waConfig()


class waResourceService(waResourceAdmin):
    def __init__(self, waEnviron, service=None, loadjson=True):
        waResourceAdmin.__init__(self, waEnviron, loadjson)
        if service is None:
            i = self.pathinfo.index("services")
            if i > 0 and i < len(self.pathinfo)-1:
                self.service = self.pathinfo[i+1]
            else:
                self.service = None
        else:
            self.service = service

        self.checkAuthorization()

        #set default config path
        if not os.path.isdir(self.waconf.paths["services"]):
            raise Exception("servicespath is not configured in the wa.cfg file [%s]." % self.waconf.paths["services"])

        defaultCFGpath = os.path.join(self.waconf.paths["services"], "default.cfg")
        if not os.path.isfile(defaultCFGpath):
            raise Exception("istsos [default] configuration file not found in %s." % (defaultCFGpath))

        if not (self.service is None or self.service == 'default'):
            serviceCFGpath = os.path.join(self.waconf.paths["services"], "%s" % self.service, "%s.cfg" % self.service)
            if not os.path.isfile(serviceCFGpath):
                raise ServiceNotFound("istsos [%s] configuration file not found in %s." % (self.service,serviceCFGpath),self.service)
            self.servicepath = os.path.join(self.waconf.paths["services"], "%s" % self.service)

            sensormlpath = os.path.join(self.waconf.paths["services"], "%s" % self.service, "sml")
            if not os.path.isdir(sensormlpath):
                raise Exception("istsos [%s] sensorML folder not found in %s." % (self.service,sensormlpath))
            self.sensormlpath = sensormlpath

            virtualpath = os.path.join(self.waconf.paths["services"], "%s" % self.service, "virtual")
            if not os.path.isdir(virtualpath):
                raise Exception("istsos [%s] virtual procedures folder not found in %s." % (self.service,virtualpath))
            self.virtualpath = virtualpath

        if self.service == None or self.service == 'default':
            self.serviceconf = configManager.waServiceConfig(defaultCFGpath)
        else:
            self.serviceconf = configManager.waServiceConfig(defaultCFGpath, serviceCFGpath)

    def checkAuthorization(self):
        if self.service and self.user and not self.user.isAdmin():
            if self.service == 'default':
                raise sosException.SOSException(
                    "ResourceNotFound", "Authorization", "Access to admin request are not allowed.")
            elif not self.user.allowedService(self.service):
                raise sosException.SOSException(
                    "ResourceNotFound", "Authorization", "You don't have the permissions to access the '%s' instance." % self.service)


class waResourceConfigurator(waResourceService):
    def __init__(self, waEnviron,loadjson=True):
        waResourceService.__init__(self,waEnviron,None,loadjson)
        tmp = []
        for key in self.template:
            tmp.append(self.template[key][0])
        self.sections = list(set(tmp))

    def validate(self):
        pass

    def executeGet(self):
        """
        Execute operation GET for on service configuration sections
        """

        data = {
            'default': True
        }
        for key in self.template:
            temp = self.serviceconf.get(self.template[key][0])
            if not temp.has_key(self.template[key][1]):
                raise Exception("Configuration error: value \"%s\" not present in section \"%s\", check your template settings!" % (self.template[key][1],self.template[key][0]))
            data[key] = temp[self.template[key][1]]
        for s in self.sections:
            data['default'] = data['default'] and self.serviceconf.get(s)["default"]
        self.setData(data)
        self.setMessage("Information successfully retrived")
        return data

    def executePut(self, json=None):
        """
        Execute operation PUT for on service configuration sections and return new values
        """
        if json is not None:
            self.json = json

        self.validate()
        for key in self.template:
            if not self.json.has_key(key):
                raise Exception("Key \"%s\" not present in json data" % (key))
            self.serviceconf.put(
                self.template[key][0],
                self.template[key][1],
                str(self.json[key]))

        self.serviceconf.save()
        self.executeGet()
        self.setMessage("Information successfully updated")

    def executeDelete(self):
        """
        Execute operation DELETE for on service configuration sections

        @note: it does not work on default service
        """
        for s in self.sections:
            self.serviceconf.delete(s)
        self.serviceconf.save()
        self.setMessage("Information successfully reset to default values!")
