
""" ----------------------------------- """
""" -- USER CONFIGURATION PARAMETERS -- """
""" ----------------------------------- """
"""  this is the part to be configured  """
"""     to personalize the service      """
""" ----------------------------------- """

#database properties
connection = {
               "user" : "postgres",
               "password" : "1234",
               "host" : "localhost",
               "dbname" : "sos",
               "port" : "5432"
              }

schema="istSOS"

#define the authority and version of your istitution
#x- denote a not registered authority
authority="x-ist" 
version=""

#define database EPSG codes
istSOSepsg = "21781"
x_axis = "easting"
y_axis = "northing"
z_axis = "altitude"
sos_allowedEPSG = [istSOSepsg,"4326"]

#define SensorML folder path
sensorMLpath = "/var/www/sos/sml/"

#define virtual process folders if required
#virtual_processes_folder = "/home/ist/Desktop/istSOS-SVN/trunk/virtProc"
#virtual_HQ_folder = "/home/ist/Desktop/istSOS-SVN/trunk/virtProc/HQ_curves"

#define the http address of the service
serviceUrl = {
              "get" : "http://localhost/sos/istsos.py",
              "post" : "http://localhost/sos/istsos.py"
              }

#identify the service
serviceIdentification={
                       "title" : "IST Sensor Observation Service",
                       "abstract" : "hydro-meteorological monitoring network",
                       "keywords" : ["SOS","IST","SUPSI"],
                       "fees" : "NONE",
                       "accessConstrains" : "NONE"
                       }

#informations on service provider
serviceProvider={
                 "providerName" : "Istituto Scienze della Terra",
                 "providerSite" : "http://istgeo.ist.supsi.ch",
                 "serviceContact" : {
                                     "individualName" : "Pinco Pallino",
                                     "positionName" : "Geomatica",
                                     "contactInfo" : {
                                                      "voice" : "1234",
                                                      "fax" : "5678",
                                                      "deliveryPoint" : "Via Cippili",
                                                      "city" : "Las Vegas",
                                                      "administrativeArea" : "Nevada",
                                                      "postalCode" : "9876",
                                                      "country" : "Mars",
                                                      "email" : "info@mars.com",
                                                      }
                                     }
                 }


""" ------------------------------------------ """
""" -- EXPERT USER CONFIGURATION PARAMETERS -- """
""" ------------------------------------------ """
"""  this part has to be configured by expert  """
"""    users only, this affects the correct    """
"""          behaviour of the service          """
""" ------------------------------------------ """


#used urn to define semantic annotations
urn={
     "phenomena" : "urn:ogc:def:phenomenon:"+authority+":"+version+":",
     "dataType" : "urn:ogc:def:dataType:"+authority+":"+version+":",
     "parameter" : "urn:ogc:def:parameter:"+authority+":"+version+":",
     "process" : "urn:ogc:def:process:"+authority+":"+version+":",
     "identifier" : "urn:ogc:def:identifier:"+authority+":"+version+":",
     "keywords" : "urn:ogc:def:keywords:"+authority+":"+version+":",
     "sensor" : "urn:ogc:object:sensor:"+authority+":"+version+":",
     "procedure" : "urn:ogc:object:procedure:"+authority+":"+version+":",
     "sensorType" : "urn:ogc:def:sensorType:"+authority+":"+version+":",
     "property" : "urn:ogc:def:property:"+authority+":"+version+":",
     "feature" : "urn:ogc:object:feature:"+authority+":"+version+":",
     "role" : "urn:role:"+authority+":"+version,
     "offering": "urn:"+authority+":"+version+":offering:",
     "refsystem" : "urn:ogc:crs:EPSG:",
     "time" : "urn:ogc:def:parameter:time:iso8601"
     }

#note in array first value used as default
parameters={
           "service" : ["SOS"],
           "version" : ["1.0.0"],
           "requests" : ["getcapabilities","describesensor","getobservation","getfeatureofinterest","insertobservation","registersensor"],
           "GC_Section" : ["serviceidentification","serviceprovider","operationsmetadata","contents","all"],
           "DS_outputFormats" : ["text/xml;subtype='sensorML/1.0.0'"],
           "GO_srs" : sos_allowedEPSG,
           "GO_timeFormats" : ["ISO 8601 (e.g.: 1997-12-17T07:37:16-08)","xsi:type='TimeInstantType'","xsi:type='TimePeriodType'"],
           "GO_responseFormat" : ["text/xml;subtype='sensorML/1.0.0'","application/json","text/plain","text/xml","text/x-json"], #mime-type
           "GO_resultModel" : ["om:Observation"],
           "GO_responseMode" : ["inline"], #may be also: "out-of-band", "attached", "resultTemplate"
           }
           
parGeom = { "x" : ["x-position","east","easting","lon","longitude","x"],
            "y" : ["y-position","north","northing","lat","latitude","y"],
            "z" : ["z-position","elevation","quota","z"]
          }
          
foiGeometryType = {
    "gml:Point"     : "station",
    "gml:Polygon"   : "surface",
    "gml:Box"       : "surface"
}

serviceType={
                "codespace" : "http://opengeospatial.net",
                "value" : "OGC:SOS",
                "version" : "1.0.0"
                }

service = "SOS"

version = "1.0.0"


