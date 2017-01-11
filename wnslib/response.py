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
import json
from os import path
from walib import configManager
from walib import databaseManager

import datetime
import time
from lib.pytz import timezone


class Response(object):
    """
        Class used to store a notifcation result

        Attributes:
            serviceconf (obj): service configuration object
            __message (dict): dictionary response
    """

    __message = {
        "date": "",
        "notifcation": None,
        "response": {}
    }

    def __init__(self):
        """

        """
        defaultCFGpath = path.join(path.dirname(path.split(
                        path.abspath(__file__))[0]), "services/default.cfg")
        self.serviceconf = configManager.waServiceConfig(defaultCFGpath)
        now = datetime.datetime.now().replace(tzinfo=timezone(time.tzname[0]))
        self.__setDate(now)

    def setResponse(self, result):
        """
            set response message

            Args:
                result (str/dict): response message, if could be a string or a python dict
        """
        self.__message['response'] = result

    def setNotification(self, not_name):
        """
            set notification name

            Args:
                not_name (str): notification name
        """
        self.__message['notification'] = not_name

    def __setDate(self, date):
        """
            set date

            Args:
                date (str): date in isoformat
        """
        self.__message['date'] = date

    def writeToFile(self):
        file_name = self.__path + "/" + self.__message['notification'] + "_"
        file_name += self.__message['date']
        with open(file_name, 'w') as outfile:
            json.dump(self.__message, outfile)

    def writeToDB(self):
        """
            Write notification to database
        """
        servicedb = databaseManager.PgDB(
            self.serviceconf.connectionWns['user'],
            self.serviceconf.connectionWns['password'],
            self.serviceconf.connectionWns['dbname'],
            self.serviceconf.connectionWns['host'],
            self.serviceconf.connectionWns['port'])

        if not self.__message['notification']:
            raise ValueError('missing notification name')
        # get notification_id
        sql = "SELECT id FROM wns.notification WHERE name=%s"
        params = (self.__message['notification'],)

        not_id = servicedb.execute(sql, params)[0]
        not_id = not_id[0]

        print "Save " + self.__message['notification'] + " notification result"

        sql = "INSERT INTO wns.responses(not_id, date, notification, response)"
        sql += " VALUES (%s, %s, %s, %s)"

        params = (not_id, self.__message['date'],
                    self.__message['notification'],
                    json.dumps(self.__message['response']))
        # write notification to db
        servicedb.execute(sql, params)
