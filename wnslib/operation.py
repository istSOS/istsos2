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
from walib import utils as ut
from walib import configManager
import os


class wnsOperation(object):
    """
    Base class for istSOS WNS
    """

    def __init__(self, wnsEnviron, loadjson=True):
        """
        Initialize resource object
        
        parameters:
            wnsEnviron (dict): wnsEnviron variable see L(wa)
        """
        self.response = {
            "success": True,
            "message": ""
        }
        self.wnsEnviron = wnsEnviron
        self.method = wnsEnviron['method']
        self.pathinfo = wnsEnviron['pathinfo']
        self.json = None
        self.postRequest = None
        if self.method in ["POST", "PUT"] and loadjson:
            import json
            self.json = ut.encodeobject(json.loads(wnsEnviron['wsgi_input']))

        defaultCFGpath = os.path.join(wnsEnviron["services_path"],
                                                    "default.cfg")
        self.serviceconf = configManager.waServiceConfig(defaultCFGpath)

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

    def setData(self, data):
        """ Set data in response """
        self.response['data'] = data
        self.response['total'] = len(data) if type(data) == type([]) else 0

    def setMessage(self, msg):
        """ Set message in response """
        self.response['message'] = msg

    def setException(self, msg):
        """ Set exception message in response """
        self.response['message'] = msg
        self.response['resource'] = self.__class__.__name__
        self.response['method'] = self.wnsEnviron["method"]
        self.response['path'] = self.wnsEnviron["path"]
        self.response['success'] = False

    def setLog(self, log):
        """ set message in log """
        self.response['log'] = log
