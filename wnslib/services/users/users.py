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
import psycopg2


class wnsUsers(wnsOperation):
    """
        Class to manage user

        Attributes:
            userid (int): user id

    """

    def __init__(self, wnsEnviron):
        wnsOperation.__init__(self, wnsEnviron)
        self.userid = None
        if len(wnsEnviron['pathinfo']) > 2:
            self.userid = wnsEnviron['pathinfo'][2]
        self.setData("")

    def executeGet(self):
        """ GET users

        require user information

        return a list with all user
        """
        import json

        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        sql = "SELECT * FROM wns.user "
        params = None

        if self.userid:
            sql += " WHERE id=%s;"
            params = (self.userid,)

        UsersList = servicedb.select(sql, params)

        users = []
        for user in UsersList:
            tmp = dict(user)
            if user['ftp']:
                tmp['ftp'] = json.loads(tmp['ftp'])
            users.append(tmp)

        self.setMessage("found [" + str(len(users)) + "] users")
        self.setData(users)

    def executePost(self):
        """ POST users

            create a new user

        Examples:

            {
                "username" : "username",
                "name": "",
                "surname": "",
                "email": "",
                "twitter": "",
                "tel":"",
                "fax":"",
                "address":"",
                "zip":"",
                "city":"",
                "state":"",
                "country":"",
                "ftp": {
                    "url": "",
                    "user": "",
                    "passwd": ""
                }
            }
        """

        import json as jsonlib

        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        json_data = self.json
        username = json_data["username"]
        email = json_data["email"]
        name = json_data['name']
        surname = json_data['surname']
        # optional value
        tel = json_data.get("tel", None)
        fax = json_data.get("fax", None)
        address = json_data.get("address", None)
        zip_code = json_data.get("zip", None)
        city = json_data.get("city", None)
        state = json_data.get("state", None)
        country = json_data.get("country", None)
        twitter = json_data.get("twitter", None)
        ftp = json_data.get("ftp", None)

        sql = "INSERT INTO wns.user(username,name,surname,email,twitter, "
        sql += "tel, fax, address, zip, city, state, country, ftp)"
        sql += " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s) RETURNING id;"

        params = (username, name, surname, email, twitter, tel, fax, address, )
        params += (zip_code, city, state, country, jsonlib.dumps(ftp))

        try:
            user_id = servicedb.execute(sql, params)[0][0]
        except psycopg2.Error as e:
            self.setException(e.pgerror)
            return

        self.setMessage("New user id: " + str(user_id))

    def executePut(self):
        """ PUT user

        Update a existing user
        """

        import json as jsonlib

        if not self.userid:
            self.setException("No user id defined")
            return

        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        json_data = self.json

        sql = "UPDATE wns.user SET "
        params = ()

        if "ftp" in json_data.keys():
            sql += ""

        for key in json_data.keys():
            if key != "ftp":
                sql += " " + key + "=%s,"
                params += (json_data[key],)
            else:
                sql += " " + key + "=%s,"
                params += (jsonlib.dumps(json_data[key]),)

        sql = sql[:-1]

        sql += " WHERE id=%s;"
        params += (self.userid,)

        try:
            servicedb.execute(sql, params)
        except psycopg2.Error as e:
            self.setException(e.pgerror)
            return

        self.setMessage("Updated user info")

    def executeDelete(self):
        """DELETE user

        delete a users, it automatically unsubscribe from notification
        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        if self.userid:
            sql = "DELETE FROM wns.user WHERE id=%s;"
            par = [self.userid]
            try:
                servicedb.execute(sql, par)
            except psycopg2.Error as e:
                self.setException(e.pgerror)
                return

            self.setMessage('User deleted')
        else:
            self.setException("Please define a user id!!!")
