.. _ws_database:

======================
Database configuration
======================

Decide where to install the PostgreSQL database. Most of the times installing the
on the database on the same machine is ok.

**Install PostgreSQL and PostGIS**

.. code-block:: bash

    sudo apt-get install postgresql postgresql-9.3-postgis-2.1


*Optionally install also PGAdmin*

.. code-block:: bash

    sudo apt-get install pgadmin3


**Change the postgreSQL password**

.. code-block:: bash

    sudo -u postgres psql -c "alter user postgres password 'postgres';"

**Create your PostGIS database**

For Postgresql 9.1 and later versions:

.. code-block:: bash

    sudo -u postgres createdb -E UTF8 istsos
    sudo -u postgres psql -d istsos -c 'CREATE EXTENSION postgis'


.. note::

    For older versions of postgresql / postgis:

    .. code-block:: bash

        sudo -u postgres createdb -E UTF8 istsos
        sudo -u postgres psql -d istsos -f /usr/share/postgresql/9.x/contrib/postgis-1.5/postgis.sql
        sudo -u postgres psql -d istsos -f /usr/share/postgresql/9.x/contrib/postgis-1.5/spatial_ref_sys.sql
