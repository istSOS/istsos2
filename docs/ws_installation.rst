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

.. parsed-literal::

    sudo dpkg -i python3-istsos_\ |version|\.deb;sudo apt-get -f -y install

This command will install all the required dependencies, with the exception of
PostgreSQL and PostGIS. In fact it could reside on other servers. Go to the
:ref:`ws_database` for instruction on how to configure the database.

.. note::

    If everything has gone well, you should see the administration page at
    this address:
    `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_

---------------------------------
Installation on Linux from source
---------------------------------

The dependencies need to be installed manually or using apt-get command.
Please refer also to specific software installation procedures.

**Download istSOS and unpack it**

Please go to `https://sourceforge.net/projects/istsos/files 
<https://sourceforge.net/projects/istsos/files/>`_, and chose the current
istSOS-|version|.tar.gz file. Save the file in the Downloads folder in your
home directory, then unpack it executing these commands:

.. parsed-literal::

    sudo tar -zxvf istSOS-\ |version|\.tar.gz -C /usr/share/

**Set executing permissions and the owner for the services and logs folders**

.. code-block:: bash

    sudo chmod 755 -R /usr/share/istsos
    sudo chown -R www-data:www-data /usr/share/istsos/services
    sudo chown -R www-data:www-data /usr/share/istsos/logs

**Install Python3, Apache2 and mod_wsgi**

.. code-block:: bash

    sudo apt install python3 python3-pip apache2 libapache2-mod-wsgi-py3

**Install Python3 dependencies**

.. code-block:: bash

    sudo pip3 install -r /usr/share/istsos/requirements.txt

**Configure Apache and WSGI**

Open /etc/apache2/sites-enabled/000-default.conf, and add the following
configuration:

.. code-block:: apacheconf
   :emphasize-lines: 9-11
   :linenos:

    <VirtualHost *:80>

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        WSGIScriptAlias /istsos /usr/share/istsos/application.py
        Alias /istsos/admin /usr/share/istsos/interface/admin
        Alias /istsos/modules /usr/share/istsos/interface/modules

        <LocationMatch /istsos>
            Options +Indexes +FollowSymLinks +MultiViews
            AllowOverride all
            Require all granted
        </LocationMatch>

    </VirtualHost>

**Optional: configure WSGI with Python virtual environments**

If you are using a Python virtual environment, and istSOS is the only
wsgi application running on your apache server then add this line to the
/etc/apache2/mods-enabled/wsgi.conf file:

.. code-block::

   WSGIPythonPath /PATH_TO_YOUR_VENV/venv/lib/python3.X/site-packages/


**Restart the Apache web server**

.. code-block:: bash

    sudo service apache2 restart

.. note::

    If everything has gone well, you should see the administration page at
    this address: `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_


Go to the :ref:`ws_database` for instruction on how to configure the database.
