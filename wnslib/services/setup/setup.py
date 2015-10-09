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
from os import path
from walib import databaseManager
import config

from wnslib.operation import wnsOperation
from wnslib import sqlschema


class wnsSetup(wnsOperation):
    """
        Class to setup the notification system
    """

    def __init__(self, wnsEnviron):
        wnsOperation.__init__(self, wnsEnviron)

    def executeGet(self):
        """ execute GET request

            create notification.aps file
            create database schema
        """
        services_dir = config.wns_path
        aps_dir = path.join(services_dir, "notifications.aps")

        #print "Service path: ", services_dir

        import datetime
        now = datetime.datetime.now()
        startDate = now.strftime('%Y-%m-%d %H:%M:%S')

        aps = open(aps_dir, 'w')
        aps.write("### CREATED ON " + str(startDate) + " ###")
        aps.close()

        if not self.serviceconf.connectionWns['dbname']:
            #Copy connection params to connectionWns
            self.serviceconf.put('connectionWns', 'dbname',
                                self.serviceconf.connection['dbname'])
            self.serviceconf.put('connectionWns', 'host',
                                self.serviceconf.connection['host'])
            self.serviceconf.put('connectionWns', 'user',
                                self.serviceconf.connection['user'])
            self.serviceconf.put('connectionWns', 'password',
                                self.serviceconf.connection['password'])
            self.serviceconf.put('connectionWns', 'port',
                                self.serviceconf.connection['port'])
            self.serviceconf.save()

        dbConnection = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        dbConnection.execute(sqlschema.wnsschema)

        msg = "Notification.aps file created in %s " % services_dir
        msg += "\nDatabase schema WNS correctly created"

        self.setMessage(msg)
