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
    
"""

# istsos/services/test/virtualprocedures/Q_TEST/code
from walib.resource import waResourceService
import os
import codecs


# istsos/services/test/virtualprocedures/Q_TEST/ratingcurves
class waCode(waResourceService):
    """
    class to handle SOS code for virtual procedure
    
    {
    "code" : "....",    
    }
    """
    
    def __init__(self,waEnviron):
        waResourceService.__init__(self,waEnviron)
        #self.demomsg = "Sorry but for security reasons virtual procedures cannot be deleted, updated or created"
        self.servicename = self.pathinfo[2]
        self.procedurename =  self.pathinfo[4]
        self.procedureFolder = os.path.join(self.servicepath, "virtual", self.procedurename)
        self.codefile = os.path.join(self.servicepath, "virtual", self.procedurename, self.procedurename+".py")
        
    def executeGet(self):
        #filename = self.RCpath + "/" + self.RCprocedure + ".dat"
        if not os.path.exists(self.procedureFolder):
            raise Exception("Virtual procedure %s not available: please check!" % self.procedurename)
        if not os.path.exists(self.codefile):
            raise Exception("Virtual procedure code file %s not available: please check!" % self.procedurename)
        
        with open(self.codefile, 'r') as content_file:
            content = content_file.read()
            self.setData({"code":content})
            self.setMessage("Virtual procedure code secessfully loaded")
    
    def executeDelete(self):
        #raise Exception(self.demomsg)
        if not os.path.exists(self.procedureFolder):
            raise Exception("Virtual procedure %s not available: please check!")
        if not os.path.exists(self.codefile):
            raise Exception("Virtual procedure code file %s not available: please check!")
        os.remove(self.codefile)
        
    def executePost(self):
        #raise Exception(self.demomsg)
        if not os.path.exists(self.procedureFolder):
            raise Exception("Virtual procedure %s not available: please check!")
        if os.path.exists(self.codefile):
            raise Exception("Virtual procedure code file %s already exists!")
        if not "code" in self.json:
            raise Exception("code parameter is mandatory")
        with open(self.codefile, 'w') as f:
            f.write(self.json["code"])
      
    def executePut(self):
        #raise Exception(self.demomsg)
        if not os.path.exists(self.procedureFolder):
            raise Exception("Virtual procedure %s not available: please check!")
        if not os.path.exists(self.codefile):
            raise Exception("Virtual procedure code file %s does not exist!")
        if not "code" in self.json:
            raise Exception("code parameter is mandatory")
        
        #with open(self.codefile, 'w') as f:
        
        with codecs.open(self.codefile, "w", "utf-8") as f:
            f.write(self.json["code"])
            f.close()
  
        
