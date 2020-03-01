.. _ws_insertobservation:

===================
Insert observations
===================

For this part of the tutorial you should use ASCII files with sensor data
formatted according to **text/csv;subtype=istSOS**. This format is a CSV
represented by a header as the first line containing the URI names of
the observed properties, the following lines contains the data.

**Example: T_LUGANO_20141231234000000.dat**

.. code-block:: csv

    urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature
    2015-01-01T00:10:00.000000+0100,0.446000
    2015-01-01T00:20:00.000000+0100,0.862000
    2015-01-01T00:30:00.000000+0100,0.932000
    2015-01-01T00:40:00.000000+0100,0.384000

.. note::

    Pay attention to the file name: there is a timestamp (YYYYMMDDhhmmssfff in
    GMT+0:00). This parameter is used as the endPosition in the sampling time
    of a procedure. This is particularly important when the procedure is
    an irregular time series.

    Think about tipping bucket rain gauge, when there isn’t rain no data are
    sent. But updating the endPosition we will be able to know that the sensor
    is working and that there is no rain, instead of thinking that the sensor
    is not transmitting or that it is broken.

Uploading CSV files
-------------------

In the data directory of this workshop there is folder named “dataset”.
There are some examples of CSV datafiles in the "**text/csv;subtype=istSOS**"
format:

- BELLINZONA_20150603125000.dat
- GRABOW_201505272100000.dat
- LOCARNO_201506031200000.dat
- P_LUGANO_20150603142000000.dat
- RH_GNOSCA_20150603142000000.dat
- T_LUGANO_20150603142000000.dat

**Loading CSV data**

Open a Shell and execute the followings commands:

If installed from source:

.. code-block:: bash

    cd /usr/local/istsos

If installed from debian package

.. code-block:: bash

    cd /usr/share/istsos

Then launch the import script:

.. code-block:: bash

    python scripts/csv2istsos.py -p BELLINZONA LOCARNO P_LUGANO T_LUGANO GRABOW RH_GNOSCA \
    -u http://localhost/istsos -s demo \
    -w ~/Desktop/Tutorial/dataset

.. note::

    The “csv2istsos.py“ file, is a python script that makes use of the WA-REST
    eatures of istSOS to insert observations.

    .. code-block:: bash

        python scripts/csv2istsos.py --help

Loading data with OGC-SOS InsertObservation request
---------------------------------------------------

Even if we have used the csv2istsos script to facilitate the data loading,
users may also use the SOS insertObservation request directly. For example,
a valid request for loading a single observation to the service is:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <sos:InsertObservation
        xmlns:gml="http://www.opengis.net/gml"
        xmlns:om="http://www.opengis.net/om/1.0"
        xmlns:sos="http://www.opengis.net/sos/1.0"
        xmlns:swe="http://www.opengis.net/swe"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        service="SOS"
        version="1.0.0">
        <sos:AssignedSensorId>f10b70b2561111e5a35e0800278295cb</sos:AssignedSensorId>
        <sos:ForceInsert>true</sos:ForceInsert>
        <om:Observation>
            <om:procedure xlink:href="urn:ogc:def:procedure:x-istsos:1.0:LOCARNO"/>
            <om:samplingTime>
                <gml:TimePeriod>
                    <gml:beginPosition>2015-06-03T14:10:00+02</gml:beginPosition>
                    <gml:endPosition>2015-06-03T14:50:00+02</gml:endPosition>
                </gml:TimePeriod>
            </om:samplingTime>
            <om:observedProperty>
                <swe:CompositePhenomenon dimension="5">
                    <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"/>
                    <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"/>
                    <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall:qualityIndex"/>
                    <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature"/>
                    <swe:component xlink:href="urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex"/>
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
                                    <swe:uom code="°C"/>
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
                    </swe:encoding> <swe:values>2015-06-03T14:10:00+02,0,200,20.4,200@2015-06-03T14:20:00+02,0.1,200,19.5,200@2015-06-03T14:30:00+02,0.1,200,19.1,200@2015-06-03T14:40:00+02,0,200,19.5,200@2015-06-03T14:50:00+02,0,200,20.6,200</swe:values>
                </swe:DataArray>
            </om:result>
        </om:Observation>
    </sos:InsertObservation>

**Let’s insert observations using the XML format:**

1. Download a tool like `Postman <https://www.postman.com/>`_
2. Choose the “POST” option
3. Insert this URL for the demo instance: http://localhost/istsos/demo
4. Copy and paste the InsertObservation xml in the body tab

.. warning::

    Pay attention to the AssignedSensorId parameter: this according to the
    standard is returned by the system only when the sensor is registered.
    To access it, you can use administration interface, looking at the
    procedure metadata details.

5. Press “Send”
