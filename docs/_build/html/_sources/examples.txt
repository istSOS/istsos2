
==========================
Example of SOS requests
==========================
The SOS operations follow the general pattern of other OGC Web Services (OWS) and where appropriate inherit or re-use elements defined previously in the context of OWS.
Operations defined for a Sensor Observation Service fall into four profiles: *core*, *enhanced*, *transactional* and *entire*.

**Core Operations Profile**

The mandatory *Core* operations are **GetCapabilities**, **DescribeSensor** and **GetObservation**. 

The GetCapabilities operation returns a service description containing information about the service interface (e.g. supported operations, service version) and the available sensor data (e.g. registered sensors, time period of available observations, spatial extent of features for which observations are available).

The DescribeSensor operation returns a description of one specific sensor, sensor system or data producing procedure containing information like position of sensor, calibration, input and outputs, etc. The response has to be either encoded in SensorML or in TML.

The GetObservation operation provides pull-based access to sensor observations and measurement-data via a spatio-temporal query that can be filtered by phenomena and value constraints.


.. toctree::
   :maxdepth: 1

   examples/getcapabilities.rst
   examples/describesensor.rst
   examples/getobservation.rst  


**Transaction Operations Profile**

The mandatory *Transactional* operations are **RegisterSensor** and **InsertObservation**.

The RegisterSensor operation allows sensor data providers to register new sensors with the SOS via the service interface by sending either a TML or a SensorML sensor description to the SOS.

The InsertObservation operation allows the client to insert new observations for a sensor system. Sensor observations can only be inserted for sensors that have first been registered with the SOS.

.. toctree::
   :maxdepth: 1

   examples/registersensor.rst
   examples/insertobservation.rst


**Enhaced Operations Profile**

The Enhanced Profile defines the following additional operations which are optional for the SOS implementations to provide:


GetFeatureOfInterest: The GetFeatureOfInterest operation returns one or more descriptions of target features of observations (FeatureOfInterest).

.. toctree::
   :maxdepth: 1

   examples/getfeatureofinterest.rst

**Not supported yet**

GetResult: The purpose of the GetResult operation is to allow a client to repeatedly obtain sensor data from the same set of sensors without having to send and receive requests and responses that largely contain the same metadata except for a new timestamp.

GetObservationByID: The GetObservationByID operation is designed to return an observation based on an identifier.



GetFeatureOfInterestTime: The GetFeatureOfInterestTime operation returns the time periods for which the SOS will return data for a given FeatureOfInterest.

DescribeFeatureType: The DescribeFeatureType operation returns the XML schema for the specified GML feature which depicts a target feature of observations (FeatureOfInterest).

DescribeResultModel: The DescribeResultModel operation returns the XML schema for the result element of a certain observation type. This is of special interest for complex result elements, e.g. containing multi-spectral values.


 

**Summary istSOS WAlib 2.0**

.. toctree::
   :maxdepth: 1

   examples/istsos_wa.rst



.. note:: This page describes the *Common Practice* in using istSOS trough practical examples of GET and POST requests based on the *demo* service that cames with the software.