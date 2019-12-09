.. _ws_datavalidation:

==================================
Data validation with quality index
==================================

istSOS is bundled with an automatic data validation. In the next paragraphs we
will see 3 levels of validation.

.. figure::  images/qi.png
    :align:   center
    :scale:   100

**The data quality index configuration panel**

Here you can change the value and the meaning of istSOS quality indexes

.. figure::  images/qi-panel.png
    :align:   center
    :scale:   100

**Raw data quality index**

For every new inserted observed property the raw data quality index is
assigned (by default QI 100 Raw data). This quality index suggests that
the observation data type is correct, which means that istSOS checks if
the measure inserted is in a numeric type.

**Correct quality index**

In the **observed properties** panel, for each observed property, you can define
specific constraint based on logical operators (greater than, Lower than,
between and value list). This is the place where you can set general quality
index check for each Observed Property. For instance a percentage (%) observed
property can use a constraint of type “Between”, because the values can be
between 0% and 100%.

**Statistical quality index**

The statistical QI is more granular. This is set when you create a new
procedure and it will be specific only to the new procedure created. For
instance in the case of temperature measurements, we know that in our region
temperature never goes under -20°C and over 40°C, so we can put as correct
QI the “between” constraint. But a new sensor deployed on top of a mountain
the limits are different and the QI constraint can be more specific for this
station (between -20° and +20°C).


Testing the quality index check
-------------------------------

Lets try to load some data that will better explain the "quality index check"
functionality. Sample data present under qi folder in your dataset:

.. code-block:: csv

    urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature
    2015-06-03T15:30:00+01:00,T_LUGANO,150
    2015-06-03T15:40:00+01:00,T_LUGANO,62
    2015-06-03T15:50:00+01:00,T_LUGANO,25

Open a terminal and…

If installed from source

.. code-block:: bash

    cd /usr/local/istsos


.. code-block:: bash

    cd /usr/share/istsos/

Then import data with errors..

.. code-block:: bash

    python scripts/csv2istsos.py -p T_LUGANO \
    -u http://localhost/istsos -s demo \
    -w ~/Desktop/Tutorial/qi

Now check what happens executing a getObservation request:

`http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=T_LUGANO&eventTime=2015-06-03T15:20:00+01:00/2015-06-03T15:50:00+01:00&observedProperty=temperature&responseFormat=text/plain&qualityIndex=True
<http://localhost/istsos/demo?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=T_LUGANO&eventTime=2015-06-03T15%3A20%3A00%2B01%3A00%2F2015-06-03T15%3A50%3A00%2B01%3A00&observedProperty=temperature&responseFormat=text/plain&qualityIndex=True>`_

Looking at the result you can note the different quality indexes associated
with the measures:

.. code-block:: csv

    urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:procedure,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature,urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature:qualityIndex
    2015-06-03T15:30:00+01:00,T_LUGANO,150.000000,100
    2015-06-03T15:40:00+01:00,T_LUGANO,62.000000,110
    2015-06-03T15:50:00+01:00,T_LUGANO,25.000000,200

- The first measure (150) didn’t pass the "acceptable"  quality check and
  didn’t get a 110 index
- The second (62) pass the "acceptable"  quality check but didn’t pass the
  "reasonable" quality check and didn’t get a 200 index
- The third measure (25) passed both the "acceptable" and "reasonable" quality
  check so it get a 200 index
