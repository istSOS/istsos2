.. _ws_offerings:

=====================
Observation Offerings
=====================

In the Sensor Observation Service 1.0.0 the concept of an Observation
Offering is equivalent to that of a sensor constellation. An Observation
Offering is analogous to a “layer” in Web Map Service because each offering
is typically a non-overlapping group of related observations.

.. figure::  images/offerings_constellation.png
    :align:   center
    :scale:   100

**Create a new offering**

Press the “new” button and fill the form as following:

========================= ================================
**Name**                   workshop
**Description**            demo dataset
**Expiration (optional)**  2020-01-01T00:00:00+09:00
**Validity**               Enabled
========================= ================================

**Associate procedures with offering**

Activate the tab panel pressing “Offering-procedure memberships”. In the
dropdown list select the newly created offering “workshop”. On the left side
you will see all the procedure that will be assigned to that offering. On the
right there are all the procedures not assigned to that offering. Use drag and
drop functionality to move procedures from right to left.

**Verify that procedures are associated with offering as desired**

Then check the getCapabilities request to see what happened.

`http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS&version=1.0.0
<http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS&version=1.0.0>`_


.. note::

    The “temporary” offering is system wide offering that is used to associate
    every registered procedure. Every new procedure is automatically assigned
    to this offering.

.. warning::

    In SOS version 2.0 Offerings are considered as containers for sensor
    summary information and thus are in a 1:1 relationship with sensors.

    istSOS answers to a getCapabilities request with version=2.0.0 parameter
    automatically assigning an Offering for each sensor naming it with the
    SENSOR_NAME.

    **Verify that procedures are associated with offering as described**

    `http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS&acceptVersions=2.0.0
    <http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS&acceptVersions=2.0.0>`_
