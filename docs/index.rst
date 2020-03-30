:orphan:

.. _index:

.. meta::
   :description: istSOS  v|version| is an OGC SOS server implementation written in Python
   :keywords: istsos, sos, sensor, data, observation, procedure, search, ogc, inspire


============================================================================== 
 istSOS
==============================================================================
*Free and Open Source Sensor Observation Service Data Management System*

.. figure::  images/istsos_logo.png
   :scale:   50


istSOS is an OGC `SOS <http://www.opengeospatial.org/standards/sos>`_ server
implementation written in `Python <https://www.python.org/>`_. istSOS allows
for managing and dispatch observations from monitoring sensors according to
the Sensor Observation Service standard.

The project provides also a Graphical user Interface that allows for easing
the daily operations and a RESTFull Web api for automatizing administration
procedures.

istSOS is released under the GPL :ref:`license`, and runs on all major
platforms (Windows, Linux, Mac OS X), even though it has been used in
production in linux environment only.

.. note:: From version >= 2.4.0 istSOS has been ported to Python3.


=============================
Quick links
=============================

* `Download <https://sourceforge.net/projects/istsos/files/>`_
* `Source (GitHub) <https://github.com/istSOS/istsos2>`_
* `Tutorial material <http://istsos.org/tutorial/>`_
* `Mailing list <https://groups.google.com/forum/#!forum/istsos>`_


.. **Users docs:**
.. ---------------------

.. .. toctree::
..     :maxdepth: 1

..     installation
..     services
..     register
..     offering
..     insert
..     acquisition
..     quality
..     getobs
..     editobs
..     virtual
..     security
..     wns

=============================
User guide
=============================

The user's documentation will give the audience all the necessary skills to
deploy the istSOS server for managing and dispatching sensor data. Moreover
attendees will be introduced with all the extra features that istSOS offers.

The material can be found here: https://sourceforge.net/projects/istsos/files/Tutorials/

Please download the latest archive and extract the content on your Desktop.

.. toctree::

    ws_installation
    ws_database
    ws_troubleshooting
    ws_instances
    ws_registersensor
    ws_offerings
    ws_insertobservation
    ws_datavalidation
    ws_dataaccess
    specimens
    profile
    ws_virtualprocedures
    ws_mapping
    ws_mqtt
    ws_arduino
    security

**Developers docs:**
---------------------

.. toctree::
    :maxdepth: 1

    intro
    istsos
    license
    dbschema
    istsoslib/istsoslib
    walib/walib
    wnslib/wnslib

.. automodule:: istsoslib
    :show-inheritance:

.. automodule:: walib
    :show-inheritance:

.. automodule:: wnslib
    :show-inheritance: