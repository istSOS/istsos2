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
from walib import resource
import config
import sys

def getUser(environ):
    #if config.authentication:
    if 'HTTP_AUTHORIZATION' in environ:
        import hashlib
        import base64
        from os import path
        try:
          import cPickle as pic
        except ImportError:
          try:
            import pickle as pic
          except ImportError as ie:
            print >> sys.stderr, ("Failed to import pickle from any known place")
            raise ie
        s, base64string = environ['HTTP_AUTHORIZATION'].split()
        username, password = base64.decodestring(base64string).split(':')
        passwordFile = path.join(config.services_path, "istsos.passwd")
        with open(passwordFile, 'rb') as f:
            users = pic.load(f)
            return User(username, users[username])
            #environ["user"] = User(username, users[username])
    #else:
    #    raise Exception("Authorization is enabled in config file but HTTP_AUTHORIZATION header not present. Check the security page in the documentation")
            
    return User("admin", {
        "password": "",
        "roles": {
            "admin": {
                "*": ["*"]
            }
        }
    })
    
class User():

    def __init__(self, username, data):
        self.username = username
        self.password = data['password']
        self.roles = data['roles']
        self.groups = data['roles'].keys()
        #print >> sys.stderr, "\n\nUser: %s" % pp.pprint(self)
    
    def getJSON(self):
        return {
            "username": self.username,
            "roles": self.roles,
            "groups": self.groups
        }
    
    def isAdmin(self):
        if "admin" in self.groups:
            return True
        return False
    
    def isNetworkManager(self):
        if "networkmanager" in self.groups:
            return True
        return False
    
    def isDataManager(self):
        if "datamanager" in self.groups:
            return True
        return False
    
    def isViewer(self):
        if "viewer" in self.groups:
            return True
        return False
    
    def allowedService(self, service):
        #print >> sys.stderr, "Checking service '%s' for user '%s'" % (service, self.username)
        for group in self.groups:
            #print >> sys.stderr, " > group '%s'" % group
            keys = self.roles[group].keys()
            #print >> sys.stderr, "    > keys %s" % keys
            if "*" in keys or service in keys:
                return True
        print >> sys.stderr, "NOT AUTHORIZED"
        return False
        
    def allowedProcedure(self, service, procedure):
        if self.allowedService(service):
            special = False
            for group in self.groups:
                if role == "*":
                    if "*" in self.roles[role]['services']["*"] or procedure in self.roles[role]['services']["*"]:
                        return True
                elif service in self.roles[role]['services']:
                    if "*" in self.roles[role]['services'][service] or procedure in self.roles[role]['services'][service]:
                        return True
                    else:
                        return False
        return False
        

class waUsers(resource.waResource):

    def __init__(self, waEnviron,loadjson=True):
        resource.waResource.__init__(self, waEnviron, loadjson)
        self.mime = "application/javascript"
        self.jsonResponse = False
            
    def getResponse(self):
        if self.jsonResponse:
            import json
            if self.response['success']:
                return json.dumps(self.response, ensure_ascii=False)
            else:
                return json.dumps(self.response, ensure_ascii=False)
        else:
            if self.response['success']:
                return "var user = %s;" % json.dumps(self.response['data'])
            else:
                return "var user = false;"
        
    def getMime(self):
        return self.mime 
        
    def executeGet(self):
        if "json" in self.waEnviron["parameters"]:
            self.mime = "application/json"
            self.jsonResponse = True
            
        user = self.waEnviron['user']
        self.setData(user.getJSON())
        self.setMessage("Authentication is not enabled. Since no one is the admin, you will do it")
            
class waUserUnauthorized(resource.waResource):
    def executeGet(self):
        self.setException("Sorry, you are not authorized to execute this request.")
            
