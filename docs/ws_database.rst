.. _ws_database:

======================
Database configuration
======================

Decide where to install the PostgreSQL database. Most of the times installing the
on the database on the same machine is ok.

**Install PostgreSQL and PostGIS**

.. code-block:: bash

    sudo apt install postgresql postgis


.. *Optionally install also PGAdmin*

.. .. code-block:: bash

..     sudo apt-get install pgadmin3


**Change the postgreSQL password**

.. code-block:: bash

    sudo -u postgres psql -c "alter user postgres password 'postgres';"

.. note::

    replace the example password with something stronger if you like

**Create the istSOS database**

.. code-block:: bash

    sudo -u postgres createdb -E UTF8 istsos
    sudo -u postgres psql -d istsos -c 'CREATE EXTENSION postgis'

Now your istSOS server is ready to be used.