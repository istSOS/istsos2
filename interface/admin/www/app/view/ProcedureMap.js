Ext.define('istsos.view.ProcedureMap', {
    extend: 'istsos.view.ui.ProcedureMap',
    alias: 'widget.proceduremap',

    initComponent: function() {

        this.addEvents({
            "procedureSelected" : true
        });

        // Init filters
        this.service = null;
        this.offering = null;
        this.procedure = null;
        this.observedProperty = null;

        this.hightlight = {};

        this.callParent(arguments);

        this.on("afterrender",function(){

          /**
           * Elements that make up the popup.
           */
          var container = document.getElementById('popup');
          var content = document.getElementById('popup-content');
          content.style.overflow = 'hidden';
          content.style.overflowY = 'scroll';
          var closer = document.getElementById('popup-closer');

          /**
           * Add a click handler to hide the popup.
           * @return {boolean} Don't follow the href.
           */
          closer.onclick = function() {
            overlay.setPosition(undefined);
            closer.blur();
            return false;
          };

          /**
           * Create an overlay to anchor the popup to the map.
           */
          var overlay = new ol.Overlay(/** @type {olx.OverlayOptions} */ ({
            element: container,
            autoPan: true,
            autoPanAnimation: {
              duration: 250
            }
          }));

          this.vector = new ol.layer.Vector({
            source: new ol.source.Vector({
              features: new ol.Collection()
            }),
            renderOrder: function(f,c){
              var pm = Ext.getCmp('proceduremap');
              if(f.get('color') && c.get('color')){
                return 0;
              }else if(f.get('color')) {
                return 1;
              }else if(c.get('color')) {
                return -1;
              }else if(pm.hightlight.hasOwnProperty(f.get('assignedid'))){
                return 1;
              }else if(pm.hightlight.hasOwnProperty(c.get('assignedid'))){
                return -1;
              }
              return null;
            },
            style: this.featureStyle
            /*style: [new ol.style.Style({
              image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({color: 'green'}),
                stroke: new ol.style.Stroke({color: 'red', width: 1})
              })
            })]*/
          });
          var attribution = new ol.control.Attribution({
            collapsible: false
          });
          this.selectSingleClick = new ol.interaction.Select({multi: true});
          this.map = new ol.Map({
              layers: [
                new ol.layer.Tile({
                  source: new ol.source.OSM()
                  /*source: new ol.source.Stamen({
                    layer: 'toner'
                  })*/
                }),
                this.vector
              ],
              overlays: [overlay],
              interactions: ol.interaction.defaults().extend([this.selectSingleClick]),
              controls: ol.control.defaults({ attribution: false }).extend([attribution]),
              target: 'map',
              view: new ol.View({
                center: [0, 0],
                zoom: 0,
                maxZoom: 16
              })
          });

          this.selectSingleClick.on('select', function(e) {

            if(e.selected.length==0){
                overlay.setPosition(undefined);
                closer.blur();
            }else{
              var coordinate = e.selected[0].getGeometry().getCoordinates();
              var selected = e.selected,
                  html = '';
              for (var c = 0, l = selected.length;c<l;c++){
                var feature = selected[c];
                var name = feature.getProperties().name;
                var begin = feature.getProperties().samplingTime.beginposition;
                var end = feature.getProperties().samplingTime.endposition;
                html += "<span style='font-weight: bold;'>"+ name + "</span><br/>" +
                  "Begin: " + begin + "<br/>" +
                  "End: " + end + "<br/>" +
                  "Observed properties:<br/>" ;
                //html += "<ol>";
                var from = new Date(end);
                begin = new Date(end);
                begin.setDate(from.getDate() - 5);
                var op = feature.getProperties().observedproperties;
                // Create link that will call the chart function
                for (var cnt = 0; cnt < op.length; cnt++){
                    //html += "<li><a href='javascript:chart(\""+name+"\",\""+begin.toISOString()+"\",\""+end+"\",\""+op[cnt].def+"\");'>" + op[cnt].name + "</a></li>";
                    html += " ** " + op[cnt].name + "<br/>";
                }
                html += "<a style='font-size: smaller;' href='javascript:Ext.callback(Ext.getCmp(\"proceduremap\").procedureSelected, Ext.getCmp(\"proceduremap\"), [\"" + feature.get('assignedid')+"\"]);'>Add</a>";
                html += "<hr/>";

                //html += "</ol><hr/>";
              }
              content.innerHTML = html;
              overlay.setPosition(coordinate);
            }
          });

          var size = this.getSize();
          content.style.maxHeight = (size.height-90)+"px";

          this.on('resize', function(container, width, height, oldWidth, oldHeight, eOpts ){
            this.map.updateSize();
            //var cnt = document.getElementById('popup-content');
            content.style.maxHeight = (height-90)+"px";
          },this);

        }, this, {
          single: true
        });

    },
    procedureSelected: function(assignedid){
      var features = this.vector.getSource().getFeatures();
      for (var c = 0, l = features.length; c<l; c++){
        if(features[c].get('assignedid')==assignedid){
          this.fireEvent("procedureSelected",
            this.service, (this.offering==null?'temporary':this.offering), features[c].get('name'));
          return;
        }
      }
    },
    featureStyle: function(feature, resolution) {
      var color = feature.get('color');
      var pm = Ext.getCmp('proceduremap');
      if(pm.hightlight.hasOwnProperty(feature.get('assignedid'))){
        color = pm.hightlight[feature.get('assignedid')];
      }else if(color==false || color==null){
        color='#008000';
      }
      return [
        new ol.style.Style({
          image: new ol.style.Circle({
            radius: 5,
            fill: new ol.style.Fill({color:color}),
            stroke: new ol.style.Stroke({color: 'black', width: 1})
          })
      })];
    },
    removeHighlight: function(procedure){
      procedure.un("colorchanged", this.add2highlight, this);
      var features = this.vector.getSource().getFeatures();
      for (var c = 0, l = features.length; c<l; c++){
        if(features[c].get('assignedid')==procedure.meta.assignedSensorId){
          features[c].set('color', false);
        }
      }
      delete this.hightlight[procedure.meta.assignedSensorId];
    },
    add2highlight: function(procedure){

      procedure.on("colorchanged", this.add2highlight, this);

      var features = this.vector.getSource().getFeatures();
      for (var c = 0, l = features.length; c<l; c++){
        if(features[c].get('assignedid')==procedure.meta.assignedSensorId){
          features[c].set('color', procedure.color);
        }
      }
      this.hightlight[procedure.meta.assignedSensorId] = procedure.color;
    },
    /*
      Fit map view to services
    */
    fit2service: function(service){
        this.service = service;
        // Resetting filters
        this.offering = null;
        this.procedure = null;
        this.observedProperty = null;
        this._reloadMap();
    },
    /*
      Fit map view to offering
    */
    fit2offering: function(offering, service){
        if(service){
          this.service = service;
        }
        if(offering){
          this.offering = offering;
        }
        // Resetting filters
        this.procedure = null;
        this.observedProperty = null;
        this._reloadMap();
    },
    /*
      Fit map view to procedure
    */
    fit2procedure: function(procedure, offering, service ){
        if(service){
          this.service = service;
        }
        if(offering){
          this.offering = offering;
        }
        this.procedure = procedure;
        // Resetting filters
        this.observedProperty = null;
        this._reloadMap();
    },
    /*
      Fit map view to observedProperty
    */
    fit2observedProperty: function(service, offering, observedProperty){
        this.service = service;
        this.offering = offering;
        this.observedProperty = observedProperty;
        // Resetting filters
        this.procedure = null;
        this._reloadMap();
    },
    _reloadMap: function(params){

      // Crear all features from map
      this.vector.getSource().clear();

      // Prepare URL for GeoJSON request
      var url = Ext.String.format('{0}/istsos/services/{1}/procedures/operations/geojson',
          wa.url, this.service);

      var params = {};

      if (this.offering){
        params['offering'] = this.offering;
      }
      if (this.procedure){
        params['procedure'] = this.procedure;
      }
      if (this.observedProperty){
        params['observedProperty'] = this.observedProperty;
      }

      Ext.Ajax.request({
        scope: this,
        method: 'GET',
        url: url,
        params: Ext.apply({
          epsg: "3857"
        },params),
        success: function(response){
          var json = Ext.decode(response.responseText);
          var reader = new ol.format.GeoJSON();
          var features = reader.readFeatures(json);
          var mp = new ol.geom.MultiPoint([],ol.geom.GeometryLayout.XYZ);
          for (idx in features){
            mp.appendPoint(features[idx].getGeometry());
          }
          this.vector.getSource().addFeatures(features);
          this.map.getView().fit(mp.getExtent(), this.map.getSize());
        }
      });
    }
});
