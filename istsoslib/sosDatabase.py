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

__author__ = 'Massimiliano Cannata, Milan Antonovic'
__copyright__ = 'Copyright (c) 2016 IST-SUPSI (www.supsi.ch/ist)'
__credits__ = []
__license__ = 'GPL2'
__version__ = '1.0'
__maintainer__ = 'Massimiliano Cannata, Milan Antonovic'
__email__ = 'geoservice@supsi.ch'

import psycopg2
import psycopg2.extras
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


class Database:
    """Connect to a database"""
    user = None
    password = None
    host = None
    dbName = None
    port = None

    def getConnection(self):
        """Return a database connection"""
        return None

    def closeConnection(self):
        """Close a database connection"""
        return None


class PgDB(Database):
    """Connect to a PostgreSQL database"""
    host = None

    def __init__(self, user, password, dbName,
                 host='localhost', port='5432', tz=None):
        "Initialize PostgreSQL connection parameters"
        self.__dns = ""
        if host:
            self.__dns += "host='%s' " % host
        if port:
            self.__dns += "port='%d' " % int(port)
        if dbName:
            self.__dns += "dbname='%s' " % dbName
        if user:
            self.__dns += "user='%s' " % user
        if password:
            self.__dns += "password='%s' " % password
        self.__connect()

    def __connect(self):
        """Connect to a PostgreSQL database"""
        try:
            self.__conn = psycopg2.connect(self.__dns)

        except Exception as e:
            emes = "%s" % e
            if emes.find("CONNECTION ERROR: wrong password") > -1:
                raise Exception("CONNECTION ERROR: wrong password or user")
            elif emes.find("could not translate host") > -1:
                raise Exception("CONNECTION ERROR: wrong host name")
            elif emes.find("database") > -1:
                raise Exception("CONNECTION ERROR: wrong database")
            elif emes.find("connections on port") > -1 or (
                    emes.find("invalid literal for int()") > -1):
                raise Exception("CONNECTION ERROR: wrong port")
            else:
                raise Exception("CONNECTION ERROR: %s" % e)

    def setTimeTZ(self, tz):
        """
        Set the database Time Zone for this connection:

        @param tz: object that define the Time Zone

        .. note::  The input parameter can be af differents types:
            1. A String that can be handled by postgresql (see Time Zone
               at http://www.postgresql.org/docs/current/static/sql-set.html)
            2. An integer, for instance -7. The time zone 7 hours west from
               UTC (equivalent to PDT / -07:00). Positive values are east
               from UTC.
            3. A datetime with timezone information
        """
        import datetime
        offset = "UTC"
        if isinstance(tz, str) or isinstance(tz, int):
            offset = tz
        elif type(tz) == datetime.datetime:
            try:
                o = tz.utcoffset()
                seconds = o.total_seconds()
                offset = seconds / 3600
            except:
                seconds = o.seconds
                if o.days < 0:
                    offset = -1 * ((86400 - seconds) / 3600)
                else:
                    offset = seconds / 3600

        else:
            raise Exception("Time Zone object tz Unknown")

        self.execute("SET SESSION TIME ZONE '%s';" % offset)

    def select(self, sql, par=None):
        """ Execute a select statement"""
        if sql.lstrip()[0:6].lower() == "select":
            cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                cur.execute(sql, par)
            except psycopg2.ProgrammingError as e:
                raise e
            try:
                rows = cur.fetchall()
            except:
                rows = None
            #self.__conn.commit()
            cur.close()
            return rows
        else:
            raise Exception("sql must be a SELECT statement")

    def commitTransaction(self):
        """Commit current transaction"""
        try:
            self.__conn.commit()
        except psycopg2.ProgrammingError as e:
            #print e.message
            raise e
        except Exception as e:
            raise e

    def rollbackTransaction(self):
        """Rollback current transaction"""
        try:
            self.__conn.rollback()
        except psycopg2.ProgrammingError as e:
            print e.message

    def executeInTransaction(self, sql, par=None):
        """Execute an sql statement in an open session"""
        cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(sql, par)
        except psycopg2.ProgrammingError as e:
            print e.message
            self.__conn.rollback()
            raise e
        except Exception as e:
            raise e
        try:
            rows = cur.fetchall()
        except:
            rows = None
        cur.close()
        return rows

    def execute(self, sql, par=None):
        """Execute an sql statement"""
        cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(sql, par)
        except psycopg2.ProgrammingError as e:
            raise e
        try:
            rows = cur.fetchall()
        except:
            rows = None
        self.__conn.commit()
        return rows

    def insertMany(self, sql, dict):
        """Insert many values at once"""
        cur = self.__conn.cursor()
        try:
            cur.executemany(sql, dict)
        except psycopg2.ProgrammingError as e:
            raise e
        self.__conn.commit()
        return

    def insertManyInTransaction(self, sql, dict):
        """Insert many values at once"""
        cur = self.__conn.cursor()
        try:
            cur.executemany(sql, dict)
        except psycopg2.ProgrammingError as e:
            print e.message
            self.__conn.rollback()
            raise e
        try:
            rows = cur.fetchall()
        except:
            rows = None
        return rows

    def mogrify(self, sql, par=None):
        """Mogrify an sql statement (print the actual sql query that
        will be executed)"""
        cur = self.__conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            if par:
                a = cur.mogrify(sql, par)
            else:
                a = cur.mogrify(sql)
        except psycopg2.ProgrammingError as e:
            raise e
        cur.close()
        return a
