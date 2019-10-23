
=================================
GetObservation
=================================

--------------
Introduction
--------------

The GetObservation operation is designed to query a service to retrieve observation data structured according to the Observation and Measurement specification. Upon receiving a GetObservation request, a SOS shall either satisfy the request or return an exception report.


-   **GetObservation parameters:** 

         .. csv-table:: *Table-1: GetObservation operation request URL parameters [OGC 06-009r6]*
	       :header: "Parameter","Description","Definition","Multiplicity and Use"
	       :widths: 20, 40, 20,20

	       "request","getObservation is designed to request detailed sensor metadata","getObservation","One (mandatory)"
	       "service","Service type identifier","SOS","One (mandatory)"
	       "version","Specification version for operation","1.0.0","One (mandatory)"
	       "srsName","Defines the spatial reference system that should be used for any geometries that are returned in the response.","This must be one of the advertised values in the offering specified in gml:srsName elements.","One (Optional)"
	       "offering","Specifies the offering URI advertised in the GetCapabilities document. All of the following parameters are dependent on the selected offering.","This must match the gml:name of the offering or be constructed as a URL with a fragment identifier resolving to the offering gml:id.","One (mandatory)"
	       "eventTime","Specifies the time period(s) for which observations are requested. This allows a client to request observations from a specific instant, multiple instances or periods of time in the past, present and future. The supported range is listed in the selected offering capabilities","ogc:temporalOps (validtime format is yyyy-MM-ddThh:mm:ss/yyyy-MM-ddThh:mm:ss)","Zero or many (Optional)"
	       "procedure","The procedure parameter specifies the sensor system(s) for which observations are requested.It defines a filter for the procedure property of the observations.","[all comma-separed valid sensors from the GetCapabilities]","Zero or many (Optional)"
	       "observedProperty","urn:ogc:def:phenomenon:OGC:1.0:depth","mandatory"
	       "featureOfInterest","Specifies the feature for which observations are requested. This can either be represented by a reference to a feature ID advertised in the capabilities document or can be a spatial constraint.","ADD","Zero or many (Optional)"
	       "resultModel","Provides a place to put in OGC filter expressions based on property values. This instructs the SOS to only return observations where the result matches this expression.","ADD","Zero or many (Optional)"
	       "responseFormat","Specifies the desired resultFormat MIME content type for transport of the results (e.g. TML, O&M native format, or MPEG stream out-of-band). The supported output formats are listed in the selected offering capabilities. Desired output format of the getObservation operation. This can be a MimeType or QName for example.","text/xml;subtype=”sensorML/1.0.0”","One (mandatory)"
	       "responseMode","Specifies whether results are requested in-line, out-of-band, as an attachment, or if this is a request for an observation template that will be used for subsequent calls to GetResult. This is provided to allow the client to request the form of the response. The value of resultTemplate is used to retrieve an observation template that will later be used in calls to GetResult. The other options allow results to appear inline in a resultTag (inline), external to the observation element (out-of-band) or as a MIME attachment (attached).","inline, out-of-band, attached, resultTemplate","Zero or many (Optional)"



----------------
GET request
----------------

getObservation:

::

   http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=workshop&procedure=P_LUGANO&eventTime=2013-01-01T00:00:00+01/2013-02-4T17:00:00+01,2013-01-30T17:30:00+01&observedProperty=rainfall&responseFormat=text/xml;subtype='sensorML/1.0.0'&service=SOS&version=1.0.0

getObservationBBOX:

::

   http://localhost/istsos/demo?service=SOS&request=GetObservation&offering=workshop&observedProperty=temperature&responseFormat=text/xml;subtype='sensorML/1.0.0'&service=SOS&version=1.0.0&featureOfInterest=&BBOX=[713800,89915 713830,89940(,21781)]&service=SOS&version=1.0.0

-----------------
POST request
-----------------

::

   http://localhost/istsos/demo/



getObservation.xml

-  :download:`getObservation.xml <xml/getObservation.xml>`
-  :download:`getObservation2.xml <xml/getObservation2.xml>`
-  :download:`getObservation4.xml <xml/getObservation4.xml>`



`getObservation3.xml`

`getObservationBBOX.xml`

`getObservationDWithin.xml`

`getObservationQualityIndex.xml`


