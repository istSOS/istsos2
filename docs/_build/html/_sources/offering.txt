.. _offering:

=========================
Observation Offerings
=========================

In the Sensor Observation Service 1.0.0 the concept of an Observation Offering is equivalent to that of a sensor constellation. An Observation Offering is analogous to a “layer” in Web Map Service because each offering is typically a non-overlapping group of related observations.

.. image:: images/offerings_constellation.png

.. info::
    The “temporary” offering is system wide offering that is used to associate every registered procedure. Every new procedure is automatically assigned to this offering. 

Creating a new offering
========================

Open the “Offerings” panel.

.. image:: images/offerings.png

.. rubric:: *Example*

+-------------------------------------------------------+
| Name: workshop                                        |
+-------------------------------------------------------+
| Description: demo dataset for FOSS4G meeting          |
+-------------------------------------------------------+
| Expiration (optional): 2015-01-01T00:00:00+02:00      |
+-------------------------------------------------------+
| Validity: Enabled                                     |
+-------------------------------------------------------+

Associate procedures with offering
===================================

Activate the tab panel pressing “Offering-procedure memberships”. 

In the dropdown list select the newly created offering “workshop”. 

On the left side you will see all the procedure that will be assigned to that offering. 

On the right there are all the procedures not assigned to that offering. 

Use drag and drop functionality to move procedures from right to left.

Verify that procedures are associated with offering as desired 
==============================================================

To verify execute a getCapabilities request.

.. rubric:: *Example*

`<http://localhost/istsos/demo?request=getCapabilities&section=contents&service=SOS&version=1.0.0>`_

.. note:: replace "demo" in the URL with your service of interest






