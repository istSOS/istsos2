#!/usr/bin/env python

import string
import sys
import os.path

import psycopg2


def _get_sosconfig_info():
    """ Get hold of the sosConfig.py file and retrieve the name of the SensorML
        folder from it.
    """
    # Assume the utilities path is a sibling of the service path.
    # We want to get hold of the path to the sos service, to import information from
    # the sosconfig file.
    file_path = os.path.split(os.path.abspath(__file__))[0]
    parent_path = os.path.sep.join(file_path.split(os.path.sep)[:-1])
    service_path = os.path.join(parent_path, 'service')

    # add the path to the sos service to the current path
    sys.path.insert(0, service_path)

    result = {}

    # import the sosConfig module and retrieve the necessary information from it
    try:
        sosconfig = __import__('sosConfig')
        result['connection'] = sosconfig.connection
        result['schema'] = sosconfig.schema
        result['sensorMLpath'] = sosconfig.sensorMLpath 
        result['authority'] = sosconfig.authority
        result['version'] = sosconfig.version

    except ImportError:
        print "Could not load sosConfig module"
        return None

    return result


def _create_sensorML_doc(config, proc_sensors):
    """ Create the sensorML doc for the procedure.
    """
    filename = proc_sensors[0]['name_prc']
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars)
    filename += '.xml'

    full_filename = os.path.join(config['sensorMLpath'], filename)
    of = open(full_filename, 'wt')

    of.write("""\
<SensorML xmlns:sml="http://www.opengis.net/sensorML/1.0.1"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:swe="http://www.opengis.net/swe/1.0.1"
  xmlns:gml="http://www.opengis.net/gml"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:dlm="http://www.ist.supsi.ch/dataloggerMD/1.0"
  xsi:schemaLocation="http://www.opengis.net/sensorML/1.0.1 http://schemas.opengis.net/sensorML/1.0.1/sensorML.xsd"
      version="1.0.1">
<member xlink:arcrole="urn:ogc:def:process:OGC:detector">""")

    of.write("""\
    <System>
            <gml:name>%s</gml:name>
            <keywords>
                <KeywordList codeSpace="urn:%s:def:keywords">
                    <keyword>insitu</keyword>
                </KeywordList>
            </keywords>
            <identification>
                <IdentifierList>
                    <identifier name="longName">
                        <Term definition="urn:ogc:def:property:OGC:longName">
                            <value>NULL</value>
                        </Term>
                    </identifier>
                    <identifier name="modelNumber">
                        <Term definition="urn:ogc:def:property:OGC:modelNumber">
                            <value>NULL</value>
                        </Term>
                    </identifier>
                    <identifier name="manufacturer">
                        <Term definition="urn:ogc:def:property:OGC:manufacturer">
                            <value>NULL</value>
                        </Term>
                    </identifier>
                </IdentifierList>
            </identification>
            <classification>
                <ClassifierList>
                    <classifier name="Intended Application">
                        <Term definition="urn:ogc:def:classifier:OGC:application">
                            <value>NULL</value>
                        </Term>
                    </classifier>
                </ClassifierList>
            </classification>
            <components>
                <ComponentList>
                    <component name="%s">
                        <Component gml:id="%s">
                            <identification>
                                <IdentifierList>
                                    <identifier name="longName">
                                        <Term definition="urn:ogc:def:property:OGC:longName">
                                            <value>%s</value>
                                        </Term>
                                    </identifier>
                                </IdentifierList>
                            </identification>
                            <inputs>
                                <InputList>
                            """ % (proc_sensors[0]['name_prc'], 
                                   config['authority'],
                                   proc_sensors[0]['name_prc'],
                                   proc_sensors[0]['assignedid_prc'], 
                                   proc_sensors[0]['name_prc']))
 
    for sensor in proc_sensors:
        of.write("""<input name="%s">
                        <swe:ObservableProperty definition="urn:ogc:def:parameter:%s:%s:meteo::%s"/>
                    </input>""" % (sensor['name_opr'], 
                                   config['authority'],
                                   config['version'],
                                   sensor['desc_opr']))

    of.write("""\
                </InputList>
            </inputs>
            <outputs>
                <OutputList>""")

    for sensor in proc_sensors:
        of.write("""<output name="%s">
                        <swe:Quantity definition="urn:ogc:def:parameter:%s:%s:meteo::%s">
                            <swe:uom code="%s"/>
                        </swe:Quantity>
                    </output>""" % (sensor['name_opr'], 
                                    config['authority'],
                                    config['version'],
                                    sensor['desc_opr'], 
                                    sensor['name_uom']))

    of.write("""                </OutputList>
                            </outputs>
                            <method xlink:href="urn:ogc:def:process:1.0:detector"/>
                        </Component>
                    </component>
                </ComponentList>
            </components>            
        </System>
    </member>
</SensorML>
""") 
    of.close()


def _get_and_create_sensorML(config):
    """ Retrieve the available information regarding procedures from the sos
        database.
        For each procedure, create a sensorML file.
    """
    # create and open the connection
    conn_str = "dbname='%s' user='%s' host='%s' password='%s' port=%d" % ( \
            config['connection']['dbname'],
            config['connection']['user'],
            config['connection']['host'],
            config['connection']['password'],
            int(config['connection']['port'])
            )
    cn = psycopg2.connect(conn_str)
    
    # create a cursor and the query to retrieve the procedure and sensor info
    cr = cn.cursor()
    sql = """\
            SELECT 
              offerings.name_off, 
              offerings.desc_off, 
              procedures.name_prc, 
              time_res_unit.name_tru, 
              procedures.time_res_prc, 
              procedures.assignedid_prc, 
              observed_properties.name_opr, 
              observed_properties.desc_opr, 
              uoms.name_uom, 
              uoms.desc_uom, 
              foi.name_foi, 
              foi.desc_foi, 
              feature_type.name_fty, 
              foi.geom_foi, 
              obs_type.name_oty, 
              obs_type.desc_oty
            FROM 
              %s.offerings, 
              %s.off_proc, 
              %s.procedures, 
              %s.foi, 
              %s.uoms, 
              %s.time_res_unit, 
              %s.proc_obs, 
              %s.observed_properties, 
              %s.obs_type, 
              %s.feature_type
            WHERE 
              off_proc.id_prc_fk = procedures.id_prc AND
              off_proc.id_off_fk = offerings.id_off AND
              procedures.id_foi_fk = foi.id_foi AND
              procedures.id_tru_fk = time_res_unit.id_tru AND
              procedures.id_oty_fk = obs_type.id_oty AND
              foi.id_fty_fk = feature_type.id_fty AND
              proc_obs.id_prc_fk = procedures.id_prc AND
              proc_obs.id_uom_fk = uoms.id_uom AND
              proc_obs.id_opr_fk = observed_properties.id_opr
              and offerings.active_off = false
            ORDER BY name_off, name_prc, name_opr;
        """ % ( \
                config['schema'], config['schema'],
                config['schema'], config['schema'],
                config['schema'], config['schema'],
                config['schema'], config['schema'],
                config['schema'], config['schema']
                )
    cr.execute(sql)

    # We are going to collect the sensor info for each procedure, and once we have
    # that, we will create the sensorML document. In this way, we do not to have to
    # build a very large in-memory list of all the procedure and sensor data in the
    # database.

    # Set some control variables
    proc_name = 'zzz' 
    proc_sensors = []

    while 1:
        # get the next sensor record, and check for the end of the data
        proc_list = cr.fetchone()
        if not proc_list:
            break

        if proc_name != proc_list[2]:
            # We have a new procedure, so create the doc for the current one, and
            # reset the sensors list.
            if proc_sensors:
                _create_sensorML_doc(config, proc_sensors)
            proc_sensors = []

        # get the next sensor info for the procedure and add it to the sensor list
        sensor = {}
        sensor['name_off'] = proc_list[0]
        sensor['desc_off'] = proc_list[1]
        sensor['name_prc'] = proc_list[2]
        sensor['name_tru'] = proc_list[3]
        sensor['time_res_prc'] = proc_list[4]
        sensor['assignedid_prc'] = proc_list[5]
        sensor['name_opr'] = proc_list[6]
        sensor['desc_opr'] = proc_list[7]
        sensor['name_uom'] = proc_list[8]
        sensor['desc_uom'] = proc_list[9]
        sensor['name_foi'] = proc_list[10]
        sensor['desc_foi'] = proc_list[11]
        sensor['name_fty'] = proc_list[12]
        sensor['geom_foi'] = proc_list[13]
        sensor['name_oty'] = proc_list[14]
        sensor['desc_oty'] = proc_list[15]
        proc_sensors.append(sensor)

        # set the procedure control varialbe to the current procedure
        proc_name = proc_list[2]

    # we are done
    cr.close()
    cn.close()



def do_main():
    """ Create a SensorML file for each procedure in the istSOS schema of the sos
        database.
    """
    # Step 1: collect path information
    config = _get_sosconfig_info()

    # Step 2: collect procedure information and write out the files
    if config is not None:
        _get_and_create_sensorML(config)



if __name__ == '__main__':
    do_main()
