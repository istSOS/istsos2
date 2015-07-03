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
import sys
import copy


def initResource(wnsEnviron):
    path = wnsEnviron['path']
    print >> sys.stderr, path

    print >> sys.stderr, wnsEnviron['pathinfo']
    pathinfo = copy.deepcopy(wnsEnviron['pathinfo'])
    pathinfo.pop(0)
    resource = pathinfo.pop(0)

    print >> sys.stderr, pathinfo
    print >> sys.stderr, resource

    if resource == 'user':
        if len(pathinfo) <= 1:
            from wnslib.services.users import users
            return users.wnsUsers(wnsEnviron)
        else:
            pathinfo.pop(0)
            resource = pathinfo.pop(0)
            if resource == 'notification' and len(pathinfo) <= 1:
                from wnslib.services.registrations import registrations
                return registrations.wnsRegistrations(wnsEnviron)
            else:
                raise Exception("Resource is not identified, check the URL")

    elif resource == 'notification':
        print >> sys.stderr, "Notifcation request"
        if len(pathinfo) <= 1:
            from wnslib.services.notifications import notifications
            return notifications.wnsNotifications(wnsEnviron)
        else:
            raise Exception("Resource is not identified, check the URL")
    elif resource == 'setup':
        from wnslib import setup
        return setup.wnsSetup(wnsEnviron)
    else:
        raise Exception("Resource is not identified, check the URL")
