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
from walib import configManager

import config

defaultCFGpath = path.join(config.services_path, "default.cfg")
serviceconf = configManager.waServiceConfig(defaultCFGpath)


def notify(name, message, status=True):
    """Notify manager

    check users subscription and raise notification

    Args:
        name (str):        name of the notification
        message (dict):     dictionary with message to notify
        status (bool):     if True update status on twitter
    """
    from walib import databaseManager as dbm
    from wnslib import notify

    dbConnection = dbm.PgDB(
            serviceconf.connectionWns['user'],
            serviceconf.connectionWns['password'],
            serviceconf.connectionWns['dbname'],
            serviceconf.connectionWns['host'],
            serviceconf.connectionWns['port'])

    sql = """SELECT r.user_id_fk, r.not_list
            FROM wns.registration r, wns.notification n
            WHERE r.not_id_fk = n.id AND n.name=%s"""
    params = (name,)

    usersList = dbConnection.select(sql, params)
    notifier = notify.Notify(serviceconf)

    if status:
        try:
            notifier.post_twitter_status(message['twitter']['public'], name)
        except AttributeError as e:
            # missing or wrong autentiation data
            print e

    for user in usersList:
        sql = "SELECT * FROM wns.user WHERE id = %s"
        par = [user['user_id_fk']]
        contact = dict(dbConnection.select(sql, par)[0])

        for con in user['not_list']:

            if con == 'alert':
                notifier.alert(message['alert'], name)

            if con == 'mail' or con == 'email':
                if 'mail' in message.keys():
                    notifier.email(message['mail'], contact['email'])

            elif con == 'twitter':
                if 'twitter' in message.keys() and 'twitter' in contact.keys():
                    notifier.twitter(message['twitter']['private'],
                                                contact['twitter'], name)
                else:
                    print "Please define a Twitter id"

            elif con == "ftp":
                if "ftp" in message.keys() and "ftp" in contact.keys():
                    import json
                    notifier.ftp(json.loads(contact['ftp']), message['ftp'])

            elif con == 'fax':
                notifier.fax(message, contact['fax'], name)

            elif con == 'sms':
                notifier.sms(message, contact['tel'], name)
