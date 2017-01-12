.. _mapping:

=====================
Mapping the stations
=====================



Initializing an OpenLayers 3 map
---------------------------------

On Ubuntu create a directory in the Apache “document root” directory (usually /var/www or
/var/www/html) and give read write permissions:

.. code-block:: rest

    sudo mkdir /var/www/istsosws
    sudo chmod 777 -Rf /var/www/istsosws
    
On Windows create a directory in the Apache “document root” directory (usually <Apache
folder>\\htdocs) and name it istsosws

If you are using firefox check if the webGL are enabled. go to http://get.webgl.org/. If they are
not enabled:

.. code-block:: rest

    open a new page and go to about:config
    search the option webgl.force-enabled and set to true

Using your favorite text editor create an **index.html** file in the istsosws directory. 
Then copy&paste the following code:

.. code-block:: html
    :linenos:

    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>istSOS - mapping sensor</title>
            <link rel="stylesheet"
                href="http://ol3js.org/en/master/css/ol.css" type="text/css">
            <style>
                #map {
                    width: 600px;
                    height: 400px;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script type="text/javascript"
                src="http://ol3js.org/en/master/build/ol.js"></script>
            <script type="text/javascript"
                src="app.js"></script>
        </body>
    </html>

Now create an **app.js** file in the same folder and copy&paste this code:

.. code-block:: javascript
    :linenos:

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: new ol.View({
            zoom: 0,
            center: [0, 0]
        }),
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
        ]
    });

Test you OL3 map opening this page `http://localhost/istsosws <http://localhost/istsosws>`_. You should see an
OpenStreetMap map.

Loading istSOS sensors on the map
---------------------------------

The istSOS WA REST exposes a request to retrieve a GeoJSON file including all the
sensors offered by a istSOS instance.

.. note::
    
    Try to load the GeoJSON:
    
    http://localhost/istsos/wa/istsos/services/demo/procedures/operations/geojson
    
    You can also execute a reprojection by adding the epsg parameter:
    
    http://localhost/istsos/wa/istsos/services/demo/procedures/operations/geojson?epsg=3857

Now modify the **app.js** file by adding a Vector layer (ol.layer.Vector) configured to load a
GeoJSON source (lines 12-17):

.. code-block:: javascript
    :linenos:
    :emphasize-lines: 12-17

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: new ol.View({
            zoom: 0,
            center: [0, 0]
        }),
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
            ,new ol.layer.Vector({
                source: new ol.source.GeoJSON({
                    url: '/istsos/wa/istsos/services/demo/' +
                        'procedures/operations/geojson?epsg=3857'
                })
            })
        ]
    });
    
Press **F5** to reload the map on the browser (now you should also see some circles
representing the sensor position).

Changing the istSOS vector layer style
--------------------------------------

Modify the **app.js** file as shown in the next box:

.. code-block:: javascript
    :linenos:
    :emphasize-lines: 17-27

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: new ol.View({
            zoom: 0,
            center: [0, 0]
        }),
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            })
            ,new ol.layer.Vector({
                source: new ol.source.GeoJSON({
                    url: '/istsos/wa/istsos/services/demo/' +
                        'procedures/operations/geojson?epsg=3857'
                })
                ,style: function(feature, resolution) {
                    return [
                    new ol.style.Style({
                        image: new ol.style.Circle({
                            radius: 5,
                            fill: new ol.style.Fill({color: 'green'}),
                            stroke: new ol.style.Stroke({color: 'red', width: 1})
                        })
                    })
                    ];
                }
            })
        ]
    });
    
Reload (F5) the web page on the browser

Adding interaction to the map to display sensor metadata
--------------------------------------------------------

In the **index.html** file add a div element just below the map div tag (line 17). This will be the place
where sensor details will be displayed:

.. code-block:: html
    :linenos:
    :emphasize-lines: 17

    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>istSOS - mapping sensor</title>
            <link rel="stylesheet"
                href="http://ol3js.org/en/master/css/ol.css" type="text/css">
            <style>
                #map {
                    width: 600px;
                    height: 400px;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div id="details"></div>
            <script type="text/javascript"
                src="http://ol3js.org/en/master/build/ol.js"></script>
            <script type="text/javascript"
                src="app.js"></script>
        </body>
    </html>

Append in the **app.js** file this code to enable the “ol.interaction.Select” feature `[ol3 example] <http://ol3js.org/en/master/examples/select-features.html>`_:

.. code-block:: javascript

    var select = new ol.interaction.Select({
        layer: map.getLayers().getArray()[1]
    });
    map.addInteraction(select);

...and append in the **app.js** file this code that will register a function that will listen for the
“add” event of the “ol.interaction.Select”:

.. code-block:: javascript

    select.getFeatures().on("add", function(e){
        var feature = e.element;
        
        var html = "<span style='font-weight: bold;'>" +
            feature.getProperties().name+"</span><br/><br/>" +
            "Begin: " + feature.getProperties().samplingTime.beginposition + "<br/>" +
            "End: " + feature.getProperties().samplingTime.endposition + "<br/><br/>" +
            "Observed properties:<ol>";
        for (var cnt = 0; cnt < feature.getProperties().observedproperties.length; cnt++){
            var obs = feature.getProperties().observedproperties[cnt];
            html += "<li>" + obs.name + "</li>";
        }
        document.getElementById('details').innerHTML = html;
    });

Reload (**F5**) the web page on the browser and click on a sensor displayed on the map.
Sensor details will be displayed in the details div.

.. note::

    If you want to display other properties using the feature.getProperties() function,
    this are the attributes that can be accessed:
    
    .. code-block:: javascript
    
        {
            "samplingTime": {
                    "beginposition": "2007-01-01T00:00:00+0100",
                    "endposition": "2011-12-31T23:50:00+0100"
            },
            "sensortype": "insitu-fixed-point",
            "observedproperties": [
                {
                    "name": "water-height",
                    "uom": "m"
                }
            ],
            "description": "",
            "name": "A_AETCAN_AIR",
            "assignedid": "8c4b9c18d464493568cfb18d015bbed5",
            "offerings": [
                "temporary"
            ],
            "id": 51
        }

Plotting measures in a chart
----------------------------

In this tutorial we will show you how to use the GetObservation request using the WA REST
interface. To display the measures this libraries will be used:

    - **Dygraphs (MIT license)**: a fast, flexible open source JavaScript charting library (http://dygraphs.com)

In addition to request and parse data we will use two other JavaScript libs:

    - **JQuery (MIT license)**: a fast, small, and feature-rich JavaScript library (http://jquery.com)
    - **Moment.js (MIT license)**: a javascript date library for parsing, validating, manipulating, and formatting dates (http://momentjs.com)

Let‟s modify the **index.html** file (see line 18, 21-26):

.. code-block:: html
    :linenos:
    :emphasize-lines: 18,21-26

    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>istSOS - mapping sensor</title>
            <link rel="stylesheet"
                href="http://ol3js.org/en/master/css/ol.css" type="text/css">
            <style>
                #map {
                    width: 600px;
                    height: 400px;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div id="details"></div>
            <div id="chart"></div>
            <script type="text/javascript"
                src="http://ol3js.org/en/master/build/ol.js"></script>
            <script type="text/javascript"
                src="http://dygraphs.com/dygraph-combined.js"></script>
            <script type="text/javascript"
                src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
            <script type="text/javascript"
                src="http://momentjs.com/downloads/moment.min.js"></script>
            <script type="text/javascript"
                src="app.js"></script>
        </body>
    </html>

Now you have access to the new API, let‟s add the code..
When a sensor is selected we have access to a limited number of properties, but enough to
make a GetObservation request. In the next code panel the added code will do the following
job:

    - Extract the endPosition (last observation measured)
    - Using the Moment.js API, parse the iso date string in a Moment object
    - Subtract 7 Days from the endPosition creating the “from” date.
    - Execute a getObservation request with JQuery, using the feature properties
        - offering
        - procedure name
        - observed property
        - the calculated “from” date and the endPosition (to request last week of data)
    - As the response arrive the data is prepared
    - The Chart is created

Here the *select.getFeatures()* modified in the **app.js** file:


.. code-block:: javascript
    

    select.getFeatures().on("add", function(e){
        var feature = e.element;
        
        var html = "<span style='font-weight: bold;'>" +
            feature.getProperties().name+"</span><br/><br/>" +
            "Begin: " + feature.getProperties().samplingTime.beginposition + "<br/>" +
            "End: " + feature.getProperties().samplingTime.endposition + "<br/><br/>" +
            "Observed properties:<ol>";
        
        for (var cnt = 0; cnt < feature.getProperties().observedproperties.length; cnt++){
            var obs = feature.getProperties().observedproperties[cnt];
            html += "<li>" + obs.name + "</li>";
        }
        
        document.getElementById('details').innerHTML = html;
        
        var from = moment(feature.getProperties().samplingTime.endposition);
        from.subtract('days', 7);
        $.ajax({
            dataType: "json",
            url: "/istsos/wa/istsos/services/sos/operations/getobservation" +
                "/offerings/" + feature.getProperties().offerings[0] +
                "/procedures/"+feature.getProperties().name +
                "/observedproperties/" +
                    feature.getProperties().observedproperties[0].def+"/eventtime"+
                "/"+from.format()+"/"+feature.getProperties().samplingTime.endposition,
            success: function(json){
                var data = [];
                for (c=0; c < json.data[0].result.DataArray.values.length; c++){
                    data.push([
                        moment(json.data[0].result.DataArray.values[c][0]).toDate(),
                        parseFloat(json.data[0].result.DataArray.values[c][1])
                    ])
                }
                new Dygraph(
                    document.getElementById("chart"),
                    data,
                    {} // options
                );
            }
        });
        
    });
























