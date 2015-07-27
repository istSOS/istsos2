.. _istsos:

==================================
istSOS software
==================================

istSOS (Istituto Scienze della Terra Sensor Observation Service) is the implementation of the Sensor Observation Service standard from Open Geospatial Consortium by the Institute of Earth Sciences (IST, Istituto Scienze della Terra). istSOS is distributed with a GPLv2 licence.
The development of istSOS started in 2009 in order to provide a simple implementation of the SOS standard for the management, provision and integration of hydro-meteorological data collected in Canton Ticino (Switzerland).

.. figure::  images/istsos_logo.png
   :align:   center
   :scale:   100


The developement of istSOS started in 2009 in orther to provide a simple implementation of the SOS standard for the management, provision and integration of hydro-meteorological data collected in Canton Ticino (Switzerland).

---------------
Project links
---------------
**Mailing list**: `<https://groups.google.com/forum/#!forum/istsos>`_

**Web**: `<http://istsos.org>`_

**Source code**: `<http://sourceforge.net/projects/istsos>`_

-----------------------------------
Technologies
-----------------------------------
istSOS is entirerly written in `Python <http://python.org/>`_ and is based on:

    * `PostgreSQL <http://www.postgresql.org/>`_ / `PostGIS <http://postgis.refractions.net/>`_
    * `Apache <http://www.apache.org/>`_ / `mod_wsgi <http://code.google.com/p/modwsgi/>`_ (`mod_python <http://www.modpython.org/>`_ for versions <= 1.0) 
    * `GDAL <http://www.gdal.org/>`_ (for versions < 2.0)
    
And it takes advantage of other python modules:

    * `isodate <http://pypi.python.org/pypi/isodate/>`_
    * `python-gdal <http://pypi.python.org/pypi/GDAL/>`_ (for versions < 2.0)
    * `psycopg2 <http://pypi.python.org/pypi/psycopg2>`_
    * `pytz <http://pypi.python.org/pypi/pytz/>`_

----------------------------------
Software structure
----------------------------------

istSOS evolved in time from being a SOS service provider to complete data management system.
Initially it was an implementation supporting the standard as defined by the OGC through the **istsoslib**, the core of the system. Thanks to the continue interaction with hydrologists and data users, We soon realized that the standard didn’t account for a number of requirements, like a missing supporting for irregular time series. So, We started developing extending features and enriched the istSOSlib. Afterward, We understood that without a comfortable Graphical User Interface (GUI) the time used to manage the system and the data (e.g.: update metadata, add new sensors, verify, correct and validate data) were too overwhelming. This lead to the idea of developing a Web Administration interface (**wainterface**) based on a RESTful service: **walib**.

As a result today istSOS is like a peach, were the **wainterface** is the peel, **walib** is the pulp and **istsoslib** is the kernel. These three components interact each others and offer different interfaces for different users types: humans, processes or standard clients.

.. figure::  images/software-architecture.png
   :align:   center
   :scale:   50

A configuration file store important setting parameters like service metadata (e.g.: name, version, owner), database connection parameters, dictionaries definition, handled requests, etc.

----------------------------------
istsosllib (core package) structure
----------------------------------
istSOS has been developed with a *factory* approach using three modules:
  * **filters**: provide an interface for converting http requests (GET or POST) submitted according the SOS standard in python objects that contains the submitted parameters and values.
  * **responders**: resolve the specific request, interacting with the istSOSdatabase and gathering the required informations.
  * **renderers**: reponsible for converting the informations stored in the responders into SOS response format as defined by SOS standard.

These istSOS service handle the different SOS requests by instantiating subsequntially a **factory_filter**, a **factory_reponder** and a **factory_renderer** wich are capable to call the specific classes for elaborating the correct response.

As illustrated in Figure, at first the *factory_filter* istantiate the appropriate filter class (function of the request type), then the *factory_responder* authomatically instantiate the relative reponder class and finally the correct renderer is called by the *factory_renderer* to produce an SOS response.
 
.. figure::  images/figure-3.png
   :align:   center
   :scale:   50

   *Figure-3: istSOS working flow.*

A configuration file store important setting parameters like service metadata (e.g.: name, version, owner), database connection parameters, dictionaries definition, handled requests, etc.

----------------------------------
istSOS extending features
----------------------------------
Apart from standard features like filter capabilities of the observations by means of time periods, observed properties, geospatial relationships and sensor names istSOS implements several extending features that, according to the developers and decades experienced collaborators in sensor network management and data management were found particularly helpful.

Some of the extending capabilities are:
  * Handle of irregular time series
  * On-the-fly aggregation of observed measures with no-data management.
  * Support for different output formats like application/json, text/csv, and textxml:subtype=sensorML.
  * Possibility of inserting many observations with a single insertObservation requests.
  * Supporting of a override parameter that allows to overwrite already registered observations with new ones.
  * Capability to filter observations based on partial observed property names ( LIKE filtering support).
  * Native support for data quality index associated with each observation.
  * Setting of maximum period for data retrievement requests to avoid server overloads.
  * Availability of a virtual procedure mechanism, that expose new sensors and observed properties as on-the-fly elaboration of regular observation.
  * On the fly data aggregation.
  * Real time data validation and quality index 
    
----------------------------------
istSOS 2.0 database schema
----------------------------------
Please look at the DB documentation generated using SchemaSpy `istSOS 2.0 Schema <_static/istsosDB/index.html>`_

---------------------    
Acknowledgements
---------------------
The authors thank all the partners of the Verbano Lake working group for flood risk reduction, and specially the Canton Ticino, (Ufficio dei corsi d’acqua), for supporting this project. Special thanks to people contributing to the software development and Google Summer of Code and OSGeo for sponsoring students works on istSOS.    
    
    


