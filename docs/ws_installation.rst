.. _ws_installation:

=====================
Installation on Linux
=====================

---------------------------------------------
Installation on Linux with the Debian package
---------------------------------------------

The easiest way to install istSOS on a Debian distribution is to use the
istSOS deb packages.

**Download the debian file from the repository**

Please go to `https://sourceforge.net/projects/istsos/files <https://sourceforge.net/projects/istsos/files/>`_
to get the latest release.

**Install the debian file**

Open a terminal and move to the folder containing the downloaded deb file.

.. code-block:: bash

    cd ~/Downloads
    sudo dpkg -i python-istsos_2.x.x.deb;sudo apt-get -f -y install

This command will install all the required dependencies, with the exception of
PostgreSQL and PostGIS. In fact it could reside on other servers.

.. note::

    If everything has gone well, you should see the administration page at
    this address:
    `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_

---------------------------------
Installation on Linux from source
---------------------------------

The dependencies need to be installed manually or using apt-get command.
Please refer also to specific software installation procedures.

**Install Apache2 and mod_wsgi**

.. code-block:: bash

    sudo apt-get install apache2 libapache2-mod-wsgi

**Install psycopg2**

.. code-block:: bash

    sudo apt-get install python-psycopg2

**Download istSOS and unpack it**

Please go to `https://sourceforge.net/projects/istsos/files <https://sourceforge.net/projects/istsos/files/>`_
, and chose the latest istSOS-2.x.x.tar.gz file. Save the file in the Downloads
folder in your home directory, then unpack it executing these commands:

.. code-block:: bash

    cd ~/Downloads
    sudo tar -zxvf istSOS-2.x.x.tar.gz -C /usr/local/


**Set executing permission and owner for the services and logs folders**

.. code-block:: bash

    sudo chmod 755 -R /usr/local/istsos
    sudo chown -R www-data:www-data /usr/local/istsos/services
    sudo chown -R www-data:www-data /usr/local/istsos/logs

**Configure Apache and WSGI**

Open /etc/apache2/sites-enabled/000-default, and add the following configuration:

.. code-block:: apacheconf
   :emphasize-lines: 9-11
   :linenos:

    <VirtualHost *:80>

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        WSGIScriptAlias /istsos /usr/local/istsos/application.py
        Alias /istsos/admin /usr/local/istsos/interface/admin
        Alias /istsos/modules /usr/local/istsos/interface/modules

    </VirtualHost>


.. note::

    If you are using Apache/2.4.6 or above (like in Ubuntu 13.10 or above) you
    could meet the "403 Forbidden" message.


    .. code-block:: apacheconf
       :emphasize-lines: 13-17
       :linenos:

        <VirtualHost *:80>

            ServerAdmin webmaster@localhost
            DocumentRoot /var/www/html

            ErrorLog ${APACHE_LOG_DIR}/error.log
            CustomLog ${APACHE_LOG_DIR}/access.log combined

            WSGIScriptAlias /istsos /usr/local/istsos/application.py
            Alias /istsos/admin /usr/local/istsos/interface/admin
            Alias /istsos/modules /usr/local/istsos/interface/modules

            <LocationMatch /istsos>
                Options +Indexes +FollowSymLinks +MultiViews
                AllowOverride all
                Require all granted
            </LocationMatch>

        </VirtualHost>

**Restart the Apache web server**

.. code-block:: bash

    sudo service apache2 restart


.. note::

    If everything has gone well, you should see the administration page at
    this address: `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_
