.. _obclass:

=========================
Get Observation Classes
=========================

When a GetObservation is requested istSOS:

* creates a *filter* object 
* passes the *filter* object to the *responder* that based on filters creates the *observations* object
* passes the *observations* object to the *renderer* to convert the information in appropriate requested outputFormat


.. py:class:: sosGOfilter

    this class contain all the filters according to the GetObservation request performed
    
    :param str request: the request, "getobservation"
    :param obj sosConfig: the configuration preference of istSOS instance
    :param str service: the service name "SOS"
    :param str version: the SOS version requested
    :param str offering: the requeste offering name
    :param list observedProperty: the list of observed properties names as string
    :param str responseFormat: the name of the desired output format
    :param str srsName: the name of the desired reference system 
    :param list eventTime: list of time intervals (list of two isodate) and/or time instants (list of one isodate), for example: *[ [2014-10-11T12:00:00+02:00, 2014-11-11T12:00:00+02:00], [2014-13-11T12:00:00+02:00] ]*
    :param list procedure: list of procedure names as string
    :param list featureOfInterest: list of feature of interest names as string
    :param str featureOfInterestSpatial: the SQL WHERE clause to apply the OGC filter expression in XML format specified in the request
    :param str result: the SQL WHERE clause to apply the OGC property operator in XML format specified in the request 
    :param str resultModel: the model to represent the result (*om:Observation*)
    :param str responseMode: the response mode (*inline*)
    :param str aggregate_interval: the aggregation interval in ISO 8601 duration
    :param str aggregate_function: the function to use for aggregation (one of: "AVG","COUNT","MAX","MIN","SUM")
    :param str aggregate_nodata_qi: the quality index value to use for representing no data in aggregated time serie
    :param bool qualityIndex: if the quality index shall be returned (*True*) or not (*False*)
    

.. py:class:: observations

    The class that contain all the observations related to all the procedures

    :param obj offInfo: the general information about offering name, connection object, and configuration options
    :param str refsys: the uri that refers to the EPSG refrence system
    :param obj filter: the filter object that contains all the parameters setting of the GetObservation request
    :param list period: a list of two values in *datetime*: the minimum and maximum instants of the requested time filters
    :param obj reqTZ: the timezone in *pytz.tzinfo*
    :param list obs: list of *Observation* objects
    
.. py:class:: Observation

    The obsevation related to a single procedure
    
    :param str id_prc: the internal id of the selected procedure
    :param str name: the name of the procedure
    :param str procedure: the URI name of the procedure
    :param str procedureType: the type of procedure (one of "insitu-fixed-point","insitu-mobile-point","virtual")
    :param list samplingTime: the time interval for which this procedure has data [*from*, *to*] 
    :param str timeResVal: the time resolution setted for this procedure when registered in ISO 8601 duration
    :param list observedPropertyName: list of observed properties names as string
    :param list observedProperty: list of observed properties URI as string
    :param list uom: list of unit of measure associated with the observed properties according to list index
    :param str featureOfInterest: the feature of interest name
    :param str foi_urn: the feature of interest URI
    :param str foiGml: the GML representation of the feature of interest (in istSOS is only of type POINT)
    :param str srs: the epsg code
    :param str refsys: the URI of the reference system (srs)
    :param float x: the X coordinate
    :param float y: the Y coordinate
    :param str dataType: the URN used for timeSeries data type
    :param str timedef: URI of the time observed propertiy
    :param list data: the list of observations as list of values (it is basically a matrix with fields as columns and measurements as rows) 

    
        .. note::
        
            data get different columns depending on procedure type and qualityIndex parameter.
            
            The following rules appies:
            
            * the first field is always the time
            * if the procedure is mobile the second, third and fourth columns are the location
            * the other columns are the values of the observed properties
            * if the qualityIndex (qi) parameter is True then values of observed properties are alternated with the corresponding quality index
            
            so for example we could have different row type:
            
            1. [2014-10-11T12:00:00+02:00, 0.2, 81.42] -> [time, rain value, humidity value]
                (insitu-fixed-point measuring rain and humidity)
            2. [2014-10-11T12:00:00+02:00, 0.2, 210, 81.42, 200] -> [time, rain value, rain qi, humidity value, humidity qi]
                (insitu-fixed-point measuring rain and humidity with qualityIndex=True)
            3. [2014-10-11T12:00:00+02:00, 8.96127, 46.02723, 344.1, 0.2, 81.42] -> [time, x, y, z, rain value, humidity value]
                (insitu-mobile-point measuring rain and humidity)
            4. [2014-10-11T12:00:00+02:00, 8.96127, 46.02723, 344.1, 0.2, 210, 81.42, 200] -> [time, x, y, z, rain value, rain qi, humidity value, humidity qi]
                (insitu-mobile-point measuring rain and humidity)
        
        
