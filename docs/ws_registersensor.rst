.. _ws_instances:

=======================
Registering new sensors
=======================

From the “services” drop down button choose the “demo” instance.

Some advices:

.. warning::

    - Once a procedure is created the outputs (observed properties) cannot be changed.
    - Before registering new sensors it’s advised to initialize missing observed
      properties and unit of measures.
    - **Procedures with multiple observed properties**:
      Is it possible to add new procedures observing more than one properties,
      but in istSOS this means that for each observation instant we have a list
      all the observed properties values.
      e.g.:
      if a procedure that observes temperature (T), humidity (H) and rain (R) is
      created the time series will always have a list of 3 values [T,H,R] for
      each instant. If you try to insert an observation with two only values it
      will raise an exception


Add the procedure GRABOW with multiple observed properties (sensor station)
---------------------------------------------------------------------------

Let’s use the following settings for the station in GRABOW

==================  ========================================
**Name:**           GRABOW
**Description:**    Enorasis Meteo Station in Grabow, Poland.
**Keywords:**       weather, meteorological,IUNG-PIB

**System type:**    insitu-fixed-point
**Sensor type:**    Meteo Station

**FOI name:**       GRABOW
**EPSG:**           4326
**Coordinates:**    x: 22.67 y: 51.25 z: 177
==================  ========================================

**Add relative humidity**

======================= ==============================================================
**Observed property**   urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity:relative
Unit of measure:        %
Description:
Quality index check:    Between / from 0 to 100
======================= ==============================================================

**Add air rainfall**

======================= ==============================================================
**Observed property:**  urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall
Unit of measure:        mm
Description:
quality index check:    Between / from 0 to +500
======================= ==============================================================

**Add air temperature**

======================= ==============================================================
**Observed property:**  urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature
Unit of measure:        °C
Description:            conversion from resistance to temperature
Quality index check:    Between / from -40 to +60
======================= ==============================================================

**Add wind velocity**

======================= ==============================================================
**Observed property:**  urn:ogc:def:parameter:x-istsos:1.0:meteo:air:wind:velocity
Unit of measure:        m/s
Description:
Quality index check:    Between / from 0 to 200
======================= ==============================================================

**Add solar radiation**

======================= ==============================================================
**Observed property:**  urn:ogc:def:parameter:x-istsos:1.0:meteo:solar:radiation
Unit of measure:        W/m2
Description:
Quality index check:    from 0 to +500
======================= ==============================================================

**Optional parameters**
fill at your own need and willing

.. note::

    Register the new sensor (procedure) pressing the **"submit"** button.

Add other procedures
--------------------

In order to speed up the "*boring*" process of inserting all the other procedures
we have prepared a script. Open a terminal and run:

.. code-block:: bash

    cd ~/Desktop/Tutorial
    python fill/execute.py

.. note::

    Feel free to analyze the code to understand the process and eventually create
    your own script to import new sensors in the istSOS server.


Verify the inserted procedures using the administration interface
-----------------------------------------------------------------

Check your procedures by accessing the "**Procedures**" panel. You will see a table
showing an abstract of all the inserted procedures. By clicking on the name you
will be able to enter the details metadata that you configured during the
procedure registration.

.. note::

    The "**Procedures**" panel not only allows for procedures and metadata
    exploration but also allows details modification. The only exception are
    the outputs parameters.

Verify the inserted procedures using the Sensor Observation Service requests
----------------------------------------------------------------------------

Let’s try to execute a getCapabilities request to verify if procedures are now
available. We can use the “Requests” test page where some samples are already
present.

`http://localhost/istsos/modules/requests <http://localhost/istsos/modules/requests>`_

Choose the the demo service and then choose “GET > GetCapabilities” option and
then modify the section parameter to contain just the “contents” option the
request to be like this:

`http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS
<http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS>`_

Let’s execute a describeSensor request to verify that the procedure description
is available:

`http://localhost/istsos/demo?request=DescribeSensor&procedure=T_LUGANO&outputFormat=text/xml;subtype="sensorML/1.0.1"&service=SOS&version=1.0.0 <http://localhost/istsos/demo?request=DescribeSensor&procedure=T_LUGANO&outputFormat=text%2Fxml%3Bsubtype%3D%22sensorML%2F1.0.1%22&service=SOS&version=1.0.0>`_

repeat for procedures: P_LUGANO, LOCARNO, BELLINZONA, GRABOW, RH_GNOSCA.

.. note::

    | Procedures are stored in the SOS with a uniqueID which is
      urn:ogc:def:procedure:x-istsos:1.0:XXXX for procedure named XXXX.
    |
    | istSOS, as we can see later for other parameters also, is not strict and
      allows to specify just the procedure name in the request.
