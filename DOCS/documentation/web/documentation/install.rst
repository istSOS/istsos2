#############
Install istSOS package 
#############

===============
Prerequirements
===============
istSOS relies on `python <http://www.python.org/>`_ (>= 2.6), PostgreSQL/PostGIS and Apache (with `mod_python <http://www.modpython.org>`_).

In particular the follwoing python packages are required:

* psycopg2
* isodate
* gdal

==============
Software installation
==============
Teoretically the installation of these package is authomatic by using easytools, but in some cases it fails due to package errors (compilation of GDAL, etc..).

Ubuntu users may found useful aading the ubuntuGIS repository and install required packages with synapthhic. In this case the workflow for Ubuntu users is:

* install setuptools (synapthic)
* install python-dev (synapthic)
* install numpy (synapthic)
* install g++ (synapthic)
* install GDAL (synapthic)
* install psycopg2 (synapthic)
* install mod_python (synapthic)
* install postgresql-8.x-postgis (synapthic)
* download istSOS
* extract istSOS
* cd into the extracted folder
* run "sudo python setup.py install"

==============
Database setup
==============
Create the database "sos" as postgres user::

    > sudo su postgres
    > createdb sos

Make your database a spatial database::
    
    #For PostGIS < 1.5 (PostgreSQL = 8.3)
    > createlang plpgsql sos
    > psql -d sos -f /usr/share/postgresql-8.3-postgis/lwpostgis.sql
    > psql -d sos -f /usr/share/postgresql-8.3-postgis/spatial_ref_sys.sql

    #For PostGIS >= 1.5 (PostgreSQL = 8.4)
    > createlang plpgsql sos
    > psql -d sos -f /usr/share/postgresql/8.4/contrib/postgis.sql
    > psql -d sos -f /usr/share/postgresql/8.4/contrib/postgis_comments.sql
    > psql -d sos -f /usr/share/postgresql/8.4/contrib/spatial_ref_sys.sql

Create the istsos schema::

    > psql -d sos -f  ..../istSOS-1.0-rc1/DOCS/database/sos_schema.sql


=================
Configuring the service
=================
Prepare your web folder for the service::

    > sudo mkdir /var/www/sos
    > sudo mk dir /var/www/sos/sml
    > sudo chmod 777 -R /var/www/sos
    
Copy required files::

    > cp ..../istSOS-1.0-rc1/sos.py /var/www/sos/
    > cp -R ..../istSOS-1.0-rc1/DOCS/testPOST /var/www/sos/
    > cp -R ..../istSOS-1.0-rc1/istSOSconfig /var/www/sos/

Configure Apache with mod_python::

    > sudo gedit /etc/apache2/sites-enabled/000-default

Edit the file by adding the following lines::

    <Directory "/var/www/sos">
		AddHandler mod_python py
		DirectoryIndex sos.py
		PythonHandler mod_python.publisher
		PythonDebug On
		PythonPath "['/var/www/sos/istSOSconfig']+sys.path"
	</Directory>

Restart Apache::

    > sudo /etc/init.d/apache2 restart

=================
Configure istSOS
=================
istSOS has a configuration file named "sosConfig.py". This file is commented to let the user understand the possible settings available.
The available sections are:

database properties::

    connection = {
                   "user" : “postgres",
                   "password" : “1234",
                   "host" : "localhost",
                   "dbname" : "sos",
                   "port" : "5432"
                  }
    schema="istsos“

authority and version of your institution::

    #x- denote a not registered authority
    authority="x-ist"
    version=""

database EPSG codes and output axis names::

    istSOSepsg = "21781"
    x_axis = "easting"
    y_axis = "northing"
    z_axis = "altitude"
    sos_allowedEPSG = [istSOSepsg,"4326","900913"] # 900913 = Google projection

SensorML folder path::

    # n.b.: the folder must exist with the correct rigths (rw)
    sensorMLpath = "/var/www/sos/sml/“

http address of the service::

    serviceUrl = {
                  "get" : "http://localhost/sos/istsos.py",
                  "post" : "http://localhost/sos/istsos.py"
                  }

service identification::

    serviceIdentification={
                           "title" : "IST Sensor Observation Service",
                           "abstract" : "hydro-meteorological monitoring network",
                           "keywords" : ["SOS","IST","SUPSI"],
                           "fees" : "NONE",
                           "accessConstrains" : "NONE"
                           }

service provider::

    serviceProvider={
                     "providerName" : "Istituto Scienze della Terra",
                     "providerSite" : "http://istgeo.ist.supsi.ch",
                     "serviceContact" : {
                                         "individualName" : "Massimiliano Cannata",
                                         "positionName" : "Geomatica",
                                         "contactInfo" : {
                                                          "voice" : "6214",
                                                          "fax" : "6200",
                                                          "deliveryPoint" : "Via Trevano",
                                                          "city" : "Canobbio",
                                                          "administrativeArea" : "Ticino",
                                                          "postalCode" : "6952",
                                                          "country" : "Switzerland",
                                                          "email" : "info@supsi.ch",
                                                          }
                                         }
                     }









