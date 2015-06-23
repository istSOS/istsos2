.. _insert:

==============================
Insertion of new observations
==============================

You can add observation to the service using the SOS request insert oservation or using the Python script *csv2istsos.py* provided with the software.

Loading CSV data with *csv2istsos.py*
===================================

Using this script you should prepare ASCII files with sensor data formatted according to *text/csv;subtype=istSOS*. 
This format is a CSV represented by a header as the first line containing the URI names of the observed properties, the following lines contains the data.

Example: PROCEDURENAME_YYYYMMDDhhmmss.dat

.. code-block:: rest
    
    urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature
    2013-01-01T00:10:00.000000+0100,0.446000
    2013-01-01T00:20:00.000000+0100,0.862000
    2013-01-01T00:30:00.000000+0100,0.932000
    2013-01-01T00:40:00.000000+0100,0.384000

.. note::
    
    Pay attention to the file name: there is a timestamp (YYYYMMDDhhmmss GMT+0:00). This parameter is used to force the endPosition in the sampling time of a procedure. This is particularly important when the procedure is an irregular time series.

    Think of tipping bucket rain gauge, when there is no rain no data are sent. But updating the endPosition we will be able to know that the sensor is working and that there is no rain, instead of thinking that the sensor is not transmitting or that it is broken.

To load the prepared CSV you should run the *csv2istsos.py* command which is under the script folder of your installation location (e.g.: /usr/local/istsos)

.. note::
    
    The “csv2istsos.py“ file, is a python script that makes use of the WA-REST features of istSOS to insert observations.
    
    .. code-block:: rest

        python scripts/csv2istsos.py --help

        usage: csv2istsos.py [-h] [-v] [-t] -p procedures [procedures ...]
                             [-q quality index] [-u url] -s service 
                             -w working directory [-e file extension] 
                             [-usr user name] [-pwd password]

        Import data from a csv file.

        optional arguments:
          -h, --help            Show this help message and exit
          -v, --verbose         Activate verbose debug
          -t, --test            Use to test the command, deactivating the insert
                                observation operations.
          -p procedures [procedures ...]
                                List of procedures to be aggregated.
          -q quality index      The quality index to set for all the measures of 
                                the CSV file, if not set into the CSV. 
                                (default: 100).
          -u url                IstSOS Server address IP (or domain name) used for 
                                all request. (default: http://localhost:80/istsos).
          -s service            The name of the service instance.
          -w working directory  Working directory where the csv files are located.
          -e file extension     Extension of the CSV file. (default: .dat)
          -usr user name
          -pwd password


.. rubric:: *Example*

For loading all the CSV files in the folder *~/Desktop/dataset* referring to the sensor T_LUGANO of the SOS service named *demo* at the URL http://localhost/istsos

.. code-block:: rest
    
    python scripts/csv2istsos.py -p T_LUGANO \
    -u http://localhost/istsos -s demo \
    -w ~/Desktop/dataset 


Loading data with OGC-SOS InsertObservation request 
====================================================

Even if you can use the *csv2istsos.py* script to facilitate the data loading, users may also use the SOS *insertObservation* request directly. 

To execute the XML request from the interface:

    1. **Open the requests test page:** `<http://localhost/istsos/admin/requests>`_
    2. **Select the desired service instance**
    3. **Choose the “POST” option**
    4. **Paste into the field the InsertObservation xml**
    5. **Press “Send”**

.. note::
    Pay attention to the AssignedSensorId parameter: this according to the standard is returned by the system only when the sensor is registered. To access it, you can use administration interface, looking at the procedure metadata details.

.. rubric:: *Example*

For example, a valid request for loading observations to a procedure named *LOCARNO* which is observing rainfall and temperature for the time inteval 2014-06-03T15:08:00Z/2014-06-03T15:48:00Z and specifying the respective qualityIndex for each measure, the request is:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <sos:InsertObservation 
      xmlns:gml="http://www.opengis.net/gml" 
      xmlns:om="http://www.opengis.net/om/1.0" 
      xmlns:sos="http://www.opengis.net/sos/1.0" 
      xmlns:swe="http://www.opengis.net/swe" 
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
      service="SOS" version="1.0.0">
      <sos:AssignedSensorId>xxxxxxxxxxxxxxxxxxxxxxxxxxx</sos:AssignedSensorId>
      <om:Observation>
        <om:procedure xlink:href="urn:ogc:def:procedure:x-istsos:1.0:LOCARNO"/>
        <om:samplingTime>
            <gml:TimePeriod>
                <gml:beginPosition>2014-06-03T15:08:00Z</gml:beginPosition>
                <gml:endPosition>2014-06-03T15:48:00Z</gml:endPosition>
            </gml:TimePeriod>
        </om:samplingTime>
        <om:observedProperty>
            <swe:CompositePhenomenon dimension="5">
                <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"/>
                <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"/>
                <swe:component
                  xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall:qualityIndex"/>
                <swe:component
                  xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature"/>
                <swe:component
                  xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex"/>
            </swe:CompositePhenomenon>
        </om:observedProperty>
        <om:featureOfInterest xlink:href="urn:ogc:def:feature:x-istsos:1.0:Point:LOCARNO"/>
        <om:result>
            <swe:DataArray>
                <swe:elementCount>
                    <swe:value>5</swe:value>
                </swe:elementCount>
                <swe:elementType name="SimpleDataArray">
                    <swe:DataRecord definition="urn:ogc:def:dataType:x-istsos:1.0:timeSeries">
                        <swe:field name="Time">
                            <swe:Time definition="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"/>
                        </swe:field>
                        <swe:field name="air-rainfall">
                            <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall">
                                <swe:uom code="mm"/>
                            </swe:Quantity>
                        </swe:field>
                        <swe:field name="air-rainfall:qualityIndex">
                            <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall:qualityIndex">
                                <swe:uom code="-"/>
                            </swe:Quantity>
                        </swe:field>
                        <swe:field name="air-temperature">
                            <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature">
                                <swe:uom code="\xc2\xb0C"/>
                            </swe:Quantity>
                        </swe:field>
                        <swe:field name="air-temperature:qualityIndex">
                            <swe:Quantity definition="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex">
                                <swe:uom code="-"/>
                            </swe:Quantity>
                        </swe:field>
                    </swe:DataRecord>
                </swe:elementType>
                <swe:encoding>
                    <swe:TextBlock blockSeparator="@" decimalSeparator="." tokenSeparator=","/>
                </swe:encoding>
                    <swe:values>
                        2014-06-03T14:10:00+0200,0.000000,200,20.000000,200@
                        2014-06-03T14:20:00+0200,0.000000,200,20.100000,200@
                        2014-06-03T14:30:00+0200,0.000000,200,20.200000,200@
                        2014-06-03T14:40:00+0200,0.000000,200,20.500000,200@
                        2014-06-03T14:50:00+0200,0.000000,200,20.500000,200@
                        2014-06-03T15:00:00+0200,0.000000,200,20.400000,200@
                        2014-06-03T15:10:00+0200,0.000000,200,20.400000,200@
                        2014-06-03T15:20:00+0200,0.100000,200,19.600000,200@
                        2014-06-03T15:30:00+0200,0.100000,200,19.100000,200@
                        2014-06-03T15:40:00+0200,0.000000,200,19.000000,200@
                        2014-06-03T15:50:00+0200,0.000000,200,20.600000,200
                    </swe:values>
            </swe:DataArray>
        </om:result>
      </om:Observation>
    </sos:InsertObservation>    


    
    
