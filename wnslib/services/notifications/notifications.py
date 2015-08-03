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


class wnsNotifications(wnsOperation):
    """ Class to manage notification

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

        get notification
        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        if self.not_id:
            sql = "SELECT * FROM wns.notification WHERE id=%s;"
            params = (self.not_id,)
        else:
            sql = "SELECT * FROM wns.notification"
            params = None

        NotificationList = servicedb.select(sql, params)
        Notification = []

        for notif in NotificationList:
            Notification.append(dict(notif))

        self.setData(Notification)

    def executePost(self):
        """ POST notification

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

        sql = """INSERT INTO wns.notification (name, description)
                        VALUES (%s,%s) RETURNING id;"""
        par = [name, description]
        not_id = servicedb.executeInTransaction(sql, par)[0][0]

        if not not_id:
            self.setException('Exception while creating a new notification')
            return
        try:
            from wnslib import notificationManager as notManager
            if "params" in self.json.keys():
                print "simpleNot"
                params = self.json["params"]
                condition = self.json["condition"]
                service = self.json["service"]
                period = self.json.get("period", None)

                notManager.createSimpleNotification(name, service, params,
                                            condition, interval, period)
            else:
                print  "Notification"
                funcFile = self.json["function"]
                msg = notManager.addNotification(name, funcFile, interval)
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
        self.setMessage(not_id)

    def executePut(self):
        """ PUT notification

        Update a existing notification
        """
        description = self.json.get("description", None)

        from wnslib import notificationManager as notManager

        if description:
            servicedb = databaseManager.PgDB(
                self.serviceconf.connectionWns['user'],
                self.serviceconf.connectionWns['password'],
                self.serviceconf.connectionWns['dbname'],
                self.serviceconf.connectionWns['host'],
                self.serviceconf.connectionWns['port'])

            sql = "UPDATE wns.notification SET description = %s WHERE id=%s;"
            params = (description, self.not_id,)
            servicedb.executeInTransaction(sql, params)

        if not self.json.get("params") or not self.json.get("function"):
            self.setMessage("Updated notifcation description")
            servicedb.commitTransaction()
            return

        try:
            name = self.json["name"]
            interval = self.json["interval"]

            if "params" in self.json.keys():
                print >> sys.stderr, "simpleNot"
                params = self.json["params"]
                condition = self.json["condition"]
                service = self.json["service"]
                period = self.json.get("period", None)

                notManager.createSimpleNotification(name, service, params,
                                            condition, interval, period)
            else:
                print >> sys.stderr, "Notification"
                funcFile = self.json["function"]
                msg = notManager.addNotification(name, funcFile, interval)
                if msg:
                    self.setException(msg)
                    if description:
                        servicedb.rollbackTransaction()
                    return
            if description:
                servicedb.commitTransaction()
            # Delete old notification function
            notManager.delNotification(name)

        except Exception, e:
            msg = "The following error occoured: " + str(e)
            msg += "\n\nPlease try again"
            if description:
                servicedb.rollbackTransaction()
            self.setException(msg)
            return

        self.setMessage("Notification updated")

    def executeDelete(self):
        """DELETE notification

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
                self.setMessage('OK')
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
