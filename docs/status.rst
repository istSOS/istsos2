.. _status:

===========
Status page
===========

The aim of this page is to quickly see the status of the system. With this page it's possible to see if a procedure is loading correctly data or if it's late.
Every procedure must have the Acqusition time defined, which is used to control the status. every procedure is represented by a rectangle, and is inside another
rectangle that represent the status of the procedure.


.. figure::  images/Result.png
   :align:   center
   :scale:   50

the procedure status is divide into 3 main category:

	1. OK: In this case there is no problem, the procedure is loading data correctly and it's in time
	2. Pending: In this case the procedure is not in time, he hasn't uploaded data in time, check the exception to find a solution
	3. Verified: In this case there is a verified exception, and the system is waiting new data to confirm that the procedure is OK

All the pending procedure have a different color. The color rappresent the amount of delay. 
This color can change from orange to red. A procedure with orange color is delayed a few minutes, on the other hand a procedure with a red color is very late.


=====================
Delay rappresentation
=====================

The system can represent the status delay in two different ways:

.. figure::  images/delay-selector.png
   :align:   center
   :scale:   100

The first rappresentation the delay is expressed in time.

Whit the second rappresentation the delay is represented in cycle. 

i.e. a procedure A is loading data every 10 min, and a procedure B load data every 2 hours. If A doesn't load data from 30 minutes, A is delayed by 3 cycles.
If B doesn't load data from 3 hours is delayed by 1.5 cycles.

===========
Exception
===========

Every procedure that have the pending status should have a exception in the detail view.

.. figure::  images/Exception-min.png
   :align:   center
   :scale:   50


With the exception description you could find a solution to the problem. Once the problem is solved, it's possible to change the exception status, from pending to verified, and wait until the procedure load new data. 

.. figure::  images/Exception_status-min2.png
   :align:   center
   :scale:   80


==========
Timer
==========

It's possible to set a timer to automatically refresh the page and control the situation.

.. figure::  images/Timer.png
   :align:   center
   :scale:   100