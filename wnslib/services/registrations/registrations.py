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
from walib import databaseManager
from wnslib.operation import wnsOperation


class wnsRegistrations(wnsOperation):

    def __init__(self, wnsEnviron):
        wnsOperation.__init__(self, wnsEnviron)
        pathinfo = wnsEnviron['pathinfo']
        print pathinfo
        self.user_id = None
        self.notification = None

        if pathinfo[1] == 'user':
            self.user_id = pathinfo[2]
        else:
            raise Exception("Resource is not identified, check the URL")

        if len(pathinfo) > 4:
            if pathinfo[3] == 'notification':
                self.notification = pathinfo[4]
            else:
                raise Exception("Resource is not identified, check the URL")
        self.setData("")

    def executeGet(self):
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        sql = "SELECT * FROM wns.registration r, wns.notification n "
        sql += "WHERE r.user_id_fk = %s AND r.not_id_fk=n.id"

        params = (self.user_id, )

        if self.notification:
            sql += " AND r.not_id_fk= %s "
            params += (self.notification, )

        NotificationList = servicedb.select(sql, params)
        RegistrationsList = {}

        for el in NotificationList:
            el = dict(el)
            del el['id']
            user_id = el['user_id_fk']
            del el['user_id_fk']
            if not(user_id in RegistrationsList):
                RegistrationsList[user_id] = [dict(el)]
            else:
                RegistrationsList[user_id].append(dict(el))

        self.setData(RegistrationsList)

    def executePost(self):
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        not_list = self.json['data']

        if len(not_list) == 0:
            self.setException('Please add a notification type')
            return

        if self.user_id and self.notification:
            sql = """INSERT INTO wns.registration (user_id_fk, not_id_fk,
                            not_list) VALUES (%s,%s, %s);"""
            par = [self.user_id, self.notification, not_list]

            servicedb.execute(sql, par)
            self.setMessage('OK')
            return
        else:
            self.setException("Please defien user and notification")

    def executePut(self):
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        not_list = self.json['data']

        if len(not_list) == 0:
            self.setException('Please add a notification type')
            return

        if self.user_id and self.notification:
            sql = """UPDATE wns.registration SET not_list=%s
                     WHERE user_id_fk=%s AND not_id_fk=%s;"""
            par = [not_list, self.user_id, self.notification]
            servicedb.execute(sql, par)
            self.setMessage('OK')
            return
        else:
            self.setException("Please defien user and notification")

    def executeDelete(self):
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        if self.user_id and self.notification:
            sql = """DELETE FROM wns.registration
                    WHERE user_id_fk = %s AND not_id_fk = %s;"""
            par = [self.user_id, self.notification]
            servicedb.execute(sql, par)
            self.setMessage('OK')
        else:
            self.setException('Please define a user_id and a notification_id')
