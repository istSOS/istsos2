# istSOS Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
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


import psycopg2 # @TODO the right library
import psycopg2.extras
import os

import sosConfig
from istSOS import sosDatabase
#from SOS.config import mimetype
from istSOS import sosException

class DescribeSensorResponse:
    def __init__(self, filter, pgdb):
        self.smlFile = ""
        sql = "SELECT id_prc from %s.procedures Where name_prc = '%s'" %(sosConfig.schema,filter.procedure)
        try:
            res=pgdb.select(sql)
            # Check if process exist
            if len(res)==1:
                # check if folder containing SensorML exists
                if not os.path.isdir(sosConfig.sensorMLpath):
                    raise sosException.SOSException(1,"istSOS configuration error, cannot find sensorMLpath!")
                # check if sensorMLpath ends with slash "/"
                path = sosConfig.sensorMLpath
                if path[-1] != '/':
                    path += '/'
                self.smlFile = path+filter.procedure+".xml"
                # check if file exist                
                if not os.path.isfile(self.smlFile):
                    raise sosException.SOSException(1,"SensorML file for procedure '%s' not found!"%(filter.procedure))
            else:
                raise sosException.SOSException(1,"Error! Procedure '%s' not exist or can't be found.")
        except:
            raise sosException.SOSException(1,"Procedure '%s' not exist or can't be found."%(filter.procedure))
       
       
       
       
       
       
       
