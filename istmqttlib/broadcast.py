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

import threading
import sys


class MQTTPublisher(threading.Thread):
    def __init__(self, conf):
        threading.Thread.__init__(self)
        self.conf = conf
        pass

    def get_url(self):
        return self.conf['broker_url']

    def get_port(self):
        return self.conf['broker_port']

    def get_topic(self):
        return self.conf['broker_topic']

    def get_data(self):
        #print self.conf['data']
        return self.conf['data']

    def run(self):
        print >> sys.stderr, "Run run.. zombie run!"
        pass


class PahoPublisher(MQTTPublisher):
    def run(self):
        import paho.mqtt.publish as publish
        if len(self.get_data()) > 1:
            msgs = []
            for data in self.get_data():
                msgs.append(
                    (self.get_topic(), ",".join(data), 0, True)
                )

            publish.multiple(
                msgs,
                hostname=self.get_url(),
                port=self.get_port()
            )

        elif len(self.get_data()) == 1:
            publish.single(
                topic=self.get_topic(),
                payload=",".join(self.get_data()[0]),
                retain=True,
                hostname=self.get_url(),
                port=self.get_port())
