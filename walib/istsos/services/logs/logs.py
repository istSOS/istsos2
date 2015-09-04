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
from walib.resource import waResourceService
from walib import databaseManager


class waLogs(waResourceService):

    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)
        self.setData("")
        pathinfo = waEnviron['pathinfo']

        self.logs_id = None
        if pathinfo[-1] != 'logs':
            self.logs_id = pathinfo[-1]

    def executeGet(self):
        """
        Method for executing a GET requests

        Request:
            (...)/istsos/wa/istsos/services/<service name>/logs/?message=TypeError
                                                        &element=T_TREVANO
                                                        &stime=2013-01-01T00:08:00.000000%2B0100
                                                        &etime=2013-01-01T00:11:00.000000%2B0100
                                                        &process=acquisition
        The response is:
        {
                 [
                    {
                        "process": "acquisition",
                        "element": "T_TREVANO",
                        "datetime": "2013-01-01T00:10:00.000000+0100",
                        "message": "TypeError",
                        "details": "Error parsing line 200",
                        "status": "pending"
                    },
                    {
                        "process": "...",
                        "element": "...",
                        "datetime": "...",
                        "message": "...",
                        "details": "...",
                        "status": "verified"
                    }
                ]
            }
        """
        if self.service == "default":
            raise Exception("logs operation can not be done for default service instance.")

        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])

        if self.logs_id:
            sql = "SELECT * FROM %s.cron_log " % (self.service)
            sql += " WHERE id_clo= %s"
            par = (self.logs_id,)
            exceptions = servicedb.select(sql, par)
        else:
            exceptions = self.search_with_params(servicedb)

        data = []
        for exc in exceptions:
            data.append(
                    {
                        "process": exc['process_clo'],
                        "element": exc['element_clo'],
                        "datetime": str(exc['datetime_clo']),
                        "message": exc['message_clo'],
                        "details": exc['details_clo'],
                        "status": exc['status_clo'],
                        "id": exc['id_clo']
                    }
            )

        self.setMessage("logs result")
        self.setData(data)

    def executePost(self):
        """
        Method for executing a POST requests that insert a new exception
         {
                "process": "acquisition",
                "element": "T_TREVANO",
                "datetime": "2013-01-01T00:10:00.000000+0100",
                "message": "TypeError",
                "details": "Error parsing line 200"
        }
        """

        if self.service == "default":
            raise Exception("Logs operation can not be done for default service instance.")

        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])

        #TODO: Add a error code to the table?
        #check if exception exist

        # Get procedure id
        sql = "SELECT id_prc FROM %s.procedures WHERE " % self.service
        sql += "name_prc = %s;"
        par = (self.json['element'],)

        procId = servicedb.execute(sql, par)

        if(len(procId) != 1):
            raise Exception("Procedure %s not found." % (self.json['element']))

        sql = "INSERT INTO %s.cron_log(process_clo, element_clo, datetime_clo,message_clo,details_clo,id_prc_fk, status_clo)" % self.service
        sql += " VALUES (%s, %s, %s, %s, %s, %s, %s);"
        par = (self.json['process'], self.json['element'],
                self.json['datetime'], self.json['message'],
                self.json['details'], procId[0][0], 'pending')
        servicedb.execute(sql, par)
        self.setMessage("Added exception")

    def executePut(self):
        """
            Method for executing a PUT requests that update the status of a  exception
            Update a exception status

            {
                "id" : 1,
                "newstatus" : "verified"
            }
        """
        if self.service == "default":
            raise Exception("Logs operation can not be done for default service instance.")

        if self.logs_id == None:
            raise Exception("Please select a valid logs id.")

        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])

        if (self.json['newstatus'] is None):
            raise Exception("Not params.")

        sql = "UPDATE %s.cron_log SET" % self.service
        sql += " status_clo = %s WHERE id_clo = %s"
        par = (self.json['newstatus'], self.logs_id)
        servicedb.execute(sql, par)
        self.setMessage("Status changed")

    def executeDelete(self):
        """
             Method for executing a DELETE requests that remove a exception
            (...)/istsos/wa/istsos/<service name>/logs_id
        """
        if self.service == "default":
            raise Exception("Logs operation can not be done for default service instance.")

        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])

        if self.logs_id is None:
            raise Exception("No exception id specified")

        sql = "DELETE FROM %s.cron_log" % self.service
        sql += " WHERE id_clo = %s"
        par = (self.logs_id,)
        servicedb.execute(sql, par)
        self.setMessage("Exception removed")

    def search_with_params(self, servicedb):
        params = self.waEnviron['parameters']
        par = ()
        sql = """SELECT datetime_clo, * FROM %s.cron_log, %s.procedures """ % (self.service, self.service)
        sql += " WHERE id_prc_fk = id_prc "

        # where
        if not params == None:
            keyList = params.keys()

            if 'message' in keyList:
                sql += " AND ( message_clo = %s) "
                par += (params['message'][0],)

            if 'stime' in keyList:
                sql += " AND  (datetime_clo > %s::timestamptz)"
                par += (params['stime'][0],)

            if 'etime' in keyList:
                sql += " AND  (datetime_clo < %s::timestamptz)"
                par += (params['etime'][0],)

            if 'process' in keyList:
                sql += " AND  (process_clo = %s )"
                par += (params['process'][0],)

            if 'element' in keyList:
                sql += " AND  (element_clo = %s )"
                par += (params['element'][0],)

            if 'status' in keyList:
                if params['status'][0] in ('verified', 'pending'):
                    sql += " AND (status_clo = %s)"
                    par += (params['status'][0],)
                else:
                    raise Exception("Status %s not supported." % params['status'][0])

        # Sort by date
        sql += " ORDER BY datetime_clo DESC;"

        res = servicedb.select(sql, par)
        return res
