.. _intro:

==================================
Introduction to the SOS standard 
==================================

Sensor Observation Servcie (SOS) is an Open Geospatial Consortium (`OGC <www.opengeospatial.org>`_) approved standard (in version 1 and 2) that is part of the Sensor Web Enablement (SWE) initiative.

---------------------------
Sensor Web Enablement
---------------------------
The OGC Sensor Web Enablement (`SWE <http://www.opengeospatial.org/projects/groups/sensorwebdwg>`_) working group was established to provide a first definition of the system that is able to enable the development of the Sensor Web idea by identifying the technology, the language syntax and the architecture to be used.

In summary, the SWE aim is to define a unique environment where specialists and users can search, access, and process data observed by a multitude of heterogeneous sensor networks. With this propose the SWE working group has defined a series of OpenGIS® standards:
    1. `SWE Common <http://www.opengeospatial.org/standards/swecommon>`_: XML model for sensors data
    2. `SensorML <http://www.opengeospatial.org/standards/swecommon>`_ (Sensor model Language): XML model for processes and components
    3. `O&M <http://www.opengeospatial.org/standards/om>`_ (Observation and Measurements): XML model for the observation and measurements
    4. `SOS <http://www.opengeospatial.org/standards/sos>`_ (Sensor Observation Service): interface for data access and distribution
    5. `SPS <http://www.opengeospatial.org/standards/sps>`_ (Sensor Planning Service): interface for the sensor operation activation
    
And a series of candidate specification or discussion paper like the:
    6. `SAS <http://www.ogcnetwork.net/SAS>`_ (Sensor Alert Service): interface for dispatching alerts using the `XMPP <http://xmpp.org/>`_ (extensible messaging and presence protocol)
    7. WNS (Web Notification Service): interface for the notification of information with different protocols


---------------------------
Sensor Observation Service
---------------------------
As part of the SWE, the Sensor Observation Service standard defines the interface to interact with sensor observations: from sensors exploration to measures retrieval and data management throughout transactional operations. It worth noting that this description refers to SOS in version 1; the version 2 of the standard was recently approved at the time of writing and introduces some minor changes.

Like most of the OGC standards, the SOS service is based on the exchange of standard messages (requests and responses) between the service and the consumer by using the HTTP protocol. The requests are sent to the service through an HTTP POST (in this case an XML file formatted according to the specification is submitted) or an HTTP GET method (in this case a KVP, key-value-pairs, is submitted) specifying the request type and the relative permitted parameters. The service responses are always XML file compliant with the specifications.
According to the OGC specification a SOS version 1.0 service must implement at minimum the three mandatory requests of the SOS core profile, while other operations of the transactional profile and of the enhanced profile are optional (see next Table-1_). 

.. _Table-1:

========================= =============== =========== ==========================================================================
SOS request               Profile         Mandatory   Short description
========================= =============== =========== ==========================================================================
GetCapabilities             Core            Yes        Allow to describe the service providing information on administrator,
                                                       offered capabilities, observed property and features, etc..
DescribeSensor              Core            Yes        It provides a potentially detailed description of a given registered 
                                                       component, system or process in SensorML format
GetObservation              Core            Yes        It provides observations based on the setting of filters that includes
                                                       timing, processes, phenomena, feature of interest, and other parameters
                                                       in O&M model
RegisterSensor              Transactional   No         It provides capability to automatically register a new sensor to the 
                                                       existing service
InsertObservation           Transactional   No         It provides capability to dynamically insert new observation(s) related 
                                                       to a registered sensor
GetFeatureOfInterest        Enhanced        No         It provides requested feature of interest in GML format
GetResult                   Enhanced        No         It provides a light way to request observation without provide full 
                                                       request every time
GetObservationByID          Enhanced        No         It provides a quick access to observation by identification number
GetFeatureOfInterestTime    Enhanced        No         It provides the time interval when a given feature of interest has 
                                                       been observed
DescribeFeatureType         Enhanced        No         It provides the schema used to represent the features of interest
DescribeObservationType     Enhanced        No         It provides the schema used to represent the Observations
DescribeResultModel         Enhanced        No         It provides the schema used to represent the result object within 
                                                       the sml:observation
========================= =============== =========== ==========================================================================

*Table-1: SOS requests for a list of SOS request and relative short description*

Two typical SOS UML sequence diagrams respectively from a data consumer and data producer perspective are presented in Figure-1_.

.. _Figure-1:

.. figure:: intro/images/figure-1.png
    :scale: 60 %
    :align:   center
    :alt: Typical SOS UML diagrams for data consumer and producers
    
    *Figure-1: Typical SOS UML diagrams for data consumer and producer.*
    
The SOS is based on five key objects as represented in Figure-2_ :
    1. **Observations**: they are the center of the standard and represent the values mesured at given time instants (e.g.: *value*: 0.2, *time*: 08-11-2012 12:12) and represented according to the *O&M* standard data model.
    2. **Procedure**: indicates who provide the observations, this is generally the sensor but it may also be a generic process that leads to some observations (e.g.: *procedure*: TREVANO) and is represented as *SensorML* standard data model.
    3. **Observed Properties**: they represent the phenomena that are observed (e.g.: *phenomenon*: air-temperature) and is represented with a URI (uniform resource identifier) composed by colon separated text according to the *om:observedProperty* of the *O&M* standard.
    4. **Feature of interest**: it is the fature that relates to the observations, so for an in-place instrument is the sensor location, while for remote device it the target location (e.g.: *location*: Trevano, *coordinates*: 718345,99224,389, *reference system*: CH1903/LV03) represented according to the *om:featureOfInterest* element of the *O&M* standard.
    5. **Offering**: it is a collection of sensor used to conveniently group them up (e.g.: *offering*: weather-sensor-SUPSI) and is represented as *sos:ObservationOffering* element of the SOS standard.
 
.. _Figure-2:
   
.. figure:: intro/images/figure-2_bis.png
    :scale: 60 %
    :align:   center
    :alt: Key object of the SOS standard

    *Figure-1: Key objects of the SOS standard.*

  
