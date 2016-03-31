# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# =============================================================================

__author__ = 'Milan Antonovic'
__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__credits__ = []
__license__ = 'GPL2'
__version__ = '1.0'
__maintainer__ = 'Massimiliano Cannata, Milan Antonovic'
__email__ = 'milan.antonovic@gmail.com'

import threading
import os
import sys
import requests
import json
import traceback
import psycopg2
sys.path.insert(0, os.path.abspath("."))
import config
from walib import utils, databaseManager, configManager
from lib import isodate as iso

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    unicode = unicode
    bytes = str
    basestring = basestring


class MQTTMediator():

    def __init__(self, conf=None):
        """ Initialize the MQTTMediator class
        conf
        """
        self.lock = threading.Lock()
        self.conf = conf
        self.broker = {}
        self.services = {}
        defaultCfg = os.path.join(config.services_path, "default.cfg")
        instances = utils.getServiceList(config.services_path, listonly=False)
        for instance in instances:
            sc = configManager.waServiceConfig(defaultCfg, instance['path'])
            conn = databaseManager.PgDB(
                sc.connection["user"],
                sc.connection["password"],
                sc.connection["dbname"],
                sc.connection["host"],
                sc.connection["port"])
            self.services[instance['service']] = {
                "config": sc,
                "conn": conn
            }
            # Get mqtt configurations
            rows = conn.select("""
                SELECT id_prc, mqtt_prc FROM %s.procedures""" % (
                instance['service']))

            for row in rows:
                if row[1] is not None and row[1] != '':
                    mqttConf = json.loads(row[1])
                    if 'port' in mqttConf:
                        broker_url = "%s:%s" % (
                            mqttConf['url'],
                            mqttConf['port'])

                    else:
                        broker_url = "%s:1883" % (
                            mqttConf['url'])

                    topic = mqttConf['topic']
                    if broker_url not in self.broker:
                        self.broker[broker_url] = {}

                    self.broker[broker_url][topic] = {
                        "id": row[0],
                        "instance": instance['service']
                    }

    def insert_observation(self, broker_url, port, topic, data):
        #print("url: %s:%s, topic: %s, data: %s" % (
        #    broker_url, port, topic, data))
        with self.lock:
            broker = "%s:%s" % (broker_url, port)
            if (broker in self.broker) and (topic in self.broker[broker]):
                id_prc = self.broker[broker][topic]['id']
                instance = self.broker[broker][topic]['instance']
                conn = self.services[instance]['conn']
                try:
                    sql = """
                        SELECT
                            procedures.id_prc,
                            proc_obs.id_pro,
                            proc_obs.constr_pro,
                            procedures.stime_prc,
                            procedures.etime_prc
                        FROM
                            %s.procedures,
                            %s.proc_obs
                        WHERE
                            proc_obs.id_prc_fk = procedures.id_prc
                    """ % (instance, instance)
                    sql += """
                      AND
                        id_prc = %s
                      ORDER BY
                        proc_obs.id_pro ASC;
                    """
                    rows = conn.select(sql, (int(id_prc),))

                    if not isinstance(data, list):
                        print (type(data))
                        if isinstance(data, str):
                            data = [data.split(",")]
                        else:
                            data = [data.decode('utf-8').split(",")]

                    # check if procedure observations length is ok
                    if len(rows) != (len(data[0])-1):
                        raise Exception(
                            "Array length missmatch with procedures "
                            "observation number")

                    else:
                        insertEventTime = """
                            INSERT INTO %s.event_time (id_prc_fk, time_eti)
                        """ % (instance)
                        insertEventTime += """
                            VALUES (%s, %s::TIMESTAMPTZ) RETURNING id_eti;
                        """

                        deleteEventTime = """
                            DELETE FROM %s.event_time
                        """ % (instance)
                        deleteEventTime += """
                            WHERE id_prc_fk = %s
                            AND time_eti = %s::TIMESTAMPTZ
                        """

                        insertMeasure = """
                            INSERT INTO %s.measures(id_eti_fk, id_qi_fk,
                                id_pro_fk,val_msr)
                        """ % (instance)
                        insertMeasure += """
                            VALUES (%s, 100, %s, %s);
                        """

                        updateBeginPosition = """
                            UPDATE %s.procedures""" % (instance)
                        updateBeginPosition += """
                            SET stime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s
                        """
                        updateEndPosition = """
                            UPDATE %s.procedures""" % (instance)
                        updateEndPosition += """
                            SET etime_prc=%s::TIMESTAMPTZ WHERE id_prc=%s
                        """

                        bp = rows[0][3]
                        bpu = False
                        ep = rows[0][4]
                        epu = False
                        for observation in data:
                            try:
                                id_eti = conn.executeInTransaction(
                                    insertEventTime, (
                                        rows[0][0], observation[0]))

                            except psycopg2.IntegrityError as ie:
                                conn.rollbackTransaction()
                                conn.executeInTransaction(
                                    deleteEventTime, (
                                        rows[0][0], observation[0]))
                                id_eti = conn.executeInTransaction(
                                    insertEventTime, (
                                        rows[0][0], observation[0]))

                            for idx in range(0, len(rows)):
                                conn.executeInTransaction(
                                    insertMeasure, (
                                        int(id_eti[0][0]),
                                        int(rows[idx][1]),
                                        float(observation[(idx+1)])))

                            if (bp is None) or (bp == '') or (
                                    iso.parse_datetime(observation[0]) < bp):
                                bp = iso.parse_datetime(observation[0])
                                bpu = True

                            if (ep is None) or (ep == '') or (
                                    iso.parse_datetime(observation[0]) > ep):
                                ep = iso.parse_datetime(observation[0])
                                epu = True

                            conn.commitTransaction()

                        if bpu:
                            conn.executeInTransaction(
                                updateBeginPosition, (bp.isoformat(), id_prc))

                        if epu:
                            conn.executeInTransaction(
                                updateEndPosition, (ep.isoformat(), id_prc))

                        conn.commitTransaction()

                except Exception as e:
                    traceback.print_exc(file=sys.stderr)
                    conn.rollbackTransaction()
                    raise Exception(
                        "Error in fast insert (%s): %s" % (type(e), e))

            else:
                #print("Sensor unknown")
                pass

    def start(self, target):
        self.threads = []
        for key in self.broker.keys():
            print ("Adding: %s" % key)
            urlPort = key.split(":")
            print(urlPort)
            self.threads.append(
                threading.Thread(
                    target=target, args=(urlPort[0], urlPort[1], self)))

        for thread in self.threads:
            thread.run()

    def stop(self):
        while len(self.threads) > 0:
            thread = self.threads.pop()
            del thread
