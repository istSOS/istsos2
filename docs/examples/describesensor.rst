=================================
DescribeSensor
=================================

--------------
Introduction
--------------

One method of obtaining metadata that describes the characteristics of an observation procedure (sensor or sensor constellation) is to retrieve it from a catalog. However, a catalog may only contain high-level information about the observable properties,locations, contact information, etc. Due to the possibly voluminous amounts of sensorrelated metadata, the “describe” operations support retrieval of the highest level of detail about the platforms and sensors associated with an SOS.
DescribeSensor is designed to request detailed sensor metadata. Likewise, the response to a GetCapabilities request could provide a list of sensors associated with an SOS. Sensors are devices for the measurement of physical quantities. For the purpose of this discussion, there are two main kinds of sensor, in-situ and remote-dynamic. The sensor characteristics can include lists and definitions of observables supported by the sensor (SOS-Spec, OGC 06-009r6).

There are two possible ways to send an GetCapabilities request: via HTTP GET and HTTP POST.



-   **DescribeSensor parameters:** 
    
	.. csv-table:: *Table-1: DescribeSensor operation request URL parameters [OGC 06-009r6]*
	       :header: "Parameter","Description","Definition","Multiplicity and Use"
	       :widths: 20, 40, 20,20

	       "request","DescribeSensor is designed to request detailed sensor metadata","DescribeSensor","One (mandatory)"
	       "service","Service type identifier","SOS","One (mandatory)"
	       "version","Specification version for operation","1.0.0","One (mandatory)"
	       "procedure","the sensor for which the description is to be returned.","[all comma-separed valid sensors from the GetCapabilities]","One or more (mandatory)"
	       "outputFormat","desired output format of the DescribeSensor operation. This can be a MimeType or QName for example.","These are for SensorML or TML: text/xml;subtype=”sensorML/1.0.0”, text/xml;subtype=”TML/1.0” ","One (mandatory)"


----------------
GET request
----------------

::

  http://localhost/istsos/demo?request=describeSensor&procedure=T_LUGANO&outputFormat=text/xml;subtype='sensorML/1.0.0'&service=SOS&version=1.0.0
 
-----------------
POST request
-----------------

::

   http://localhost/istsos/demo/



DescribeSensor.xml

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
	<sos:describeSensor
	   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	   xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
	   xmlns:sos="http://www.opengis.net/sos/1.0"
	   xmlns:gml="http://www.opengis.net/gml/3.2"
	   xmlns:ogc="http://www.opengis.net/ogc"
	   xmlns:om="http://www.opengis.net/om/1.0" 
	   service="SOS" 
	   outputFormat="text/xml;subtype='sensorML/1.0.0'"> 

	      <procedure>T_LUGANO</procedure> 
	</sos:describeSensor>








