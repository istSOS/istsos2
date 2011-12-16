# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2011 Massimiliano Cannata, Milan Antonovic
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sys, pprint
from walibs.waError import waError
#import simplejson
import json
import pprint
import isodate as iso

class qualityCheck:
    """Base class for quality check.
    
    self.db - db connection object
    self.procedure - procedure name,
    self.procID - procedure ID
    self.obspr - observed property name
    self.obsprID  - observed property ID
    
    """
        
    def __init__(self,pgdb,proc,obspr,schema,debug=False):
        """ set quality check object.
        
        Args:
            pgdb (str):  connection object.
            proc (str): procedure name (full urn)
            obspr (st): observed property name (full urn)
        
        Kwargs:
            timeint ((str,str)): time interval limits (from,to) in ISO8601 format (use None for infinite).
        """        
        self.pgdb = pgdb
        self.procedure = proc
        self.obspr = obspr
        self.schema = schema
        self.debug = debug
        
        #--SET procedure ID
        sql  = "SELECT id_prc FROM %s.procedures" %(self.schema)
        sql += " WHERE name_prc=%s"
        par = [self.procedure]
        try:
            self.procID = self.pgdb.select(sql,tuple(par))[0]['id_prc']
        except Exception as e:
            if self.debug==True:
                raise waError.waException(1001,lang='EN',mesg=self.pgdb.mogrify(sql,tuple(par)))
            else:
                raise waError.waException(1001,lang='EN',mesg="procID")
        
        #--SET observed property ID
        sql  = "SELECT id_opr FROM %s.observed_properties" %(self.schema)
        sql += " WHERE name_opr=%s"
        par = [self.obspr]
        try:
            self.obsprID = self.pgdb.select(sql,tuple(par))[0]['id_opr']
        except Exception as e:
            if self.debug==True:
                raise waError.waException(1001,lang='EN',mesg=self.pgdb.mogrify(sql,tuple(par)))
            else:
                raise waError.waException(1001,lang='EN',mesg="obsprID")
    
    
    def executeQC_IN(self,lb,ub,qcode=210,timeint=(None,None),commit=True):
        """ apply  quality check for level 0 (is within control).
        
        Args:
            pgdb (str):  connection object.
            proc (str): procedure name (full urn)
            obspr (st): observed property name (full urn)
            lb (int,float): lower bound of check interval (excluded)
            ub (int,float): upper bound of check interval (excluded)
        
        Kwargs:
           timeint ((str,str)): time interval limits (from,to) in ISO8601 format (use None for infinite).
        
        """
        
        #-- CHECK QUALITY CODE
        sql  = "SELECT name_qi,desc_qi,id_qi FROM %s.quality_index" %(self.schema)
        sql += " WHERE id_qi = %s"
        par = [qcode]
        try:
            code = self.pgdb.select(sql,tuple(par))[0]
        except Exception as e:
            if self.debug==True:
                raise waError.waException(1001,lang='EN',mesg=("%s -- MSG:%s") %(self.pgdb.mogrify(sql,tuple(par)),"QUALITY INDEX NOT AVAILABLE"))
            else:
                raise waError.waException(1001,lang='EN',mesg="quality index")
        
        #-- PREPARE SQL STATEMENT        
        sql  = "UPDATE %s.measures m" %(self.schema)
        sql += " SET id_qi_fk=%s"
        sql += " FROM %s.procedures p,%s.event_time t,%s.observed_properties o" %( (self.schema,)*3 )
        sql += " WHERE m.val_msr>=%s and m.val_msr<%s"
        # where observed property ID
        sql += " AND m.id_opr_fk=%s" 
        # where procedure ID
        sql += " AND t.id_prc_fk=%s"
        # where quality index is lower
        sql += " AND m.id_qi_fk<%s"
        # where time is in interval ]xx,xx[
        par = [qcode,lb,ub,self.obsprID,self.procID,qcode]
        if not timeint==(None,None):
            sql += " AND m.id_eti_fk=t.id_eti"
        if not timeint[0]==None:
            sql += " AND t.time_eti > %s"
            par.append(iso.parse_datetime(timeint[0]))
        if not timeint[1]==None:
            sql += " AND t.time_eti < %s"
            par.append(iso.parse_datetime(timeint[1]))
        sql += " RETURNING m.id_msr,t.time_eti"
        #--EXECUTE QUERY UPDATE
        try:
            result = self.pgdb.executeInThread(sql,tuple(par))
        except Exception as e:
            if self.debug==True:
                raise waError.waException(1001,lang='EN',mesg=("%s -- MSG:%s") %(self.pgdb.mogrify(sql,tuple(par)),e) )
            else:
                raise waError.waException(1001,lang='EN',mesg="obsprID")
        
        if commit==False:
            self.pgdb.rollbackThread()
        else:
            self.pgdb.commitThread()
        
        return result
        


    
