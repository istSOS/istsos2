
=================================
InsertObsertation
=================================

--------------
Introduction
--------------


The InsertObservation operation allows the client to insert new observations for a sensor system. This is a request to an SOS to perform the Insert operation. The request includes the sensor ID that was obtained from the RegisterSensor operation. The observation must be encoded in XML following the O&M specification. InsertObservation is mandatory for the transactional profile.



-   **InsertObsertation parameters:** 

         .. csv-table:: *Table-1: InsertObsertation operation request URL parameters [OGC 06-009r6]*
	       :header: "Parameter","Description","Definition","Multiplicity and Use"
	       :widths: 20, 40, 20,20

	       "request","InsertObsertation is designed to request detailed sensor metadata","getObservation","One (mandatory)"
	       "service","Service type identifier","SOS","One (mandatory)"
	       "version","Specification version for operation","1.0.0","One (mandatory)"
	       "Observation","The new observation for insertion.","[name of XML document]","One (mandatory)"
	       "AssignedSensorId","Specifies the identifier for the sensor that made this observation. This identifier is obtained by the RegisterSensor operation.","[id of sensor, which has produced the observation]","One (mandatory)"
	      


-----------------
Request
-----------------

::

   http://localhost/istsos/demo/

InsertObsertation.xml

-  :download:`insertObservation_stationary_insitu_simple.xml <xml/insertObservation_stationary_insitu_simple.xml>`
-  :download:`insertObservation_stationary_insitu_composite.xml <xml/insertObservation_stationary_insitu_composite.xml>`

`insertObservation_dynamic_insitu_simple.xml`

`insertObservation_dynamic_insitu_composite.xml`



