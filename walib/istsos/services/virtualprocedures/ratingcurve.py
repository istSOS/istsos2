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
import os


# istsos/services/test/virtualprocedures/Q_TEST/ratingcurves
class waRatingcurves(waResourceService):
    """
    class to handle SOS rating curve for virtual procedure of type HQ
    called with a request to istsos/services/{serviceName}/virtualprocedures/{procedurename}/ratingcurve

    list of ordered dictionary of rating-curve parameters:
        [
         {
          "A": "5.781",
          "B": "0.25",
          "C": "1.358",
          "K": "0",
          "from": "1982-01-01T00:00+00:00",
          "to": "1983-01-01T00:00+00:00",
          "low_val": "0",
          "up_val": "1000"
         },
         {...},{...},...
        ]
    """

    def __init__(self, waEnviron):
        waResourceService.__init__(self, waEnviron)
        self.servicename = self.pathinfo[2]
        self.procedurename = self.pathinfo[4]
        self.procedureFolder = os.path.join(self.servicepath,
                                                "virtual", self.procedurename)
        self.RCfilename = os.path.join(self.procedureFolder,
                                                self.procedurename + ".rcv")

    def executeGet(self):
        #filename = self.RCpath + "/" + self.RCprocedure + ".dat"
        if not os.path.isfile(self.RCfilename):
            raise Exception("Rating-curve parameters of procedure <%s> not set" % self.procedurename)

        RClist = RCload(self.RCfilename)
        self.setData(RClist)
        self.setMessage("Rating-curve parameters of procedure <%s> successfully retrived" % self.procedurename)

    def executePost(self):
        """
        Method for executing a POST requests that create a new SOS observed property

        """
        if not os.path.exists(self.procedureFolder):
            raise Exception("Virtual procedure <%s> not set" % self.procedurename)
            #os.makedirs(self.procedureFolder)
        if os.path.isfile(self.RCfilename):
            old_json = RCload(self.RCfilename)
        else:
            old_json = {}

        if RCsave(self.json, self.RCfilename):
            self.setMessage("Rating-curve parameters of procedure <%s> successfully saved" % self.procedurename)

        # log changes to db
        #print "flag: ", self.serviceconf.getobservation['transactional_log']
        if self.serviceconf.getobservation['transactional_log']:
            self.__logToDB(old_json)

    def executeDelete(self):
        if os.path.isfile(self.RCfilename):
            os.remove(self.RCfilename)
        else:
            raise Exception("Rating-curve parameters of procedure <%s> not set" % self.procedurename)

    def __logToDB(self, old_json):
        # read old values
        from walib import databaseManager
        import datetime
        import copy

        # get new data
        new_json = copy.deepcopy(self.json)

        if old_json == new_json:
            return

        result = self.__check_changes(old_json, new_json)

        now = datetime.datetime.now()

        servicedb = databaseManager.PgDB(
                self.serviceconf.connection['user'],
                self.serviceconf.connection['password'],
                self.serviceconf.connection['dbname'],
                self.serviceconf.connection['host'],
                self.serviceconf.connection['port'])

        for res in result:

            count = 0
            sql = "INSERT INTO %s.tran_log(transaction_time_trl, " % self.service
            sql += "operation_trl, procedure_trl, begin_trl, end_trl, count) "
            sql += "VALUES (%s, %s, %s, %s, %s, %s)"

            params = (now, "RatingCurve", self.procedurename, res['from'],)
            params += (res['to'], count)

            servicedb.execute(sql, params)

    def __check_equals(self, old, new):
        for var in ['A', 'B', 'C', 'K', 'up_val', 'low_val']:
            if float(old[var]) != float(new[var]):
                return False
        return True

    def __get_old_intervals(self, old, new, last_element):
        """
            Some magic!

            old: array of intervals
            new: new interval
        """
        from copy import deepcopy

        result = []

        nfrom = new['from']
        nto = new['to']

        for interval in old:

            ofrom = interval['from']
            oto = interval['to']

            if oto < nfrom or nto < ofrom:
                continue

            # if old == new
            # old  |---------------|
            # new  |---------------|
            if nfrom == ofrom and nto == oto:
                tmp = deepcopy(interval)
                result.append(tmp)
            # old |----|
            # new |--|
            # new  |-|
            # new  |---|
            elif nfrom >= ofrom and nto <= oto:
                tmp = deepcopy(interval)
                tmp['from'] = nfrom
                tmp['to'] = nto
                result.append(tmp)
            # if new between 2 old intervals
            # old   |------|
            # new |----|
            # ret   |--|
            elif nfrom < ofrom and nto > ofrom and nto <= oto:
                tmp = deepcopy(interval)
                tmp['to'] = nto
                result.append(tmp)
            elif (nfrom >= ofrom and nfrom < oto) and nto > oto:
                tmp = deepcopy(interval)
                tmp['from'] = nfrom
                result.append(tmp)

        return result

    def __check_changes(self, old, new):
        from copy import deepcopy
        from dateutil.parser import parse

        for elem in old:
            elem['from'] = parse(elem['from']).replace(hour=0, tzinfo=None)
            elem['to'] = parse(elem['to']).replace(hour=0, tzinfo=None)

        for elem in new:
            elem['from'] = parse(elem['from']).replace(hour=0, tzinfo=None)
            elem['to'] = parse(elem['to']).replace(hour=0, tzinfo=None)

        # if no old curve -> new
        if len(old) == 0:
            return new

        myresult = []

        for new_elem in new:
            change_elem = self.__get_old_intervals(old, new_elem, True)

            #print change_elem

            if len(change_elem) == 0:
                myresult.append(new_elem)
                continue

            for old_elem in change_elem:
                if not self.__check_equals(new_elem, old_elem):
                    tmp = deepcopy(new_elem)
                    tmp['from'] = old_elem['from']
                    tmp['to'] = old_elem['to']
                    myresult.append(tmp)

        return myresult


def RCload(filename):
    #load HQ virtual procedure conf file to a list of dictionaries
    cvlist = []
    with open(filename) as f:
        lines = f.readlines()
        items = [i.strip().split("|") for i in lines if i.strip() != ""]
        fields = items[0]
        for i in range(1, len(items)):
            cvdict = {}
            for f, field in enumerate(fields):
                cvdict[field] = items[i][f]
            cvlist.append(cvdict)
    return cvlist


def RCsave(cvlist, filename):

    lines = []
    header = ['from', 'to', 'low_val', 'up_val', 'A', 'B', 'C', 'K']
    #check cvlist validity and save to HQ virtual procedure conf file
    for item in cvlist:
        try:
            if not item["from"] < item["to"]:
                raise Exception, 'Error: <from> %s not before of <to> %s' %(item["from"],item["to"])
            line = [item[h] for h in header]
            lines.append(line)
        except Exception as e:
            raise Exception("Error: invalid HQ parameter list; %s" % str(e))

    lines.sort()
    for i in range(1, len(lines)):
        if lines[i][0] == lines[i - 1][0] and lines[i][1] == lines[i - 1][1]:
            if not lines[i][2] == lines[i - 1][3]:
                raise Exception, 'Error: series of HQ curve same period multilevel wrong; check <from> %s' %(lines[i][0])
        elif not lines[i][0] == lines[i - 1][1]:
            raise Exception, 'Error: series of HQ curve not continue; check <from> %s' %(lines[i][0])

    with open(filename, 'w') as f:
        f.write("|".join(header) + "\n")
        for line in lines:
            f.write("|".join(line) + "\n")

    return True
"""
from|to|low_val|up_val|A|B|C|K
1982-
"""

