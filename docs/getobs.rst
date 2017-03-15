.. _getobs:

==================
Get observations
==================

Accessing the data is possible using:
* the SOS Standard requests, 
* WA REST requests or 
* directly using the Data Viewer or Data Editor.

.. image:: images/data_access.png

Using the SOS Standard requests
================================

Here some example of request:


.. rubric:: *Example 1 - filter on procedure, time, property*

Requesting rainfall observations from sensor P_LUGANO between 2013-01-01T00:00:00+01 and 2013-02-4T17:00:00+01

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&
        request=GetObservation&
        offering=temporary&
        procedure=urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO&
        eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&
        observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&
        responseFormat=text/xml;subtype="om/1.0.0"&
        service=SOS&
        version=1.0.0 

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO&eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&responseFormat=text/xml;subtype="om/1.0.0"&service=SOS&>`_
    

.. rubric:: *Example 2 - filter on time, property*

Requesting rainfall observations from all the stations between 2014-06-01T00:00:00+02 and
2014-06-03T00:00:00+02

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&
        request=GetObservation&
        offering=temporary&
        eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&
        observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&
        responseFormat=text/xml;subtype="om/1.0.0"&
        service=SOS&
        version=1.0.0 

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&responseFormat=text/xml;subtype="om/1.0.0"&service=SOS&>`_


.. rubric:: *Example 3 - filter on time, property, area filters*

Requesting rainfall observations from all the stations between 2014-06-01T00:00:00+02 and
2014-06-03T00:00:00+02

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&
        request=GetObservation&
        offering=temporary&
        observedProperty=meteo&
        responseFormat=text/xml;subtype="om/1.0.0"&
        service=SOS&
        version=1.0.0&
        featureOfInterest=<ogc:BBOX>
            <ogc:PropertyName>the_geom</ogc:PropertyName>
            <gml:Box srsName='EPSG:4326'>
                <gml:coordinates>18,4530,55</gml:coordinates></gml:Box>
            </ogc:BBOX>

`[execute above request] <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&observedProperty=meteo&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.1%E2%80%9D&service=SOS&version=1.0.0&featureOfInterest=%3Cogc:BBOX%3E%3Cogc:PropertyName%3Ethe_geom%3C/ogc:PropertyName%3E%3Cgml:Box%20srsName=%27EPSG:4326%27%3E%3Cgml:coordinates%3E18,45%2030,55%3C/gml:coordinates%3E%3C/gml:Box%3E%3C/ogc:BBOX%3E>`_



.. rubric:: *Example 4 - filter on time, property, distance filters*

Requesting rainfall observations from all the stations between 2014-06-01T00:00:00+02 and
2014-06-03T00:00:00+02

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&
        request=GetObservation&
        offering=temporary&
        observedProperty=temperature&
        responseFormat=text/xml;subtype="om/1.0.0"&
        service=SOS&
        version=1.0.0&
        featureOfInterest=<ogc:DWithin>
            <ogc:PropertyName>SHAPE</ogc:PropertyName>
            <gml:Point srsName="EPSG:4326">
                <gml:coordinates decimal="." cs="," ts="">8.967,46.027</gml:coordinates>
            </gml:Point>
            <ogc:Distance>1</ogc:Distance>
        </ogc:DWithin>

`[execute above request] <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2013-01-01T00:00:00%2001/2013-02-4T17:00:00%2001&observedProperty=temperature&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.1%E2%80%9D&service=SOS&version=1.0.0&featureOfInterest=%3Cogc:DWithin%3E%3Cogc:PropertyName%3ESHAPE%3C/ogc:PropertyName%3E%3Cgml:Point%20srsName=%22EPSG:4326%22%3E%3Cgml:coordinates%20decimal=%22.%22%20cs=%22,%22%20ts=%22%20%22%3E8.967,46.027%3C/gml:coordinates%3E%3C/gml:Point%3E%3Cogc:Distance%3E1%3C/ogc:Distance%3E%3C/ogc:DWithin%3E>`_


Using the istSOS extending features
====================================

In this part of the tutorial we will explore the extending features of istSOS, developed for
making users life easier and to fulfill data experts requirements.

.. rubric:: *Example 5 - GetObservation with simple names*

According to the standard observedProperties and procedures are accessible using a
Unique Resource Identifier (URI). This is those used when the observed property and the
procedure was created.
In this tutorial we used for example:

- urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall
- urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO

istSOS is not strict and allows to specify in a GetObservation request just the or procedure
name and/or observed property in the request: as a result for the desired procedures all the
observed properties with that words will be selected (LIKE „%XXX%‟ SQL query).
In a suggested hierarchical usage of URIs, this allows to quickly access to all the subdomain
properties, so for example using *observedProperty=urn:ogc:def:parameter:x-
istsos:1.0:meteo* in a getObservation request in istSOS will return all the available
observations which measure meteo parameters (rainfall, windspeed, humidity, etc..).

Let‟s try requesting all the rainfall observations between 2014-06-01T00:00:00+02 and 2014-06-
03T00:00:00+02:

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&        
        request=GetObservation&
        offering=temporary&
        eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&
        observedProperty=rainfall&
        responseFormat=text/xml;subtype=”sensorML/1.0.0”

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.0%E2%80%9D>`_

And now the same, but only for LUGANO station:

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&        
        request=GetObservation&
        offering=temporary&
        procedure=P_LUGANO&
        eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&
        observedProperty=rainfall&
        responseFormat=text/xml;subtype="om/1.0.0"
`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=P_LUGANO&eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.0%E2%80%9D>`_


.. rubric:: *Example 6 - GetObservation with specific time zone*

istSOS support time zones. Whenever in getObservation request the eventTime is specified
with a time zone (e.g.: +0700) the response will be returned with the same time zone.

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&        
        request=GetObservation&
        offering=temporary&
        procedure=P_LUGANO&
        eventTime=2014-06-01T00:00:00+0500/2014-06-03T00:00:00+0500&
        observedProperty=rainfall&
        responseFormat=text/xml;subtype="om/1.0.0"&

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=P_LUGANO&eventTime=2014-06-01T00:00:00+0500/2014-06-03T00:00:00+0500&observedProperty=rainfall&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.0%E2%80%9D>`_


.. rubric:: *Example 7 - GetObservation in CSV or JSON*

In addition to the mandatory *text/xml;subtype=”sensorML/1.0.0”* istSOS support also
application/json and text/csv (for simplification also text or json )

Data in CSV:

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&        
        request=GetObservation&
        offering=temporary&
        eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&
        observedProperty=rainfall&
        responseFormat=text/plain

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/plain>`_       

Data in JSON:

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&        
        request=GetObservation&
        offering=temporary&
        eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&
        observedProperty=rainfall&
        responseFormat=application/json

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&eventTime=2014-06-01T00:00:00+0200/2014-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=application/json>`_  


.. rubric:: *Example 8 - GetObservation with data aggregation on the fly*

When executing a getObservation request istSOS offer an extra feature. Adding vendor
specific parameters *aggregateInterval, aggregateFunction, aggregatenodata** and
**aggregatenodataqi* you can request data already aggregated by istSOS.

- *aggregateInterval*: `ISO 8601 Durations <http://en.wikipedia.org/wiki/ISO_8601#Durations>`_ (e.g.: P1DT = 1 Day, PT12H = 12 hours)
- *aggregateFunction*: AVG, SUM, MAX, MIN

The next two parameters are optional and the default values can be configured using the
Web Admin interface:

- *aggregatenodata*: numeric value to use in the case of irregular time series.
- *aggregatenodataqi*: the quality index to be assigned to no data.

For example we can Request maximal daily temperature observation:

.. code-block:: rest

    http://localhost/istsos/demo?
        service=SOS&
        version=1.0.0&
        request=GetObservation&
        offering=temporary&
        procedure=T_LUGANO&
        eventTime=2014-05-04T00:00:00+01/2014-05-14T00:00:00+01&
        observedProperty=temperature&
        aggregateInterval=PT24H&
        aggregateFunction=MAX&
        responseFormat=text/plain

`[execute above request] <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=T_LUGANO&eventTime=2014-05-04T00:00:00+01/2014-05-14T00:00:00+01&observedProperty=temperature&aggregateInterval=PT24H&aggregateFunction=MAX&responseFormat=text/plain>`_


Using the WA REST
==================

Composing a WA REST request is all about building the correct path url.

.. rubric:: *GetObservation with WA REST*

To get the observations execute this request:

`<http://localhost/istsos/wa/istsos/services/demo/operations/getobservation/offerings/temporary/procedures/T_LUGANO/observedproperties/temper>`_

.. note::
    - Executing a service request, you will receive a list of istSOS service instances: http://localhost/istsos/wa/istsos/services
    - Executing a procedures get list operation, you will receive a list of procedures belonging to a specific service: http://localhost/istsos/wa/istsos/services/demo/procedures/operations/getlist


Using the Data Viewer
======================

The istSOS web administration pages interact with the service making use of WA REST.
The Data Viewer panel is implemented as an example of data visualization.

.. rubric:: *View observation*

To open your Web Viewer follow this link: `<http://localhost/istsos/admin/viewer.html>`_

.. note::
    Up to now the viewer permit to display data of a single observationProperties only, you can select and display multiple procedures but with the same observed property.

Go ahead and take some confidence with the `Data Viewer <http://localhost/istsos/admin/viewer.html>`_.

.. image:: images/data_viewer.png

From the Web Admin:

    - Go to Data Viewer
    - Press the Data Editor button
    - Like in the Data Viewer sequentially choose
        - the service **demo**,
        - the offering **temporary**
        - and then “Add” **BELLINZONA**, **LOCARNO** and **T_LUGANO**

.. image:: images/load_data.png

And:

    - On the right panel choose the Property: air-temperature
    - Press “Plot”, the last week of measurements is loaded and displayed

.. image:: images/data_loaded.png


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
