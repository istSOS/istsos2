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
'''
This script should be used to manage user authentication and authorization
'''

import sys
import os
from os import path
import hashlib
import pprint
try:
  import cPickle as pic
except ImportError:
  try:
    import pickle as pic
  except ImportError:
    print >> sys.stderr, ("Failed to import pickle from any known place")
sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e

pp = pprint.PrettyPrinter(indent=4)
passwordFile = path.join(path.abspath("."), "services", "istsos.passwd")

def get_users():
    with open(passwordFile, 'rb') as f:
        return pic.load(f)

def execute (args, conf=None):
    
    remove = False
    if 'r' in args:
        remove = args['r']
    
    ll = False
    if 'l' in args:
        ll = args['l']
        
    role = None
    if 'role' in args and args['role'] != None:
        if args['role'] not in ['a', 'admin', 'n', 'networkmanager', 'd', 'datamanager', 'v', 'viewer']:
            print ("You ca choose role between: admin (or a), networkmanager (or n), datamanager (or d), viewer (or v).\nAdd -h for help")
            return
        elif args['role'] in ['a', 'n', 'd', 'v']:
            rd = {
                'a', 'admin',
                'n', 'networkmanager',
                'd', 'datamanager',
                'v', 'viewer'
            }
            role = rd[args['role']]
        else:
            role = args['role']
    
    if remove:
        if not 'user' in args or args['user'] == None:
            print ("To remove a user, the user name must be provided.\nAdd -h for help")
            return
        elif not path.isfile(passwordFile):
            print "User file not exist"
        
        user = args['user']
        users = get_users()
        
        if role:
        
            if not role in users[user]['roles']:
                print "User '%s' does not have role %s" % (user, role)
                
            del users[user]['roles'][role]
            with open(passwordFile, 'w+') as f:
                pic.dump(users, f)
                
        else:
            if user in users.keys():
                del users[user]
                
                with open(passwordFile, 'w+') as f:
                    pic.dump(users, f)
                    
            else:
                print "User '%s' does not exists" % user
            
        return
        
            
    elif ll:
        if not path.isfile(passwordFile):
            print "User file not exist"
        users = get_users()
        pp.pprint(users) 
        '''for user in users.keys():
            print user'''
               
    elif 'password' in args and args['password'] != None:
    
        if not 'user' in args or args['user'] == None:
            print ("To add or update a user the username must be defined.\nAdd -h for help")
            return
        if not 'password' in args or args['password'] == None:
            print ("To add or update a user a password must be defined.\nAdd -h for help")
            return
        
        # checking if file exist. If it does not exist a new one will be 
        # created with default admin user (admin:istsos)
        if not path.isfile(passwordFile):
            with open(passwordFile, 'w+') as f:
                users = {
                    "admin": {
                        "password": "%s" % (hashlib.md5("istsos").hexdigest()),
                        "roles": {
                            "admin": {
                                "*": ["*"]
                            }
                        }
                    }
                }
                pic.dump(users, f)
        
        user = args['user']
        password = args['password']
        
        with open(passwordFile, 'rb') as f:
            users = pic.load(f)
            if user in users.keys():
                users[user]["password"] = hashlib.md5(password).hexdigest()
            else:
                users[user] = {
                    "password": "%s" % (hashlib.md5(password).hexdigest()),
                    "roles": {}
                }
            
        with open(passwordFile, 'w+') as f:
            pic.dump(users, f)
            
    if role:
        if not 'user' in args or args['user'] == None:
            print ("To add or update an user's role the username must be defined.\nAdd -h for help")
            return
            
        elif not path.isfile(passwordFile):
            print "Users file not exist"
        
        user = args['user']
        service = args['service']
        procedures = args['procedures']
        users = get_users()
        
        if user in users.keys():
            if not role in users[user]['roles']:
                users[user]['roles'][role] = {}
            users[user]['roles'][role][service] = procedures
            with open(passwordFile, 'w+') as f:
                pic.dump(users, f)
        else:
            print "User not exists in file, to create the user set also the password.\nAdd -h for help"
            
    
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""
Use this script to manage user authentication and authorization     
    """)
    
    parser.add_argument('-r',
        action = 'store_true',
        dest   = 'r',
        help   = 'Remove the user')
        
    parser.add_argument('-l',
        action = 'store_true',
        dest   = 'l',
        help   = 'List users')
    
    parser.add_argument('-user',
        action = 'store',
        dest   = 'user',
        metavar= 'user name',
        help   = 'The user name to add or remove')
        
    parser.add_argument('-password',
        action = 'store',
        dest   = 'password',
        metavar= 'password',
        help   = 'Password for new user or update existing')
        
    parser.add_argument('-role',
        action = 'store',
        dest   = 'role',
        metavar= 'role name',
        help   = '''Add a role to the given user, options: admin (or a), networkmanager (or n), datamanager (or d), viewer (or v).
        Mandatory params: -user, -role, -service (optional, default *), -procedure (optional, default *)''')
        
    parser.add_argument('-s',
        action = 'store',
        dest   = 'service',
        default= '*',
        metavar= 'services name',
        help   = 'Add accessible service to a user role, options: "admin", "datamanager", "viewer", default: "%(default)s"')
        
    parser.add_argument('-p',
        action = 'store',
        dest   = 'procedures',
        nargs  = '+',
        default= '*',
        metavar= 'procedures name',
        help   = 'Define which procedure can be accessed, default: "%(default)s"')
        
    
        
    args = parser.parse_args()
    execute(args.__dict__)
