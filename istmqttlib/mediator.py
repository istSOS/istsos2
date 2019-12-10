# -*- coding: utf-8 -*-
# =============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2010 - 2017 IST-SUPSI (www.supsi.ch/ist)
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
import isodate as iso
import istmqttlib

try:
    str = str
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    bytes = bytes
    str = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    bytes = str
    str = str

"""
Usage example with paho mqtt client (https://eclipse.org/paho):

code::

    import istmqttlib
    m = istmqttlib.MQTTMediator()
    import paho.mqtt.client as mqtt


    def paho_client(url, port, istSos):

        def on_message(client, userdata, msg):
            istSos.insert_observation(url, port, msg.topic, msg.payload)

        def on_connect(mqttc, obj, flags, rc):
            client.subscribe("#")

        client = mqtt.Client(clean_session=True)
        client.on_message = on_message
        client.on_connect = on_connect

        client.connect(url, int(port), 60)
        client.loop_forever()

    m.start(paho_client)


Usage example with HBMQTT mqtt client (https://github.com/beerfactory/hbmqtt)

code::

    from hbmqtt import client
    import asyncio
    import istmqttlib


    def hbmqtt_client(url, port, istSos):
        print ("Starting hbmqtt_client..")

        C = client.MQTTClient()

        @asyncio.coroutine
        def uptime_coro():
            print ("Starting uptime_coro..")
            yield from C.connect('mqtt://%s:%s' % (url, port))
            # Subscribe to 'istsos/t_lugano' with QOS=1
            # Subscribe to 'istsos/p_lugano' with QOS=2
            yield from C.subscribe([
                ('istsos/t_lugano', 1),
                ('istsos/p_lugano', 2),
            ])
            try:
                while True:
                    message = yield from C.deliver_message()
                    packet = message.publish_packet
                    istSos.insert_observation(
                        url, port,
                        packet.variable_header.topic_name,
                        str(packet.payload.data.decode("utf-8")))

                    print("%s => %s" % (
                        packet.variable_header.topic_name,
                        str(packet.payload.data)))

                print ("unsubscribe..")
                yield from C.unsubscribe(
                    ['istsos/t_lugano', 'istsos/p_lugano'])
                print ("disconnect..")
                yield from C.disconnect()

            except client.ClientException as ce:
                print("Client exception: %s" % ce)

        asyncio.get_event_loop().run_until_complete(uptime_coro())


    m = istmqttlib.MQTTMediator()
    m.start(hbmqtt_client)

"""


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
                SELECT id_prc, mqtt_prc, name_prc FROM %s.procedures""" % (
                instance['service']))

            for row in rows:
                if row[1] is not None and row[1] != '':
                    mqttConf = json.loads(row[1])
                    if 'broker_port' in mqttConf and (
                            mqttConf['broker_port'] is not None
                            and mqttConf['broker_port'] != ''):
                        broker_url = "%s:%s" % (
                            mqttConf['broker_url'],
                            mqttConf['broker_port'])

                    else:
                        broker_url = "%s:1883" % (
                            mqttConf['broker_url'])

                    topic = mqttConf['broker_topic']
                    if broker_url not in self.broker:
                        self.broker[broker_url] = {}

                    self.broker[broker_url][topic] = {
                        "id": row[0],
                        "name": row[2],
                        "instance": instance['service']
                    }

    def insert_observation(self, broker_url, port, topic, data):
        print(("url: %s:%s, topic: %s, data: %s" % (
            broker_url, port, topic, data)))
        with self.lock:
            broker = "%s:%s" % (broker_url, port)
            if (broker in self.broker) and (topic in self.broker[broker]):
                id_prc = self.broker[broker][topic]['id']
                name_prc = self.broker[broker][topic]['name']
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
                        #print (type(data))
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

                        # Publish / broadcast new data
                        mqttConf = self.services[instance]['config'].mqtt
                        print ("mqttConf: ")
                        print (mqttConf)
                        if mqttConf["broker_url"] != '' and (
                                mqttConf["broker_port"] != ''):
                            print ("Broadcasting new data!!")
                            istmqttlib.PahoPublisher({
                                "broker_url": mqttConf["broker_url"],
                                "broker_port": mqttConf["broker_port"],
                                "broker_topic": "%s%s" % (
                                    mqttConf["broker_topic"],
                                    name_prc),
                                "data": data
                            }).start()

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
        print ("Ciao")
        print((self.broker))
        for key in list(self.broker.keys()):
            urlPort = key.split(":")
            self.threads.append(
                threading.Thread(
                    target=target, args=(urlPort[0], urlPort[1], self)))

        for thread in self.threads:
            try:
                thread.run()
            except Exception as e:
                print((str(e)))

    def stop(self):
        while len(self.threads) > 0:
            thread = self.threads.pop()
            del thread
