.. _installation:

==============
Installation
==============

---------------------------------------------
Installation of the software on Ubuntu 14.04
---------------------------------------------
This part of the tutorial provides instruction on installing istSOS on a Linux Operating System based on Debian distribution. Nevertheless, even though extensive testing has been conducted in this environment only, istSOS is developed in Python which is known for its cross platform support and existing installation are recorded in Windows ® systems and OS X Apple's operating system should be supported too. Interested users may look at the istSOS Website or ask support on the mailing list.

**1) Install PostgreSQL and PostGIS**

::
    
    sudo apt-get install postgresql postgresql-9.3-postgis-2.1 pgadmin3
    
**2) Configure postgreSQL password**

::
    
    sudo -u postgres psql
    alter user postgres password '*******'; 

.. note:: Ctrl-D to exit from psql console

.. warning:: the python code must be in the PYTHONPATH.

.. seealso:: http://sphinx.pocoo.org/markup/desc.html
    
**3) Install Apache2 and mod_wsgi**

::

    sudo apt-get install apache2 libapache2-mod-wsgi
    
**4) Install psycopg2**

::
    
    sudo apt-get install python-psycopg2


**5) Download istSOS and unpack it**

Go to `<https://sourceforge.net/projects/istsos/files/latest/download?source=files>`_ the download of the latest version of istSOS will start in 5 seconds, save the file in the Downloads folder in your home directory, then unpack executing these commands:

::
    
    cd ~/Downloads
    sudo tar -zxvf istSOS-2.1.1.tar.gz -C /usr/local/ 

**6) Set executing permission and owner for the services and logs folders**

::
    
    sudo chmod 755 -R /usr/local/istsos
    sudo chown -R www-data:www-data /usr/local/istsos/services
    sudo chown -R www-data:www-data /usr/local/istsos/logs

**7) Configure Apache and WSGI**

Open /etc/apache2/sites-enabled/000-default:

::
    
    sudo gedit /etc/apache2/sites-enabled/000-default.conf

And add the following lines just before the last VirtualHost  tag:

::

    <VirtualHost *:80>
	    # The ServerName directive sets the request scheme, hostname and port that
	    # the server uses to identify itself. This is used when creating
	    # redirection URLs. In the context of virtual hosts, the ServerName
	    # specifies what hostname must appear in the request's Host: header to
	    # match this virtual host. For the default virtual host (this file) this
	    # value is not decisive as it is used as a last resort host regardless.
	    # However, you must set it for any further virtual host explicitly.
	    #ServerName www.example.com

	    ServerAdmin webmaster@localhost
	    DocumentRoot /var/www/html

	    # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	    # error, crit, alert, emerg.
	    # It is also possible to configure the loglevel for particular
	    # modules, e.g.
	    #LogLevel info ssl:warn

	    ErrorLog ${APACHE_LOG_DIR}/error.log
	    CustomLog ${APACHE_LOG_DIR}/access.log combined

	    # For most configuration files from conf-available/, which are
	    # enabled or disabled at a global level, it is possible to
	    # include a line for only one particular virtual host. For example the
	    # following line enables the CGI configuration for this host only
	    # after it has been globally disabled with "a2disconf".
	    #Include conf-available/serve-cgi-bin.conf

           WSGIScriptAlias /istsos /usr/local/istsos/application.py
           Alias /istsos/admin /usr/local/istsos/interface
    </VirtualHost> 

.. warning::

    If you are using Apache/2.4.6 or above (like in Ubuntu 13.10 or above) 
    you could meet the "403 Forbidden" message.
    
    
    .. figure::  images/forbidden.png
   
   
    In that case additional setup shall be made. In the “000-default.conf” 
   
    ::
        
        [...]
               WSGIScriptAlias /istsos /usr/local/istsos/application.py
               Alias /istsos/admin /usr/local/istsos/interface
               <LocationMatch /istsos>
                   Options +Indexes +FollowSymLinks +MultiViews
                   AllowOverride all
                   Require all granted
               </LocationMatch>
        </VirtualHost> 
    
**8) Restart the Apache web server**

::

    sudo service apache2 restart 
    
**9) Create your PostGIS database**

For Postgresql 9.1 and later versions:

::

    sudo -u postgres createdb -E UTF8 istsos
    sudo -u postgres psql -d istsos -c 'CREATE EXTENSION postgis'

.. warning::

    For older versions of postgresql:
    
    ::
        
        sudo -u postgres createdb -E UTF8 istsos

        sudo -u postgres psql -d istsos \
          -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql

        sudo -u postgres psql -d istsos \
          -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql

------------------------------
Installation using deb package
------------------------------

**1) Download istSOS package**

Go to `<https://sourceforge.net/projects/istsos/files/latest/download?source=files>`_ the download of the latest deb of istSOS will start in 5 seconds, save the file in the Downloads folder in your home directory, then install executing these commands:

::
    
    cd ~/Downloads
    sudo dpkg -i python-istsos_<version>.deb
    sudo apt-get -f install 

This command will install all the required dependencies, with the exception of PostgreSQL and PostGIS as the database is not mandatory. In fact it could reside on other servers.


**2) Create your PostGIS database**

To install and configure the database, plese go to the 'Installation of the software on Ubuntu 14.04' paragraph and see the procedure explained at point 1, 2, and 9.

--------------------------------
Installation on windows 7 and 8
--------------------------------

**1) install python**

Download python 2.7 from `<https://www.python.org/downloads/>`_ and install it. Check if the python path is in the Environment variables:

::

    Computer > properties > advanced system settings > Environment Variables.
    Check if the python27 exists in the variable Path, if not add ‘;C:\Python27\’

**2) install postgreSQL with PostGIS**

Get PostgreSQL from `<http://www.enterprisedb.com/products-services-training/pgdownload#windows>`_ and install it.

.. note::
    During the installation configure the password to be ‘postgres’.
    Install postGIS 2.1 using the application Stack Builder at the end of the installation of   
    postgreSQL. Check the option to create a new database and call it ‘istsos’


**3) install apache 2.2**

download Apache 2.2  (`<http://mirror.switch.ch/mirror/apache/dist//httpd/binaries/win32/>`_) and install it using the .msi file. 

.. warning::
    If an error signals a missing dll, download and install Microsoft Visual C++, then try again to install Apache. If the error persists, download the missing dll from `<http://www.dll-files.com/dllindex/index-m.shtml>`_ and copy into the /windows/system32 folder and reboot the system.

**4) install mod_wsgi**

get the apache module mod_wsgi (`<http://www.lfd.uci.edu/~gohlke/pythonlibs/#mod_wsgi>`_) for apache 2.2 and python 2.7 and copy it in the folder / modules of the Apache installation folder.

**5) install extra modules**

Download this extra modules and install them:

* psycopg2: `<http://www.stickpeople.com/projects/python/win-psycopg/>`_
* python-dateutil: `<http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-dateutil>`_
* six: `<http://www.lfd.uci.edu/~gohlke/pythonlibs/#six>`_

**6) install istSOS**

Download istSOS (`<http://sourceforge.net/projects/istsos/files/>`_) and unpack under the disk C: so that will be a folder C:\istsos

**7) Configure apache2**

Go to the folder where Apache is installed, modify the permissions of conf/httpd.conf and conf/extra/httpd-vhosts.conf so that they are writable from Everyone.
Open conf/httpd.conf with a text editor and add this line:

::

    LoadModule wsgi_module modules/mod_wsgi.so #close to the others LoadModule lines
    
    Uncomment the line 'Include conf/extra/httpd-vhosts.conf' (remove the #) 

Open conf/extra/httpd-vhosts.conf, delete the two examples of <VirtualHost> and paste the following code. Modify the paths so they correspond to the Apache and istSOS folders.

::

    <VirtualHost *:80>
            ServerAdmin webmaster@localhost
            #DocumentRoot "C:/istsos/interface"
            DocumentRoot "C:/Apache2/htdocs"
            <Directory />
                    Options FollowSymLinks
                    AllowOverride None
            </Directory>

            #<Directory C:/istsos/interface/>
            <Directory C:/Apache2/htdocs/>
                    Options Indexes FollowSymLinks MultiViews
                    AllowOverride None
                    Order allow,deny
                    allow from all
            </Directory>
            
            ScriptAlias /cgi-bin/ "c:/Apache2/cgi-bin/"
            <Directory "c:/Apache2/cgi-bin">
                    AllowOverride None
                    Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
                    Order allow,deny
                    Allow from all
            </Directory>

            ErrorLog "c:/Apache2/logs/error.log"
            LogLevel warn
            CustomLog "c:/Apache2/logs/access.log" combined
            Alias /doc/ "c:/Apache2/manual/"
           
            <Directory "c:/Apache2/manual/">
                    Options Indexes MultiViews FollowSymLinks
                    AllowOverride None
                    Order deny,allow
                    Deny from all
                    Allow from 127.0.0.1
            </Directory>
           
            WSGIScriptAlias /istsos "c:/istsos/application.py"
            <Location "/istsos">
                    Options Indexes MultiViews FollowSymLinks
                    AllowOverride None
                    Order deny,allow
                    Deny from all
                    Allow from 127.0.0.1
            </Location>
            Alias /istsos/admin "c:/istsos/interface"
    </VirtualHost>

**8) restart Apache 2.2**

Restart apache 2.2 using the icon or:

::

    control panel > system and security > administrative tools > services
    click on Apache 2.2 and then on restart.

-----------------------
Check the installation
-----------------------

Now istSOS is up and running. Open a web browser and go to `<http://localhost/istsos/admin>`_. You should see the istSOS Web Admin page. 

.. note::
    If an error occurs, take a look at the Apache error log with this command to understand what’s going wrong
    
    In *Ubuntu* try:
    
    :: 
    
        tail -f /var/log/apache2/error.log 
    
    In Windows open the file:
    
    :: 
        
        <Apache2.2 folder>\logs\error.log














