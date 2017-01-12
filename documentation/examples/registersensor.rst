
=================================
RegisterSensor
=================================

--------------
Introduction
--------------


The RegisterSensor operation allows the client to register a new sensor system with the SOS as part of the transactional profile. Sensor observations can only be inserted for sensors that have first been registered with the SOS. RegisterSensor is mandatory for the transactional profile.



-   **RegisterSensor parameters:** 

         .. csv-table:: *Table-1: RegisterSensor operation request URL parameters [OGC 06-009r6]*
	       :header: "Parameter","Description","Definition","Multiplicity and Use"
	       :widths: 20, 40, 20,20

	       "request","RegisterSensor is designed to register a new sensor system with the SOS","getObservation","One (mandatory)"
	       "service","Service type identifier","SOS","One (mandatory)"
	       "version","Specification version for operation","1.0.0","One (mandatory)"
	       "sensorDescription","This is generally a Sensor or System element from either SensorML or TML which is the detailed description of this sensor or system. The content is open to accommodate changes to TML and SensorML and to support other sensor description languages.","[Name of XML document]","One (mandatory)"
	       "observationTemplate","A template for observation instances that will be inserted for this sensor or system.","[Name of XML document]","One (mandatory)"
	      


-----------------
Request
-----------------

::

   http://localhost/istsos/demo/



RegisterSensor.xml

-  :download:`registerSensor_stationary_insitu_simple.xml <xml/registerSensor_stationary_insitu_simple.xml>`
-  :download:`registerSensor_stationary_insitu_composite.xml <xml/registerSensor_stationary_insitu_composite.xml>`

`registerSensor_dynamic_insitu_simple.xml`

`registerSensor_dynamic_insitu_composite.xml`




	



