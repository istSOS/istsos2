=================================
GetCapabilities
=================================

--------------
Introduction
--------------

This operation allows clients to retrieve service metadata about a specific service instance. No "request" parameter is included, since the element name specifies the specific operation. (SOS-Spec, OGC 06-009r6)




.. csv-table:: *Table-1: GetCapabilities operation request URL parameters [OGC 06-121r3]*
       :header: "Parameter","Description","Definition","Multiplicity and Use"
       :widths: 20, 20, 20, 20

       "request","operation name","GetCapabilities","One (mandatory)"
       "service","service type identifier","SOS","One (mandatory)"
       "acceptVersions","Comma-separated prioritized sequence of one or more specification versions accepted by client with preferred versions listed first","1.0.0","Zero or more (optional)"
       "sections","Comma-separated unordered list of zero or more names of sections of service metadata document to be returned in service metadata document","serviceidentification, serviceprovider, operationsmetadata, contents","Zero or more (optional)"
       "updateSequence","Service metadata document version, value is “increased” whenever any change is made in complete service metadata document","[value] (value of metadata document version)","Zero or more (optional)"
       "acceptFormats","Comma-separated prioritized sequence of zero or more response formats desired by client, with preferred formats listed first","text/xml","Zero or more (optional)"

All parameter names are listed here using mostly lower case letters. The capitalization of parameter values when encoded using Keyword Value Pairs shall be
case insensitive, meaning that parameter names may have mixed case or not (see Subclause 11.5.2 [OGC 06-121r3]).



There are two possible ways to send an GetCapabilities Request: via HTTP GET and HTTP POST.

----------------
GET request
----------------

::

  http://localhost/istsos/demo?request=getCapabilities&sections=serviceidentification,serviceprovider,operationsmetadata,contents&service=SOS&version=1.0.0



-----------------
POST request
-----------------

::

   http://localhost/istsos/demo

.. code-block:: xml

	<?xml version="1.0" encoding="UTF-8"?>
	<sos:GetCapabilities
	   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	   xsi:schemaLocation="http://schemas.opengis.net/sos/1.0.0/sosAll.xsd"
	   xmlns:sos="http://www.opengis.net/sos/1.0"
	   xmlns:gml="http://www.opengis.net/gml/3.2"
	   xmlns:ogc="http://www.opengis.net/ogc"
	   xmlns:om="http://www.opengis.net/om/1.0" 
	   version="1.0.0" service="SOS">
		<section>serviceidentification</section>
		<section>serviceprovider</section>
		<section>operationsmetadata</section>
		<section>contents</section>
	</sos:GetCapabilities>


    

