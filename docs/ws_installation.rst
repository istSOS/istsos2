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

-----------------------------------------------------
Installation on Linux with docker-compose from source
-----------------------------------------------------

An easy way to install istSOS with PostgreSQL and PostGIS on Ubuntu is to use docker-compose.

It is possible to use this docker-compose application on any system that supports 
docker with small variations.


**Install Docker**

Please refer to `https://docs.docker.com/install/linux/docker-ce/ubuntu/ <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_
to get information about how to install the latest docker engine. Use docker version >= 19.03.8.

**Install docker-compose**

Please refer to `https://docs.docker.com/compose/install/ <https://docs.docker.com/compose/install/>`_
to get information about how to install the latest docker-compose release. Use docker-compose version >= 1.25.1.

**Clone istSOS repository**

.. code-block:: bash

    git clone https://github.com/istSOS/istsos2.git
    cd istsos2

**Build docker images**

We are building 2 images from source, postgreSQL and istSOS. Then we delete dangling 
images because istSOS use a multi-stage build.  

.. code-block:: bash

    docker-compose build
    docker rmi -f $(docker images -f "dangling=true" -q)

**Run istSOS with docker-compose**

.. code-block:: bash

    docker-compose up -d


.. note::

    If everything has gone well, you should see the administration page at
    this address:
    `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_

**Check running containers**

If docker-compose is running you should see 2 container: istsos2_istsos_1 and istsos2_istsos-db_1.

.. code-block:: bash

    docker ps

**List volumes**

Persistent data are stored in volumes. 
You can list and inspect volumes:

.. code-block:: bash

    docker volume ls
    docker volume inspect <volume-name>    

**Stop istSOS and remove containers**

You can stop and delete istSOS and postgreSQL services, data will remain in 
persistent docker volumes.

.. code-block:: bash

    docker-compose down

Note that you can re-run istSOS with the same data because 
we have not deleted any volumes.

**Remove docker volumes**

After docker-compose down you can also delete all data in volumes:

.. code-block:: bash

    docker volume rm v-istsos-pgdata
    docker volume rm v-istsos-services

**List and delete images**

After docker-compose down you can eventually delete all images:

.. code-block:: bash

    docker images
    docker rmi <images-name>

.. warning::

    Remember to disable services on your device that runs on port 80 and 5432 (e.g. 
    postgreSQL, nginx/httpd) because docker-compose expose these ports.
    
    You can edit ports section on docker-compose.yml.
    In this example we expose port 8081 instead of 80.   

        ports:

        - 8081:80

    If you have trouble in postgreSQL connection after a port change remember to 
    edit Proxy Configuration section with <http://device-ip:istsos-port/istsos> at 
    the administration page at this address:
    `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_

    Check also Proxy Configuration of the target service.

Go to the :ref:`ws_database` for instruction on how to configure the database.


---------------------------------------------------------------
Installation on Linux with docker-compose using official images
---------------------------------------------------------------

The easiest way to install istSOS with PostgreSQL and PostGIS is to use docker-compose 
that uses official istSOS and PostGIS images.  

It is possible to use this docker-compose application on any system that supports 
docker with small variations.

**Install Docker**

Please refer to `https://docs.docker.com/install/linux/docker-ce/ubuntu/ <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_
to get information about how to install the latest docker engine. Use docker version >= 19.03.8.

**Install docker-compose**

Please refer to `https://docs.docker.com/compose/install/ <https://docs.docker.com/compose/install/>`_
to get information about how to install the latest docker-compose release. Use docker-compose version >= 1.25.1.

**Create docker-compose**

Create a folder "istsos2", and inside it create and edit a new file called "docker-compose.yml".

.. code-block:: bash

    mkdir istsos2 && cd istsos2
    nano docker-compose.yml

**Configure docker-compose**

Copy and paste the following configuration in docker-compose.yml and save.

.. code-block:: docker-compose

    version: '3.7'
    services:
        istsos-db:
            image: postgis/postgis:12-2.5-alpine
            restart: always
            ports:
                - 5432:5432
            environment:
                POSTGRES_USER: postgres
                POSTGRES_PASSWORD: postgres
                POSTGRES_DB: istsos
                TZ: Europe/Zurich
            volumes:
                - v-istsos-pgdata:/var/lib/postgresql/data
        istsos:
            image: istsos/istsos:2.4.0-RC4
            restart: always
            ports:
                - 80:80
            volumes:
                - v-istsos-services:/usr/share/istsos/services
    volumes:
        v-istsos-pgdata:
        v-istsos-services:

**Create .env file**

Create and edit a new file called ".env" to set environment for all services of the compose.

.. code-block:: bash

    nano .env        


**Configure .env**

Copy and paste the following configuration and save.

.. code-block:: bash

    COMPOSE_PROJECT_NAME=istsos2      

**Run istSOS with docker-compose**

.. code-block:: bash

    docker-compose up -d

.. note::

    If everything has gone well, you should see the administration page at
    this address:
    `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_


**Check running containers**

If docker-compose is running you should see 2 container: istsos2_istsos_1 and istsos2_istsos-db_1.

.. code-block:: bash

    docker ps

**List volumes**

Persistent data are stored in volumes. 
You can list and inspect volumes:

.. code-block:: bash

    docker volume ls
    docker volume inspect <volume-name>

**Stop istSOS and remove containers**

You can stop and delete istSOS and postgreSQL services, data will remain in 
persistent docker volumes.  

.. code-block:: bash

    docker-compose istsos2 down

Note that you can re-run istSOS with the same data because 
we have not deleted any volumes.    

**Remove docker volumes**

After docker-compose down you can also delete all data in volumes:

.. code-block:: bash

    docker volume rm v-istsos-pgdata
    docker volume rm v-istsos-services

**List and delete images**

After docker-compose down you can eventually delete all images:

.. code-block:: bash

    docker images
    docker rmi <images-name>

.. warning::

    Remember to disable services on your device that runs on port 80 and 5432 (e.g. 
    postgreSQL, nginx/httpd) because docker-compose expose these ports.
    
    You can edit ports section on docker-compose.yml.
    In this example we expose port 8081 instead of 80.   

        ports:

        - 8081:80

    If you have trouble in postgreSQL connection after a port change remember to 
    edit Proxy Configuration section with <http://device-ip:istsos-port/istsos> at 
    the administration page at this address:
    `http://localhost/istsos/admin/ <http://localhost/istsos/admin/>`_

    Check also Proxy Configuration of the target service.

Go to the :ref:`ws_database` for instruction on how to configure the database.
