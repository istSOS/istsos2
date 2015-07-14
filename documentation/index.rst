:orphan:

.. _index:

.. meta::
   :description: istSOS is an OGC SOS server implementation written in Python
   :keywords: istsos, sos, sensor, data, observation, procedure, search, ogc, inspire

=============================
istSOS-project documentation
=============================

*Free and Open Source Sensor Observation Service Data Management System*
   
.. figure::  images/istsos_logo.png
   :align:   center
   :scale:   100


istSOS is an OGC `SOS <http://www.opengeospatial.org/standards/sos>`_ server implementation written in `Python <https://www.python.org/>`_. 
istSOS allows for managing and dispatch observations from monitoring sensors according to the Sensor Observation Service standard.

The project provides also a Graphical user Interface that allows for easing the daily operations and a RESTFull Web api for automatizing administration procedures.

istSOS is released under the GPL :ref:`license`, and runs on all major platforms 
(Windows, Linux, Mac OS X), even though it has been used in production in linux environment only.


**Users docs:**
---------------------

.. toctree::
    :maxdepth: 1

    installation
    services
    register
    offering
    insert
    quality
    getobs
    editobs
    virtual
    mapping
    license

**Developers docs:**
---------------------

.. toctree::
    :maxdepth: 1

    gcclass
    obclass
    dbschema
    
    
