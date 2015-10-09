# -*- coding: utf-8 -*-
from wnslib.operation import wnsOperation
from walib import databaseManager
import json
import psycopg2


class wnsResponses(wnsOperation):
    """

        Class to read stored responses from db and send back to user

        Attributes:
            not_id (int): notification id


    """

    def __init__(self, wnsEnviron):
        """

        """
        wnsOperation.__init__(self, wnsEnviron)
        pathinfo = wnsEnviron['pathinfo']
        self.not_id = None

        if pathinfo[1] == 'response':
            try:
                self.not_id = pathinfo[2]
            except Exception:
                raise Exception("Please define a notification id")
        else:
            raise Exception("Resource is not identified, check the URL")

    def executeGet(self):
        """
            GET request
        """
        params = self.wnsEnviron['parameters']

        servicedb = databaseManager.PgDB(
            self.serviceconf.connection['user'],
            self.serviceconf.connection['password'],
            self.serviceconf.connection['dbname'],
            self.serviceconf.connection['host'],
            self.serviceconf.connection['port'])

        sql = "SELECT * FROM wns.responses WHERE not_id=%s "
        par = (self.not_id,)

        limit = "LIMIT 1"

        if params is not None:
            keyList = params.keys()

            if 'stime' in keyList:
                sql += " AND  (date > %s::timestamptz)"
                par += (params['stime'][0],)

            if 'etime' in keyList:
                sql += " AND  (date < %s::timestamptz)"
                par += (params['etime'][0],)

            if 'limit' in keyList:
                if params['limit'][0] != "all":
                    limit = "LIMIT %s" % params['limit'][0]
                else:
                    limit = ""

        sql += " ORDER BY date DESC "
        sql += limit

        try:
            result = servicedb.execute(sql, par)
        except psycopg2.Error as e:
            self.setException(e.pgerror)
            return

        response = []

        for res in result:
            response.append(
                {
                    "id": res['id'],
                    "notification": res['notification'],
                    "date": res['date'].strftime('%Y-%m-%dT%H:%M:%S%z'),
                    "response": json.loads(res['response'])
                }
            )

        self.setData(response)
        self.setMessage("Found [" + str(len(response)) + "] element")




