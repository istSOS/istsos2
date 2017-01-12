GetFeatureOfInterest
---------------------

--------------
Introduction
--------------

GetFeatureOfInterest returns a featureOfInterest that was advertised in one of the observation offerings of the SOS capabilities document. This could be a Station for in-situ sensors, for example.(SOS-Spec, OGC 06-009r6)





-   **DescribeSensor parameters:** 
    
	.. csv-table:: *Table-1: GetFeatuatureOfInterest operation request URL parameters [OGC 06-009r6]*
	       :header: "Parameter", "Description", "Definition", "Multiplicity and Use"
	       :widths: 20, 40, 20, 20

	       "request", "returns a featureOfInterest that was advertised in one of the observation offerings of the SOS capabilities document", "getFeatureOfInterest", "One (mandatory)"
	       "service", "Service type identifier", "SOS", "One (mandatory)"
	       "version", "Specification version for operation", "1.0.0", "One (mandatory)"       
           "featureOfInterestId", "Specifies the identifier of the feature of interest being returned, for which detailed information is requested. These identifiers must be listed in the Contents section of the service metadata (GetCapabilities) document", "featureId from GetCapabilities", "One (mandatory) Choice1"
	       "bbox", "geographical boundingbox in comma-separeted values", "lon1,lat1,lon2,lat2", "One (mandatory) Choice2 with srs"
	       "srs", "srs of the bbox enveloppe : only EPSG:4326", "EPSG:4326", "One (mandatory) Choice2 with bbox"
           "eventTime", "Specifies the time for which the feature of interest is to be queried. This uses a modified version of filter.xsd and allows a client to request targets from a specific instance, multiple instances or periods of time in the past, present and future. This is useful for dynamic sensors for which the properties of the feature of interest are time-dependent. Multiple time parameters may be indicated so that the client may request details of the observation target at multiple times. The supported range is listed in the contents section of the service metadata.",  "srs of the bbox enveloppe : only EPSG:4326", "Zero or more (optional)"


----------------
GET request
----------------

-   **GetFeatureOfInterest GET request:**



	

::

 
   http://localhost/istsos/demo/?request=getFeatureOfInterest&featureOfInterestId=LUGANO&srsName=21781&service=SOS&version=1.0.0


-----------------
POST request
-----------------

::

   http://localhost/istsos/demo/

-   **GetFeatureOfInterest with ID :** 

GetFeatureOfInterestFeatureId.xml 

-  :download:`getFeatureOfInterest.xml <xml/getFeatureOfInterest.xml>`


.. code-block:: xml


      <?xml version="1.0" encoding="UTF-8"?>
	<sos:getfeatureOfinterest
	   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	   xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
	   xmlns:sos="http://www.opengis.net/sos/1.0"
	   xmlns:gml="http://www.opengis.net/gml/3.2"
	   xmlns:ogc="http://www.opengis.net/ogc"
	   xmlns:om="http://www.opengis.net/om/1.0" service="SOS" outputFormat="text/xml;subtype='sensorML/1.0.0'"> 
	<FeatureOfInterestId>urn:ogc:def:feature:x-istsos:1.0:Point:LUGANO</FeatureOfInterestId>
	<srsName>4326</srsName>

	<!-- See GetFeatureOfInterest operation description 
	in the getCapabilities response to see available projection -->

	<!-- Examples
	<srsName>urn:ogc:crs:EPSG:21781</srsName>
	<srsName>urn:ogc:crs:EPSG:4326</srsName>
	<srsName>urn:ogc:crs:EPSG:8001</srsName>
	-->

	</sos:getfeatureOfinterest>




