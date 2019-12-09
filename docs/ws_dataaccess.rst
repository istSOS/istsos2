.. _ws_dataaccess:

===============
Accessing data
===============

Accessing the data is possible using the SOS Standard requests, WA REST
requests or directly using the Data Viewer or Data Editor.

.. figure::  images/data_access.png

Let’s try to request data using the different interfaces...

Getting observations in the SOS 1.0.0 way
-----------------------------------------

Quick view on the GetObservation request using the GET method:

==================  ==========================  ==========================  ==========================
Parameter           Description                 Definition                  Multiplicity and Use

request             getObservation is designed  getObservation              One (mandatory)
                    to request detailed sensor
                    metadata

service             Service type identifier     SOS                         One (mandatory)

version             Specification version for   1.0.0                       One (mandatory)
                    operation

srsName             Defines the spatial         This must be one of the     One (Optional)
                    reference system that       advertised values in the
                    should be used for any      offering specified in
                    geometries that are         gml:srsName elements.
                    returned in the
                    response.

offering            Specifies the offering      This must match the         One (mandatory)
                    URI advertised in the       gml:name of the offering
                    GetCapabilities document.   or be constructed as a
                    All of the following        URL with a fragment
                    parameters are dependent    identifier resolving to
                    on the selected offering.   the offering gml:id.

eventTime           Specifies the time          ISO 8601                    Zero or many
                    period(s) for which         Examples:                   (Optional)
                    observations are            Time instant:
                    requested. This allows      2015-06-11T17:30:00+0200
                    a client to request         Time period
                    observations from a         2015-06-11T14:30:00+0200/
                    specific instant,           2015-06-11T17:30:00+0200
                    multiple instances
                    or periods of time in
                    the past, present and
                    future. The supported
                    range is listed in
                    the selected offering
                    capabilities

procedure           The procedure parameter     comma separated valid       Zero or many
                    specifies the sensor        sensors from the            (Optional
                    system(s) for which         GetCapabilities
                    observations are
                    requested. It defines
                    a filter for the
                    procedure property
                    of the observations.

observedProperty                                                            One or many
                                                                            (mandatory)

featureOfInterest   Specifies the feature                                   Zero or many
                    for which observations                                  (Optional)
                    are requested. This
                    can either be
                    represented by a
                    reference to a feature
                    ID advertised in the
                    capabilities document
                    or can be a spatial
                    constraint.

responseFormat      Specifies the desired       text/xml;subtype="sensor    One (mandatory)
                    resultFormat MIME           ML/1.0.0"
                    content type for
                    transport of the
                    results (e.g. TML,
                    O&M native format,
                    or MPEG stream
                    out-of-band).
                    The supported
                    output formats are
                    listed in the selected
                    offering capabilities.
                    Desired output format
                    of the getObservation
                    operation. This can
                    be a MimeType or
                    QName for example.

==================  ==========================  ==========================  ==========================

Procedure-time-property filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Requesting rainfall observations from sensor P_LUGANO between
2015-01-01T00:00:00+01 and 2015-02-4T17:00:00+01:

| ``http://localhost/istsos/demo?``
|       ``service=SOS&``
|       ``request=GetObservation&``
|       ``offering=temporary&``
|       ``procedure=urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO&``
|       ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|       ``observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&``
|       ``responseFormat=text/xml;subtype="sensorML/1.0.1"&``
|       ``service=SOS&``
|       ``version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&procedure=urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&responseFormat=text/xml;subtype="sensorML/1.0.1"&service=SOS&version=1.0.0>`_

Time-property filters
^^^^^^^^^^^^^^^^^^^^^

Requesting rainfall observations from all the stations between
2014-06-01T00:00:00+02 and 2014-06-03T00:00:00+02:

| ``http://localhost/istsos/demo?``
|       ``service=SOS&``
|       ``request=GetObservation&``
|       ``offering=temporary&``
|       ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|       ``observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&``
|       ``responseFormat=text/xml;subtype="sensorML/1.0.0"&``
|       ``service=SOS&version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&responseFormat=text/xml;subtype="sensorML/1.0.0"&service=SOS&version=1.0.0>`_

Time-property-area filters
^^^^^^^^^^^^^^^^^^^^^^^^^^

Requesting the last meteo observations applying a spatial intersection
with a BBOX:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``observedProperty=meteo&``
|     ``responseFormat=text/xml;subtype="sensorML/1.0.1"&``
|     ``service=SOS&``
|     ``version=1.0.0&``
|     ``featureOfInterest=<ogc:BBOX><ogc:PropertyName>the_geom</ogc:PropertyName><gml:Box srsName='EPSG:4326'><gml:coordinates>18,45 30,55</gml:coordinates></gml:Box></ogc:BBOX>``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&observedProperty=meteo&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.1%E2%80%9D&service=SOS&version=1.0.0&featureOfInterest=%3Cogc:BBOX%3E%3Cogc:PropertyName%3Ethe_geom%3C/ogc:PropertyName%3E%3Cgml:Box%20srsName=%27EPSG:4326%27%3E%3Cgml:coordinates%3E18,45%2030,55%3C/gml:coordinates%3E%3C/gml:Box%3E%3C/ogc:BBOX%3E>`_

Time-property-distance filters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Requesting the last meteo observations applying a distance filter:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``observedProperty=temperature&``
|     ``responseFormat=text/xml;subtype="sensorML/1.0.1"&``
|     ``service=SOS&version=1.0.0&``
|     ``featureOfInterest=<ogc:DWithin><ogc:PropertyName>SHAPE</ogc:PropertyName><gml:Point srsName="EPSG:4326"><gml:coordinates decimal="." cs="," ts=" ">8.961,46.027</gml:coordinates></gml:Point><ogc:Distance>10</ogc:Distance></ogc:DWithin>``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&observedProperty=temperature&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.1%E2%80%9D&service=SOS&version=1.0.0&featureOfInterest=%3Cogc:DWithin%3E%3Cogc:PropertyName%3ESHAPE%3C/ogc:PropertyName%3E%3Cgml:Point%20srsName=%22EPSG:4326%22%3E%3Cgml:coordinates%20decimal=%22.%22%20cs=%22,%22%20ts=%22%20%22%3E8.961,46.027%3C/gml:coordinates%3E%3C/gml:Point%3E%3Cogc:Distance%3E10%3C/ogc:Distance%3E%3C/ogc:DWithin%3E>`_

*Now try to change the distance from 10 to 100.*

Time-property filters and result values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Requesting rainfall observations from all the stations between
2014-06-01T00:00:00+02 and  2014-06-03T00:00:00+02 and where the rain value
is greater than 0:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|     ``observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&``
|     ``responseFormat=text/plain&``
|     ``result="<ogc:PropertyIsGreaterThan><ogc:PropertyName>rainfall</ogc:PropertyName><ogc:Literal>0</ogc:Literal></ogc:PropertyIsGreaterThan>"``

`Execute request <http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall&responseFormat=text/plain&result=%22%3Cogc:PropertyIsGreaterThan%3E%3Cogc:PropertyName%3Erainfall%3C/ogc:PropertyName%3E%3Cogc:Literal%3E0%3C/ogc:Literal%3E%3C/ogc:PropertyIsGreaterThan%3E%22>`_

Getting observations using the istSOS extending features
--------------------------------------------------------

In this part of the tutorial we will explore the extending features of istSOS,
developed for making user life easier and to fulfill data experts requirements.

GetObservation with simple names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

According to the standard observedProperties and procedures are accessible
using a Unique Resource Identifier (URI). This is those used when the
observed property and the procedure was created.

In this tutorial we used for example:

- urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall
- urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO

istSOS is not strict and allows to specify in a GetObservation request just
the or procedure name and/or observed property in the request: as a result
for the desired procedures all the observed properties with that words will
be selected (LIKE ‘%XXX%’ SQL query).

In a suggested hierarchical usage of URIs, this allows to quickly access to
all the subdomain properties, so for example using
``observedProperty=urn:ogc:def:parameter:x-istsos:1.0:meteo`` in a getObservation
request in istSOS will return all the available observations which measure
meteo parameters (rainfall, windspeed, humidity, etc..).

Let’s try:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``procedure=P_LUGANO&``
|     ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|     ``observedProperty=rainfall&``
|     ``responseFormat=text/xml;subtype="sensorML/1.0.1"&``
|     ``service=SOS&version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&procedure=P_LUGANO&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/xml;subtype="sensorML/1.0.1"&service=SOS&version=1.0.0>`_

Requesting all the rainfall observations between 2015-06-01T00:00:00+02 and
2015-06-03T00:00:00+02:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|     ``observedProperty=rainfall&``
|     ``responseFormat=text/xml;subtype="sensorML/1.0.1"&``
|     ``service=SOS&``
|     ``version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/xml;subtype=%E2%80%9DsensorML/1.0.0%E2%80%9D&service=SOS&version=1.0.0>`_

GetObservation with specific time zone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
istSOS support time zones. Whenever in getObservation request the eventTime
is specified with a time zone (e.g.: +0700) the response will be returned with
the same time zone.

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``procedure=P_LUGANO&``
|     ``eventTime=2015-06-01T00:00:00+0500/2015-06-03T00:00:00+0500&``
|     ``observedProperty=rainfall&``
|     ``responseFormat=text/xml;subtype="sensorML/1.0.1"&``
|     ``service=SOS&``
|     ``version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&procedure=P_LUGANO&eventTime=2015-06-01T00:00:00+0500/2015-06-03T00:00:00+0500&observedProperty=rainfall&responseFormat=text/xml;subtype="sensorML/1.0.1"&service=SOS&version=1.0.0>`_

GetObservation in CSV or JSON
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In addition to the mandatory text/xml;subtype="sensorML/1.0.0" istSOS support
also application/json and text/csv (for simplification also text or json )

Data in CSV:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|     ``observedProperty=rainfall&``
|     ``responseFormat=text/plain&``
|     ``service=SOS&``
|     ``version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/plain&service=SOS&version=1.0.0>`_

Data in JSON:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|     ``observedProperty=rainfall&``
|     ``responseFormat=text/json&``
|     ``service=SOS&``
|     ``version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/json&service=SOS&version=1.0.0>`_

GetObservation with data aggregation on the fly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When executing a getObservation request istSOS offer an extra feature. Adding
vendor specific parameters aggregateInterval, aggregateFunction,
aggregatenodata and aggregatenodataqi you can request data already aggregated
by istSOS.

- aggregateInterval: ISO 8601 Durations (P1DT = 1 Day, PT12H = 12 hours)
- aggregateFunction: AVG, SUM, MAX, MIN

For example we can Request maximal daily temperature observation:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``procedure=T_LUGANO&``
|     ``eventTime=2015-05-04T00:00:00+01/2015-05-14T00:00:00+01&``
|     ``observedProperty=temperature&``
|     ``aggregateInterval=PT24H&``
|     ``aggregateFunction=MAX&``
|     ``responseFormat=text/plain&``
|     ``service=SOS&``
|     ``version=1.0.0``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&procedure=T_LUGANO&eventTime=2015-05-04T00:00:00+01/2015-05-14T00:00:00+01&observedProperty=temperature&aggregateInterval=PT24H&aggregateFunction=MAX&responseFormat=text/plain&service=SOS&version=1.0.0>`_

GetObservation in CSV with qualityIndex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

in addition to the mandatory text/xml;subtype="sensorML/1.0.0" istSOS support
also application/json and text/csv (for simplification also text or json)

Data in CSV with **qualityIndex**:

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&``
|     ``observedProperty=rainfall&``
|     ``responseFormat=text/plain&``
|     ``service=SOS&``
|     ``version=1.0.0&``
|     ``qualityIndex=True``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200&observedProperty=rainfall&responseFormat=text/plain&service=SOS&version=1.0.0&qualityIndex=True>`_

**Data in CSV with qualityFilter:**

Note that when applying a qualityFilter istSOS returns only the observations
that has all the observedProperties values with associated qualityIndex
satisfying the criteria.

e.g.: suppose you have a procedure observing rainfall, temperature and
humidity. Your single observation will have the triplet of values and quality
index:

.. code-block:: csv

    time1, rain value, rain qi, temperature val, emperature  qi, humidity val, humidity qi
    time2, rain value, rain qi, temperature val, emperature  qi, humidity val, humidity qi
    time3, rain value, rain qi, temperature val, emperature  qi, humidity val, humidity qi
    time4, rain value, rain qi, temperature val, emperature  qi, humidity val, humidity qi

=================   ============================================================
**Operator**        **istSOS behaviour**
>                   only records where all qi are > of the filter value are
                    returned
>=                  only records where all qi are >= of the filter value are
                    returned
<                   only records where all qi are < of the filter value are
                    returned
<=                  only records where all qi are <= of the filter value are
                    returned
=                   all the records that has at least one qi equal to the
                    filter value
=================   ============================================================

| ``http://localhost/istsos/demo?``
|     ``service=SOS&``
|     ``request=GetObservation&``
|     ``offering=temporary&``
|     ``eventTime=2015-06-03T15:00:00+01:00/2015-06-03T16:00:00+01:00&``
|     ``observedProperty=temperature&``
|     ``responseFormat=text/plain&``
|     ``service=SOS&``
|     ``version=1.0.0&``
|     ``procedure=T_LUGANO&``
|     ``qualityIndex=True&``
|     ``qualityfilter=>110``

`Execute request <http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=temporary&eventTime=2015-06-03T15:00:00+01:00/2015-06-03T16:00:00+01:00&observedProperty=temperature&procedure=T_LUGANO&responseFormat=text/plain&service=SOS&version=1.0.0&qualityIndex=True&qualityfilter=%3E110>`_

Getting observations using the WA REST
--------------------------------------

Composing a WA REST request is all about building the correct path url.

`http://localhost/istsos/wa/istsos/services/demo/operations/getobservation/offerings/temporary/procedures/T_LUGANO/observedproperties/temperature/eventtime/2015-05-21T00:00:00+02:00/2015-05-28T00:00:00+02:00 <http://localhost/istsos/wa/istsos/services/demo/operations/getobservation/offerings/temporary/procedures/T_LUGANO/observedproperties/temperature/eventtime/2015-05-21T00:00:00+02:00/2015-05-28T00:00:00+02:00>`_

.. note::

    Executing a service request, you will receive a list of istSOS service
    instances: http://localhost/istsos/wa/istsos/services

    Executing a procedures get list operation, you will receive a list of
    procedures belonging to a specific service:

    `http://localhost/istsos/wa/istsos/services/demo/procedures/operations/getlist <http://localhost/istsos/wa/istsos/services/demo/procedures/operations/getlist>`_

Getting observations with the Data Viewer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The istSOS web administration pages interact with the service making use of
WA REST. The Data Viewer panel is implemented as an example of data
visualization.

**View observation**

To open your Web Viewer follow this link: http://localhost/istsos/admin

And then in the "Data Management" tab press the "Data Viewer" button.

.. note::

    Up to now the viewer permit to display data of a single
    observationProperties only, you can select and display multiple procedures
    but with the same observed property.

Go ahead and take some confidence with the Data Viewer.

.. figure::  images/dataviewer.png
    :scale:   100

Editing observations with the Data Editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hey! The procedure T_LUGANO has some problems.. let's fix it!

From 2015-06-02T02:40:00 to 2015-06-02T07:20:00 there are no data values:

.. code-block:: csv

    urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature
    2015-06-02T02:30:00.000000+0200,12.150000
    2015-06-02T02:40:00.000000+0200,-999.9
    2015-06-02T02:50:00.000000+0200,-999.9
    2015-06-02T03:00:00.000000+0200,-999.9

We can correct them using the Data Editor!

**Load the data**

From the Web `Admin <http://localhost/istsos/admin>`_:

- Go to Data Management
- Press the Data Editor button
- Like in the Data Viewer sequentially choose
    - the service demo,
    - the offering temporary
    - and then "Add" BELLINZONA, LOCARNO and T_LUGANO

.. figure::  images/load_data.png
    :scale:   100

- On the right panel choose the Property: air-temperature
- Press "**Plot**", the last week of measurements is loaded and displayed

.. figure::  images/data_loaded.png
    :scale:   100

**Editing with the "Calculator"**

On the left panel there is the "**Editor**" tab:

.. figure::  images/editor_tab.png
    :scale:   100

- Select **T_LUGANO** from the combo list

- The press "**Start editing**", the grid is now displayed

- At the bottom-right corner of the chart there are 3 buttons "Day", "Week" and "All"
    - Click on "Day", the chart is zoomed to contain only one day of data
    - Drag the timeline bar on the right where you will see that T_LUGANO has no data

.. figure::  images/no_data.png
    :scale:   100

- Click on the chart to select the last observation before the "**nodata**" hole,
  a green line is displayed and in the **Editing Grid** the corresponding row is
  selected.

- Now go to the **Editing Grid** panel
    - Click the first row where data are **NaN**,
    - Scroll to the last **NaN** record and holding the `SHIFT` Key click on it
    - The press the "**Calculator**" button

.. figure::  images/data_editing.png
    :scale:   100

With the Calculator we are able to correct an interval of data in a single
action. It is possible to set a numeric value or also use a function using
data from the other loaded procedures.

Let’s build a function that make the average of the data from BELLINZONA
and LOCARNO and then removes to units:

.. code::

    ((BELLINZONA+LOCARNO)/2)-2

Select the quality index. In this case we can choose a QI 500 (manually
adjusted).

.. figure::  images/calculator.png
    :scale:   100
