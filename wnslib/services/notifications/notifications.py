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
from wnslib.operation import wnsOperation
from walib import databaseManager
import sys
import psycopg2


class wnsNotifications(wnsOperation):
    """
    Class to manage notification

    Attributes:
        not_id (int): notification id

    """

    def __init__(self, wnsEnviron):
        wnsOperation.__init__(self, wnsEnviron)
        self.not_id = None
        if len(wnsEnviron['pathinfo']) > 2:
            self.not_id = wnsEnviron['pathinfo'][2]
            print self.not_id
        self.setData("")

    def executeGet(self):
        """ GET request

            get notification request handler

            return list of notification
        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        sql = "SELECT * FROM wns.notification "
        params = None

        if self.not_id:
            sql += " WHERE id=%s;"
            params = (self.not_id,)

        NotificationList = servicedb.select(sql, params)

        Notification = []

        for notif in NotificationList:
            Notification.append(dict(notif))

        self.setData(Notification)
        self.setMessage("fount [" + str(len(Notification)) + "] notifications")

    def executePost(self):
        """ POST notification

            post notifation request handler
            create new notifcation, simple or complex
        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        name = self.json["name"]
        description = self.json["description"]
        interval = self.json["interval"]
        not_id = None
        store = self.json.get("store", False)

        sql = """INSERT INTO wns.notification (name, description,
                        interval, store) VALUES (%s,%s, %s, %s) RETURNING id;"""
        par = [name, description, interval, store]
        try:
            not_id = servicedb.executeInTransaction(sql, par)[0][0]
        except psycopg2.Error as e:
            self.setException(e.pgerror)
            servicedb.rollbackTransaction()
            return

        if not not_id:
            self.setException('Exception while creating a new notification')
            return
        try:
            from wnslib import notificationManager as notManager
            if "params" in self.json.keys():
                params = self.json["params"]
                condition = self.json["condition"]
                service = self.json["service"]
                period = self.json.get("period", None)

                notManager.createSimpleNotification(name, service, params,
                                            condition, interval, period, store)
            else:
                print  "Notification"
                funcFile = self.json["function"]
                msg = notManager.addNotification(name, funcFile,
                                                        interval, store)
                if msg:
                    self.setException(msg)
                    servicedb.rollbackTransaction()
                    return

        except Exception, e:
            msg = "The following error occoured: " + str(e)
            msg += "\n\nPlease try again"
            self.setException(msg)
            servicedb.rollbackTransaction()
            return

        servicedb.commitTransaction()
        self.setMessage(
                    "New notifcation added, notification id: " + str(not_id))

    def executePut(self):
        """ PUT notification

            Put notification request handler

            Update a existing notification
        """
        description = self.json.get("description", None)
        interval = self.json.get("interval", None)

        from wnslib import notificationManager as notManager
        servicedb = databaseManager.PgDB(
                self.serviceconf.connectionWns['user'],
                self.serviceconf.connectionWns['password'],
                self.serviceconf.connectionWns['dbname'],
                self.serviceconf.connectionWns['host'],
                self.serviceconf.connectionWns['port'])

        if description:

            sql = "UPDATE wns.notification SET description = %s "
            params = (description,)

            sql += " WHERE id=%s RETURNING *"
            params += (self.not_id,)

            try:
                row = servicedb.executeInTransaction(sql, params)
            except psycopg2.Error as e:
                self.setException(e.pgerror)
                servicedb.rollbackTransaction()
                return
        else:
            sql = "SELECT * FROM wns.notification WHERE id=%s"
            params = (self.not_id,)

            try:
                row = servicedb.executeInTransaction(sql, params)
            except psycopg2.Error as e:
                self.setException(e.pgerror)
                servicedb.rollbackTransaction()
                return

        if not self.json.get("params") and not self.json.get("function"):
            self.setMessage("Updated notifcation description")
            servicedb.commitTransaction()
            return

        if self.json.get('params') and self.json.get('function'):
            self.setException("What?!?!")
            servicedb.rollbackTransaction()
            return

        try:
            interval = self.json.get("interval", row[0][3])
            name = row[0][1]
            store = self.json.get("store", row[0][4])

            # Delete old notification function
            notManager.delNotification(name)

            if "params" in self.json.keys():
                print >> sys.stderr, "simpleNot"
                params = self.json["params"]
                condition = self.json["condition"]
                service = self.json["service"]
                period = self.json.get("period", None)

                notManager.createSimpleNotification(name, service, params,
                                            condition, interval, period, store)
            else:
                print >> sys.stderr, "Notification"
                function_path = self.json["function"]
                msg = notManager.addNotification(name, function_path,
                                                        interval, store)

                if msg:
                    self.setException(msg)
                    if description:
                        servicedb.rollbackTransaction()
                    return

            if description:
                servicedb.commitTransaction()
            else:
                sql = "UPDATE wns.notification SET interval = %s, store = %s"
                sql += " WHERE id=%s"

                params = (interval, store, self.not_id)

                try:
                    servicedb.executeInTransaction(sql, params)
                except psycopg2.Error as e:
                    self.setException(e.pgerror)
                    servicedb.rollbackTransaction()

                servicedb.commitTransaction()

        except Exception, e:
            msg = "The following error occoured: " + str(e)
            msg += "\n\nPlease try again"
            if description:
                servicedb.rollbackTransaction()
            self.setException(msg)
            return

        self.setMessage("Notification " + name + " updated")

    def executeDelete(self):
        """DELETE notification

            delete notification request handler
            delete selected notification
        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        sql = "DELETE FROM wns.notification WHERE id = %s RETURNING name;"
        par = [self.not_id]
        notname = None
        notname = servicedb.executeInTransaction(sql, par)[0][0]

        try:
            from wnslib import notificationManager as notManager
            if notname:
                notManager.delNotification(notname)
                servicedb.commitTransaction()
                self.setMessage('Notifcation ' + notname + ' deleted')
            else:
                servicedb.rollbackTransaction()
                self.setException("Canno't delete the notifcation")
                return
        except Exception, e:
            msg = "The following error occoured: " + str(e)
            msg += "\n\nPlease try again"
            servicedb.rollbackTransaction()
            self.setException(msg)
            return
