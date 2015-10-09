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

import psycopg2


class wnsRegistrations(wnsOperation):
    """
        Class to manage user subscription to notification

        Attributes:
            user_id (int): user id
            notification (int): notification id
    """

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
        """GET registration

        get user subscription to notifications

        Returns:
            A dict containing all user subscription to notification.
            Example:
            {
                user_id:[
                    {
                        "not_id": 1,
                        "not_list": [
                            "email", "twitter"
                        ],
                        "description": "notification description",
                        "name": "notification name"
                    }
                ]
            }
        """
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
        RegistrationsList = []

        for el in NotificationList:
            el = dict(el)
            del el['not_id_fk']
            del el['user_id_fk']

            RegistrationsList.append(dict(el))

        self.setMessage("Notification subscription for user: " + self.user_id)
        self.setData(RegistrationsList)

    def executePost(self):
        """ POST registrations

        subscribe a user to a notification

        Return confirm message if subscribed
        """
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

        if not self.check_data(not_list):
            return

        if self.user_id and self.notification:

            # Check notification type
            for noti in not_list:
                if noti == "mail" or noti == "email":
                    if not self.serviceconf.mail['usermail']:
                        self.setException("Cannot subscribe via email")
                        return
                if noti == "twitter":
                    if not self.serviceconf.twitter['consumer_key']:
                        self.setException("Cannot subscribe via twitter")
                        return

            sql = """INSERT INTO wns.registration (user_id_fk, not_id_fk,
                            not_list) VALUES (%s,%s, %s);"""
            par = [self.user_id, self.notification, not_list]

            try:
                servicedb.execute(sql, par)
            except psycopg2.Error as e:
                self.setException(e.pgerror)
                return

            message = 'User ' + self.user_id + ' subscribed to notification '
            message += str(self.notification)
            self.setMessage(message)
        else:
            self.setException("Please define user and notification")

    def executePut(self):
        """ PUT registration

            Update user subscription to notification
        """
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

        if not self.check_data(not_list):
            return

        if self.user_id and self.notification:

            # Check notification type
            for noti in not_list:
                if noti == "mail" or noti == "email":
                    if not self.serviceconf.mail['usermail']:
                        self.setException("Cannot subscribe via email")
                        return
                if noti == "twitter":
                    if not self.serviceconf.twitter['consumer_key']:
                        self.setException("Cannot subscribe via twitter")

            sql = """UPDATE wns.registration SET not_list=%s
                     WHERE user_id_fk=%s AND not_id_fk=%s;"""
            par = [not_list, self.user_id, self.notification]
            try:
                servicedb.execute(sql, par)
            except psycopg2.Error as e:
                self.setException(e.pgerror)
                return

            self.setMessage('Update subscription')

        else:
            self.setException("Please defien user and notification")

    def executeDelete(self):
        """ DELETE subscription
            delete user from notification alert
        """
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
            try:
                servicedb.execute(sql, par)
            except psycopg2.Error as e:
                self.setException(e.pgerror)
                return

            message = "User" + self.user_id
            message += ' unsubscribed from notification ' + self.notification

            self.setMessage(message)
        else:
            self.setException('Please define a user_id and a notification_id')

    def check_data(self, data):
        """
            Method to check subscription

            Check if a user can receive notification via mail or twitter

        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        sql = "SELECT * FROM wns.user WHERE id = %s"
        params = (self.user_id,)

        try:
            user = servicedb.execute(sql, params)[0]
        except psycopg2.Error as e:
            self.setException(e.pgerror)
            return False

        for tmp in data:

            if tmp == "mail" or tmp == "email":
                if not user['email']:
                    self.setException("User can't receive notification via mail")
                    return False

            if tmp == "twitter" and not user["twitter"]:
                self.setException("User cann't receive notification via twitter")
                return False

        return True
