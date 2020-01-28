.. _notification:

=================================
istSOS-WNS: Notification Service
=================================

the istSOS-WNS is a service gathering data from an istSOS database and sending a notification to the users after testing the retrieved data to meet some conditions. The systems is divided in three parts: a database for storing the information about the notifications, the users and the registrations of the users to the notifications; a database of the istSOS service storing the actual data received from external sensors; and a scheduler that periodically runs the functions to retrieve the data, test it and send the notifications to the registered users. The system also do a notification on a twitter account.

The following features are supported:
	* creation/deletion of notifications
	* creation/deletion of users
	* subscription/unsubscription of user to notification
	* request old notification

istSOS-WNS database schema
============================

The wns schema is represented below.

.. figure::  images/WNSschema.png
   :align:   center
   :scale:   70



Activation of istSOS-WNS
=========================

By default the istWNS use the database connection of the default service but you could specify a different db setting connection parameters editing the default.cfg file. 

::

	[connectionWns]
	dbname = istsos
	host = 127.0.0.1
	user = postgres
	password = postgres
	port = 5432

The other parameter reported below are used to send notification via email or twitter

::

	[mail]
	usermail = mail@notifier.com
	password = ""
	smtp = ""
	port = ""

	[twitter]
	oauth_token = ""
	oauth_secret = ""
	consumer_key = ""
	consumer_secret = ""

.. warning:: 
	
	Actually the system update the status on twitter and can send notification via email.

To setup the Web Service do this GET request:

::

	http://localhost/istsos/wns/setup

This will create a notification.asp file under the wns/ folder, where the notification function are stored and create a schema in the istSOS-WNS database.


Create a notification
======================

It’s possible to create two type of notification, 

	* **Simple notification**, that execute a getObservation and compare the results with a condition
	* **Complex observation**, the user write a specific requests and validation function in python

Method 1: simple notification
-----------------------------

Do a POST request to:

::

	http://localhost/istsos/wns/notification


with the following parameter

	a. name: the function name [mandatory]
	b. description: the description indicates what the function does [mandatory]
	c. period: expressed in ISO period format, is the interval over witch the getObservation will be performed, starting from now i.e. the last 2 hours. [optional]
	d. interval: expressed in minutes [mandatory]
	e. service: the service name [mandatory]
	f. condition: the condition describes in which case the notification will be performed. Every element retrived with the getObservation is tested again this contion, and as soon one element satisfies it the notification is triggered [mandatory]
	g. params: this is used to build a getObservation request. The offering, observedPropertiy and procedure are mandatory [mandatory]
	h. store: if true, store the result into the DB [optional]

Example:

::

    { 
        "name": "arduino_heat", 
        "description": "check arduino DHT11 heat­index", 
        "interval": 20, 
        "params": { 
            "offering":"temporary", 
            "observedProperty":"air:heat:index", 
            "procedure":"ARDUINO" 
        }, 
        "condition": "> 26", 
        "service": "demo", 
        "period": "PT1H", 
        "store": true 
	} 
	
Method 2: complex notification
------------------------------

create a python function with the following constraint:

	a. The content of the function must have the structure of the extract below, retrieving the data, handling it and checking a condition to send out notifications.
	b. Pay attention to the function name you choose, because the exact name has to be used in the next step. The name also has to be unique, to avoid potential overriding.
	c. Every function must implement the notify() method, be sure to import the correct file (wns.notificationScheduler). The two lines specified in the extract should be copied in your method, to make sure you import the correct file.

	d. The ns.notify() method takes three arguments:
		i.	functionName of the method you defined [mandatory] 
		ii.	a python dict containing the message to send via twitter or mail [mandatory]
		iii.	Status: the last parameter is a flag, if True, the Notifier update the status of the twitter account [Optional, default True]. 

	e. A notify dict with the twitter and mail message to send. The two message cold be differnt because whit twitter you ave the constraint of 140 character. 

Example:

.. code-block:: python

	def meanTemp():
	    import datetime
	    import time
	    from pytz import timezone
	    now = datetime.datetime.now().replace(tzinfo=timezone(time.tzname[0]))
	    endDate = now.strftime('%Y-%m-%dT%H:%M:%S%z')
	    eventTime = now - datetime.timedelta(hours=5)
	    startDate = eventTime.strftime('%Y-%m-%dT%H:%M:%S%z')

	    startDate = datetime.datetime(2015,7,12,15,00,0, tzinfo=timezone(time.tzname[0])).strftime('%Y-%m-%dT%H:%M:%S%z')
	    endDate = datetime.datetime(2015,7,12,16,00,0, tzinfo=timezone(time.tzname[0])).strftime('%Y-%m-%dT%H:%M:%S%z')

	    rparams = {"service": "SOS", "offering": "temporary", "request": "GetObservation", 
	                "version": "1.0.0", "responseFormat": "application/json", 
	                "observedProperty": "air:temperature", "procedure": "T_BELLINZONA"}
	    rparams['eventTime'] = str(startDate) + "/" +str(endDate)

	    import lib.requests as requests
	    res = requests.get('http://localhost/istsos/demo', params=rparams)

	    result = res.json()['ObservationCollection']['member'][0]['result']['DataArray']['values']

	    mean = 0
	    count = 0

	    for el in result:
	        if float(el[1]) != -999.9:
	            mean += float(el[1])
	            count += 1

	    if len(result) == 0:
	        message = "Cannot make mean with no data"
	    else:
	        mean = mean / count
	        message = "The mean temp in Bellinzona in the last hour: "  + str(mean)


	    # this structure is mandatory to send notification
	    notify = {
	        "twitter": {
	            "public": message,
	            "private": message
	        },
	        "mail":{
	            "subject": "mean temp from T_BELLINZONA",
	            "message": message
	        }
	    }

	    # these line are mandatory
	    import wnslib.notificationScheduler as nS
	    nS.notify('meanTemp',notify, True)


do this POST request:

::
 
	http://localhost/istsos/wns/notification
	
with the following params:
	* name: function name [mandatory]
	* description: a little function description [mandatory]
	* interval: interval [mandatory]
	* function: path to function file, plese note that the file must be on the server [mandatory]
	* store: if true, store the result into the DB [optional]

Example:

::

	{
		"name": "meanTemp",
		"description": "last hour temp in Bellinzona",
		"interval": 60,
		"function": "path/to/function.py",
		"store": true
	}


Delete notification
-------------------

It's possible delete a notification with this DELETE request:

::

	http://localhost/istsos/wns/notification/<notification_id> 

.. warning ::
	You can delete a notification only if no user are subscribed


List of available notification
------------------------------

To see all available notification function do this GET request:

::

	http://localhost/istsos/wns/notification


Register a user
===============

to subscribe to a notification and receive update you must create a user and provide some information to contact you.
do this POST request:

::

	http://localhost/istsos/wns/user

with the following params:

	a. username: is the name that will be used to recognise the user [mandatory]
	b. email: a user email [mandatory]
	c. twitter: twitter id, mandatory if you will recieve notification via twitter private message [optional]
	d. tel: mobile phone number, mandatory if you will recieve notification via mobile phone (actually not supported) [optional]
	e. fax, address, zip, city, state, country: additional info about the user [optional]
	f. name, surname: additional info about the user [mandatory]

Example:

::

	{
		"username": "userName",
		"email": "user.name@provider.com",
		"twitter": "userTwitter",
		"tel": "+41123456789",
		"fax": "+41123456080",
		"address": "via test",
		"zip": "1234",
		"city": "",
		"state": "",
		"country": "",
		"name": "Pinco",
		"lastname": "Pallino"
	}


Delete a user
-------------

It's possible to remove user with this DELETE request:

::

	http://localhost/istsos/wns/user/<user_id> 

.. warning ::
	When you delete a user it automatically unsubscribe from notifications


Subscribe to a notification
===========================

To receive notification you must subscribe to an existing notification, do this POST request

::

	http://localhost/istsos/wns/user/<user_id>/notification/<notification_id>

with the following params
	1. data: array of how would you like to receive the notification [mandatory]
	

::

	{
	    "data": ["mail", "twitter"]
	}


Unsubscribe to a notification
-----------------------------

Unsubscribe a user from notification with this DELETE request

::

	http://localhost/istsos/wns/user/<user_id>/notification/<notification_id>


Check user subscription
-----------------------

Check a user subscription to notification with this GET request

::

	http://localhost/istsos/wns/user/<user_id>/notification


Activate the scheduler
======================

To activate the scheduler move to istsos root filder and run the scheduler script

::

	cd /usr/local/istsos
	python scheduler_notification.py



Store the notification
======================

If you want to store every notification result, set the store flag when you create a new notification.

If you add a new complex notification the function must return the message to save.

.. code-block:: python

	def notFunction():
	    
	    # get your data

	    # check condition

	    message = "your message to notify"

	    notify = {
	        "twitter": {
	            "public": message,
	            "private": message
	        },
	        "mail":{
	           "subject": "mean temp",
	           "message": message
	       }
	    }

	    import wnslib.notificationScheduler as nS
	    nS.notify('notFunction',notify, True)

	    # return the message to save it could be a python dict or a string
	    return {"message": message}


Request old notification
------------------------

To request old notification do this GET request:

::

	http://localhost/istsos/wns/response/<notification_id>


by default the system return only the last notification, if you want more notification, or you want to search in a specific period, it's possible to add some params to the request

	* **limit**: number, how many response return, if 'all' return all notification
	* **stime**: start date in isoformat (2015-10-01T0:00:00+02:00)
	* **etime**: end date in isoformat (2015-10-07T16:30:00+02:00)

::

	http://localhost/istsos/wns/response/<notification_id>?limit=all&stime=2015-10-01T0:00:00+02:00&etime=2015-10-07T16:30:00+02:00 
