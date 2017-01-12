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
Add this files to configure basic authentication in Apache2

    <Location /istsos>
            AuthType Basic
            AuthName "Welcome to istSOS"
            AuthBasicProvider wsgi
            WSGIAuthUserScript /usr/local/istsos/auth.py
            Require valid-user
    </Location>

"""
import sys
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

pp = pprint.PrettyPrinter(indent=4)
istsosPasswd = path.join(path.dirname(path.abspath(__file__)), "services", "istsos.passwd")

if not path.isfile(istsosPasswd):
    with open(istsosPasswd, 'w+') as f:
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

def check_password(environ, user, password):
    #print >> sys.stderr, "\nCheck_password: %s" % pp.pformat(environ)
    #return True
    with open(istsosPasswd, 'rb') as f:
        users = pic.load(f)
        if user in users.keys():
            if hashlib.md5(password).hexdigest() == users[user]["password"]:
                return True
            return False
        return None
    

