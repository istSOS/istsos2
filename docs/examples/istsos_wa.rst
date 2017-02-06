
==========================
istSOS WAlib 2.0
==========================




	.. csv-table:: *Table-1: istSOS WAlib Requests*
	       :header: "url","GET","POST","PUT","DELETE"
	       :widths: 24, 19, 19, 19, 19

	       "**/istsos/operations/check**","*Unsupported*","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/operations/status**","Return for each service numbers of foi, obsProp, Proc, available operations and its status (ON-OFF-unknown)","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/operations/log**","Return the last N lines of the server log","*Unsupported*","*Unsupported*","Clear the server log"
	       "**/istsos/operations/about**","Return: istsos version, wa version","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/operations/validatedb**","*Unsupported*","Test the posted db parameters and reports if connection is active","*Unsupported*","*Unsupported*"
	       "**/istsos/operations/initialization**","Get initialization level","*Unsupported*","Set initialization level (level > 0 --> initialized)","*Unsupported*"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services**","Return a list of services name","Create a new service according posted parameters","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}**","Return the service name","*Unsupported*","Update the service name","Delete the service"
	       "**/istsos/services/{name/default}/configsections**","Return the list of sections","*Unsupported*","Update some sections of the config file","*Unsupported*"
	       "**/istsos/services/{name/default}/configsections/
	       getobservation**","Return the GetObservation settings that influence the behaviour of request vendor parameters","*Unsupported*","Update the GetObservation settings that influence the behaviour of request vendor parameters","Not for default"
	       "**/istsos/services/{name/default}/configsections/
	       identification**","Return the service identification","*Unsupported*","Update the service identification","Not for default"
	       "**/istsos/services/{name/default}/configsections/
	       geo**","Return the coordinate system settings","*Unsupported*","Update the coordinate system settings","Not for default"
	       "**/istsos/services/{name/default}/
	       configsections/connection**","Retrun the connection parameters","*Unsupported*","Update the connection parameters","Not for default"
	       "**/istsos/services/{name/default}/configsections/
	       connection/operations/validatedb**","Validateconnection parameters of the selected service","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name/default}/configsections/
	       serviceurl**","Return the server url accessible by user","*Unsupported*","Update the server url accessible by user","Not for default"       
	       "**/istsos/services/{name/default}/configsections/
	       provider**","Return the provider infos (street, phone, etc..)","*Unsupported*","Update the provider infos (street, phone, etc..)","Not for default"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/dataqualities**","Return a list of (code,desc)","Insert the new code and description in db","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/dataqualities/
	       {code}**","Return code and description","*Unsupported*","Update the code and description in db","Delete the code and description in db"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/procedures**","*Unsupported*","Insert a new procedure","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/procedures/
	       {name}**","Return details of a single procedure","*Unsupported*","Update a procedure sensorML (but not affect the database: eg. you cannot change observed properties or FOI) if sensor name is different from existing update the sensor name","Delete a procedure"
	       "**/istsos/services/{name}/procedures/
	       operations/getlist**","Return a list of procedures","*Unsupported*","*Unsupported*","*Unsupported*"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/offerings**","Return a detailed list of offerings","Insert a new offering","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/offerings/
	       {name}**","Return details of a single offering","*Unsupported*","Update offering name","Delete a offering"
	       "**/istsos/services/{name}/offerings/
	       {name}/procedures**","Return list of procedures","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/offerings/
	       {name}/procedures/{name}**","*Unsupported*","insert the procedures associated with this offering, rewriting the existing associations","*Unsupported*","Delete the procedure from offering and check that it exist at least in the temporary offering"
	       "**/istsos/services/{name}/offerings/
	       {name}/procedures/operations/memberslist**","Return list of procedures that are members of the given offering","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/offerings/
	       {name}/procedures/operations/nonmemberslist**","Return list of procedures that are not members of the given offering","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/operations/
	       getobservation/offerings/{name}/
	       procedures/{*|name|name1&name2&...}/
	       observedproperties/{name|name1&name2}/
	       eventtime/{begin}/{end}|{instant}|{last}**","Return a list of getobservation results","*Unsupported*","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/
	       operations/insertobservation**","*Unsupported*","Insert a new observations overriding existing old observations (force insert)","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/offerings/
	       operations/getlist**","Return a simplified list of offerings","*Unsupported*","*Unsupported*","*Unsupported*"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/observedproperties**","Return a list of observed properties","Insert a new observed property","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/observedproperties/
	       {name}**","Return details of a single observed property","*Unsupported*","Update an observed property","Delete an observed property"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/uoms**","Return a list of uom","Insert a new uom","*Unsupported*","*Unsupported*"
	       "**/istsos/services/{name}/uoms/
	       {name}**","Return details of a single uom","*Unsupported*","Update an uom","Delete an uom"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/epsgs**","Return a list of epsg","*Unsupported*","*Unsupported*","*Unsupported*"
	       "            ","            ","            ","            ","            "
	       "**/istsos/services/{name}/systemtypes**","Return a list of system types (fixed, mobile..)","*Unsupported*","*Unsupported*","*Unsupported*"