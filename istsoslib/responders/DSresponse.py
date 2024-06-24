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
import importlib
from istsoslib import sosException, sosDatabase


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
                vproc = importlib.import_module(filter.procedure)
                # exec("import %s as vproc" %(filter.procedure))

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
        filename += '.xml'

        self.smlFile = os.path.join(filter.sosConfig.sensorMLpath, 'well.xml')
        # check if file exist                
        if not os.path.isfile(self.smlFile):
            raise Exception("SensorML file for procedure '%s' not found!" % (filter.procedure))

        # TODO:
        #   IGRAC specified
        sqlProc = "SELECT * FROM istsos.observed_properties_sensor WHERE name_prc = %s"
        params = (str(filter.procedure),)
        try:
            self.observedProperties = pgdb.select(sqlProc, params)
        except Exception as exe:
            raise Exception("Error! %s\n > sql: %s." % (str(exe), pgdb.mogrify(sqlProc, params)))

        # SPECIFICALLY FOR IGRAC SENSOR
        fields = [
            'longitude', 'photo', 'latitude', 'elevation_value', 'elevation_unit',
            'original_id', 'ggis_uid', 'name', 'id', 'country', 'license',
            'restriction_code_type', 'constraints_other', 'organisation',
            'manager', 'aquifer_name', 'aquifer_material', 'aquifer_type',
            'aquifer_thickness', 'confinement'
        ]

        sqlProc = f"SELECT {','.join(fields)} from {filter.sosConfig.schema}.vw_istsos_sensor WHERE original_id='{filter.procedure}' LIMIT 1 "

        # Get the data of licenses
        gdb = None
        if os.environ.get("GEONODE_DATABASE", None):
            gdb = sosDatabase.PgDB(
                os.environ["GEONODE_DATABASE_USER"],
                os.environ["GEONODE_DATABASE_PASSWORD"],
                os.environ["GEONODE_DATABASE"],
                os.environ["GEONODE_DATABASE_HOST"],
                os.environ["GEONODE_DATABASE_PORT"]
            )

        try:
            results = pgdb.select(sqlProc, params)
            if not results:
                raise Exception("Sensor does not exist.")

            self.sensorProperties = []
            for result in results:
                row = {}
                for idx, field in enumerate(fields):
                    row[field] = result[idx]
                    if gdb:
                        if field == 'license' and row[field]:
                            licenses = gdb.select(
                                f'SELECT name, description, abbreviation from base_license where id={row[field]}',
                                {}
                            )
                            try:
                                license = licenses[0]
                                if result['organisation']:
                                    row['summary'] = f'This data was made available by {result["organisation"]} under the {license[2]} license.'
                                row[field] = license[0]
                                row['license_desc'] = license[1]
                            except IndexError:
                                row[field] = ''
                        elif field == 'restriction_code_type' and row[field]:
                            codes = gdb.select(
                                f'SELECT identifier, description from base_restrictioncodetype where id={row[field]}',
                                {}
                            )
                            try:
                                code = codes[0]
                                row[field] = code[0]
                                row['restriction_code_type_desc'] = code[1]
                            except IndexError:
                                row[field] = ''
                print(row)
                self.sensorProperties.append(row)
        except Exception as exe:
            raise Exception("Error! %s\n > sql: %s." % (
            str(exe), pgdb.mogrify(sqlProc, params)))
