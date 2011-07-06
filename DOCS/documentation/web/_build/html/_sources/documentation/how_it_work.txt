#############
How it works
#############

Basic software structure
============================
istSOS has been developed with a *factory* approach using three sets of classes:
  * **filters**
  * **responders**
  * **renderers**

These sets of classes are composed by specific sub-set of classes able to handle different requests types by instantiating a **factory_filter**, a **factory_reponder** and a **factory_renderer** wich are able to call the specific classes based on the request type.

The main file, that actually create the service, is the **istSOS.py** that use mod_python library to interact with the Apache web server.

This file is reponsible for reading the user request, process it and provde the response.

First the factory_filter istantiate the correct filter class (function of the request type), then the factory_responder authomatically instantiate the relative reponder class and finally the correct renderer is called to produce an SOS standard response.

.. figure::  images/istSOSflow.png
   :align:   center
   :scale:   50

   istSOS working flow.

An important file is the configuration file (**SOSconfig.py**) that enable the setting of important parameters like service name, service version, database connection parameters, dictionaries definition, handled requests, etc.


Filter classes
============================
Filters provide a class interface for converting http requests (GET or POST) submitted according the SOS standard in python objects that contains the submitted parameters and values.

Responder classes
============================
Responders are a set of classes that resolve the specific request, interacting with the istSOSdatabase and gathering the required informations.


Renderer classes
============================
They are reponsible for converting the informations stored in the responders into SOS response format as defined by SOS standard.


