.. _acquisition:

=====================================================
istSOS scheduler for data acquisition
=====================================================

With istSOS you can configure the acquisition of new observations using a 
time-based scheduler. 

How it works
-------------

The istSOS scheduler relies on the Advanced Python Scheduler library (`APScheduler 2.1.2 <http://apscheduler.readthedocs.org/en/v2.1.2/>`_).

In the istSOS directory there is the **scheduler.py** script. If executed, it will scan the **services** folder searching for files with ***.aps** extension and if present it will schedule time-based job based on you configuration choices.

To create a job you have to create a file (e.g. demo.aps) inside the folder of the istSOS instance you want the acquisition is executed (e.g. services/demo/demo.aps).

The APS file example
--------------------

Tipically a remote sensor is sending data to a FTP server where all the raw files are stored waiting to be loaded into istSOS. with the scheduler you can decide the acquisition frequency.

The next example is an aps file that convert one (or more if present in the folder) proprietary CSV file located in a predefined folder. (for more examples on how to implement proprietary csv file converter go to the :doc:`Insertion of new observations </insert>` page)

To configure the acquisition insterval between executions check the `APScheduler decorator syntax <http://apscheduler.readthedocs.org/en/v2.1.2/cronschedule.html#decorator-syntax>`_. 

File location: /usr/local/istsos/services/demo/demo.aps

.. code-block:: python
  :linenos:
  
  @sched.interval_schedule(minutes=10, start_date='2014-01-01 00:00')
  def importMaggia():
    from scripts.converter import csv
    # Configuring the Converter
    conv = csv.CsvImporter('MAGGIA', {
        "headrows": 0,
        "separator": ",",
        "filenamedate": {
          "format": '%Y%m%d%H%M%S',
          "remove": ['maggia_', '.dat']
        },
        "datetime": {
          "column": 0,
          "format": '%Y-%m-%d %H:%M:%S',
          "tz": '+01:00'
        },
        "observations": [{
          "observedProperty": "urn:ogc:def:parameter:x-istsos:1.0:river:water:height",
          "column": 1
        }]
      },
      'http://localhost/istsos', 'demo',
      '/data/maggia', 'maggia_*.dat',
      debug=True,
      archivefolder='/data/archive/maggia'
    )
    # Converting raw data to text/csv;subtype=istSOS
    if conv.execute():
      # Send observation to istSOS
      conv.csv2istsos()


To run the scheduler:

.. code-block:: guess

  cd /user/local/istsos
  python scheduler.py 


Now every ten minutes the function will be executed and the data will be converted using the `Generic CSV converter <insert.html#generic-csv-converter-example>`_.





