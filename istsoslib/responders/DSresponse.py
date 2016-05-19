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
import string
import os
import os.path
import sys

from istsoslib import sosException


class DescribeSensorResponse:
    """Responer for the DescribeSensor request

    Attributes:
        smlFile: sensorML of this sensor
        procedureType: type of sensor
        stime (str): start time of this sensor
        etime (str): end time of this sensor
        observedProperties (list): the list of observed properties of this sensor

            .. note::
                observedProperties is a list of rows as:
                ["def_opr", "name_opr", "desc_opr", "constr_pro", "name_uom"]

    """
    def __init__(self, filter, pgdb):
        
        pgdb.setTimeTZ("UTC")
        self.version = filter.version
    
        self.smlFile = ""
        sql = "SELECT id_prc, stime_prc, etime_prc, name_oty from %s.procedures, %s.obs_type" %(filter.sosConfig.schema,filter.sosConfig.schema)
        sql += " WHERE id_oty=id_oty_fk AND name_prc = %s" 
        params = (str(filter.procedure),)
        try:
            res=pgdb.select(sql,params)
        except:
            raise Exception("Error! sql: %s." %(pgdb.mogrify(sql,params)) )
        
        # raise error if the procedure is not found in db
        if res==None:
            raise sosException.SOSException("InvalidParameterValue","procedure","Procedure '%s' not exist or can't be found.")
        
        
        # look for observation end time
        try:
            self.procedureType = res[0]['name_oty']
        except:
            self.procedureType = None
            
        
        if self.procedureType == 'virtual':
            vpFolder = os.path.join(filter.sosConfig.virtual_processes_folder,filter.procedure)
            try:
                sys.path.append(vpFolder)
            except:
                raise Exception("Error in loading virtual procedure path")
                
            # check if python file exist
            if os.path.isfile("%s/%s.py" % (vpFolder,filter.procedure)):
                
                #import procedure process
                exec "import %s as vproc" %(filter.procedure)
                
                # Initialization of virtual procedure will load the source data
                vp = vproc.istvp()
                vp._configure(filter,pgdb)
                
                self.stime, self.etime = vp.getSampligTime()
                
            else:
                self.stime = None
                self.etime = None
        
        else:
            # look for observation start time
            try:
                self.stime = res[0]['stime_prc']
            except:
                self.stime = None
                #raise sosException.SOSException(1,"Procedure '%s' has no valid stime."%(filter.procedure))
            
            # look for observation end time
            try:
                self.etime = res[0]['etime_prc']
            except:
                self.etime = None
            
        
        # check if folder containing SensorML exists
        if not os.path.isdir(filter.sosConfig.sensorMLpath):
            raise Exception("istsos configuration error, cannot find sensorMLpath!")
        
        # clean up the procedure name to produce a valid file name
        filename = filter.procedure
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        for c in filename:
            if not c in valid_chars:
                raise Exception("procedure name '%s' is not a valid: use only letters or digits!"%(filter.procedure))
        filename += '.xml'
        
        self.smlFile = os.path.join(filter.sosConfig.sensorMLpath, filename)
        # check if file exist                
        if not os.path.isfile(self.smlFile):
            raise Exception("SensorML file for procedure '%s' not found!" % (filter.procedure))
        
        sqlProc  = "SELECT def_opr, name_opr, desc_opr, constr_pro, name_uom, id_pro"
        sqlProc += " FROM %s.observed_properties opr, %s.proc_obs po," %(filter.sosConfig.schema,filter.sosConfig.schema)
        sqlProc += " %s.procedures pr, %s.uoms um" %(filter.sosConfig.schema,filter.sosConfig.schema)
        sqlProc += " WHERE opr.id_opr=po.id_opr_fk AND pr.id_prc=po.id_prc_fk AND um.id_uom = po.id_uom_fk"
        sqlProc += " AND name_prc = %s ORDER BY id_pro" 
        params = (str(filter.procedure),)
        try:
            self.observedProperties = pgdb.select(sqlProc, params)
        except Exception as exe:
            raise Exception("Error! %s\n > sql: %s." % (str(exe), pgdb.mogrify(sqlProc, params)))
        
        
