Ext.define('istsos.view.procedure', {
    extend: 'istsos.view.ui.procedure',

    initComponent: function() {

        var me = this;
        this.addEvents({
            "ready2load" : true
        });

        this.remaining2load = 2;
        //this.remaining2load = 2;

        var systy = Ext.create('istsos.store.cmbSystemType', {

        });
        systy.on('load',function(){
          this.remaining2load--;
          this.checkRemaining();
        },this);

        systy.getProxy().url = Ext.String.format('{0}/istsos/services/{1}/systemtypes',
            wa.url, this.istService);
        Ext.create('istsos.store.cmbDocumentFormat');
        Ext.create('istsos.store.gridDocumentation');
        Ext.create('istsos.store.gridOutputs');
        Ext.create('istsos.store.Constraint');

        // Identification SML tool
        Ext.create('istsos.store.cmbSml',{
            "storeId": 'cmbidentification',
            "proxy": {
                "type": 'ajax',
                "url": 'app/data/cmbidentification.json',
                "reader": {
                    "type": 'json',
                    "idProperty": 'definition',
                    "root": 'data'
                }
            }
        });

        Ext.create('istsos.store.cmbSml',{
            "storeId": 'grididentification'
        });

        // Capabilites SML tool

        Ext.create('Ext.data.Store', {
            storeId: 'cmbCapabilities',
            autoLoad: true,
            proxy: {
                type: 'ajax',
                url: 'app/data/cmbcapabilities.json',
                reader: {
                    type: 'json',
                    idProperty: 'definition',
                    root: 'data'
                }
            },
            fields: [
            {
                name: 'combo',
                convert: function(v, record){
                    return record.get('name')  + " (" + record.get('uom') + ")";
                }
            },
            {
                name: 'name',
                type: 'string'
            },
            {
                name: 'definition',
                type: 'string'
            },
            {
                name: 'uom',
                type: 'string'
            }
            ]
        });

        Ext.create('Ext.data.Store', {
            storeId: 'cmbcapabilitiesuom',
            autoLoad: true,
            proxy: {
                type: 'ajax',
                url: 'app/data/cmbcapabilitiesuom.json',
                reader: {
                    type: 'json',
                    idProperty: 'definition',
                    root: 'data'
                }
            },
            fields: [
            {
                name: 'combo',
                convert: function(v, record){
                    return record.get('name')  + " (" + record.get('uom') + ")";
                }
            },
            {
                name: 'name',
                type: 'string'
            },
            {
                name: 'uom',
                type: 'string'
            }
            ]
        });

        Ext.create('Ext.data.Store', {
            storeId: 'cmbcapabilitiesuom2',
            autoLoad: true,
            proxy: {
                type: 'ajax',
                url: 'app/data/cmbcapabilitiesuom.json',
                reader: {
                    type: 'json',
                    idProperty: 'definition',
                    root: 'data'
                }
            },
            fields: [
            {
                name: 'combo',
                convert: function(v, record){
                    return record.get('name')  + " (" + record.get('uom') + ")";
                }
            },
            {
                name: 'name',
                type: 'string'
            },
            {
                name: 'uom',
                type: 'string'
            }
            ]
        });

        Ext.create('istsos.store.cmbSml',{
            "storeId": 'gridCapabilities'
        });

        Ext.create('istsos.store.cmbName',{
            "storeId": 'locationEPSG',
            "autoLoad": true,
            "proxy": {
                "type": 'ajax',
                "url": Ext.String.format('{0}/istsos/services/{1}/epsgs', wa.url,
                    this.istService),
                "reader": {
                    "type": 'json',
                    "idProperty": 'name',
                    "root": 'data'
                }
            },
            "listeners": {
              "load": {
                fn: function(){
                  this.remaining2load--;
                  this.checkRemaining();
                },
                scope: this
              }
            }
        });

        Ext.create('istsos.store.cmbSml',{
            "storeId": 'gridinput'
        });

        Ext.create('istsos.store.cmbSml',{
            "storeId": 'cmbphenomenon',
            "proxy": {
                "type": 'ajax',
                "url": 'app/data/cmbphenomenon.json',
                "reader": {
                    "type": 'json',
                    "idProperty": 'definition',
                    "root": 'data'
                }
            }
        });
        Ext.create('istsos.store.cmbSml',{
            "storeId": 'cmbobservedproperties',
            "proxy": {
                "type": 'ajax',
                "url": Ext.String.format('{0}/istsos/services/{1}/observedproperties', wa.url,
                    this.istService),
                "reader": {
                    "type": 'json',
                    "idProperty": 'definition',
                    "root": 'data'
                }
            }
        });

        Ext.create('istsos.store.cmbSml',{
            "storeId": 'cmbuom',
            "proxy": {
                "type": 'ajax',
                "url": Ext.String.format('{0}/istsos/services/{1}/uoms', wa.url,
                    this.istService),
                "reader": {
                    "type": 'json',
                    "idProperty": 'definition',
                    "root": 'data'
                }
            }
        });

        Ext.define('smlfield', {
            extend: 'Ext.data.Model',
            fields: [
            {
                name: 'name',
                type: 'string'
            },
            {
                name: 'value',
                type: 'string'
            },
            {
                name: 'definition',
                type: 'string'
            }
            ]
        });


        // Stores used for the utils - copy template
        Ext.create('istsos.store.Offerings');
        Ext.create('istsos.store.gridProceduresList');
        var ssrv = Ext.create('istsos.store.Services');
        ssrv.getProxy().url = Ext.String.format('{0}/istsos/services',wa.url);

        me.callParent(arguments);


        if (!Ext.Array.contains(wa.user.groups, 'admin') && !Ext.Array.contains(wa.user.groups, 'networkmanager')){
            Ext.getCmp('procedurename').setVisible(false);
            Ext.getCmp('procedureNameRO').setVisible(true);
        }


        Ext.getCmp('procedurename').on('change',function(field, newValue, oldValue, eOpts){
            var gridIdentification = Ext.getCmp('gridIdentification');
            var rec = gridIdentification.store.findRecord(
                'definition',
                'urn:ogc:def:identifier:OGC:uniqueID'
            );
            if (Ext.isEmpty(rec)){ // unique id still not exist
                gridIdentification.store.insert(0,
                    Ext.create('smlfield', {
                        'name': 'uniqueID',
                        'definition': 'urn:ogc:def:identifier:OGC:uniqueID',
                        'value': this.istSections.urn.procedure+newValue
                    })
                );
            }else{ // UniqueID exist and must be updated
                rec.set('value',this.istSections.urn.procedure+newValue);
            }
        },this);

        Ext.getCmp("constrChoose").select(0);

        Ext.getCmp("constrChoose").on("select",function(combo, records, eOpts){

            var value = combo.getValue();

            var from = Ext.getCmp('constrFrom');
            var to = Ext.getCmp('constrTo');
            var list = Ext.getCmp('constrList');

            switch (value) {
                case 0:
                  from.setVisible(false);
                  to.setVisible(false);
                  list.setVisible(false);
                  break;
                case 1:
                  from.setVisible(true);
                  to.setVisible(false);
                  list.setVisible(false);
                  break;
                case 2:
                  from.setVisible(false);
                  to.setVisible(true);
                  list.setVisible(false);
                  break;
                case 3:
                  from.setVisible(true);
                  to.setVisible(true);
                  list.setVisible(false);
                  break;
                case 4:
                  from.setVisible(false);
                  to.setVisible(false);
                  list.setVisible(true);
                  break;
            }
        });

        // Combos used for the utils - copy template
        Ext.getCmp("cmbServices").on("select",function(combo, records, eOpts){

            var pr = Ext.getCmp('oeCbProcedure');
            pr.reset();
            pr.getStore().removeAll();
            pr.disable();

            var o = Ext.getCmp('oeCbOffering');
            o.reset();
            o.getStore().removeAll();
            o.disable();

            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/offerings/operations/getlist',
                    wa.url,combo.getValue()),
                scope: o,
                method: "GET",
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (json.data.length>0) {
                        this.getStore().loadData(json.data);
                        this.enable();
                    }else{
                        this.disable();
                        Ext.Msg.alert("Server message", "\"" + json['message'] + "\"<br/><br/>" +
                                "<small>Status response: " + response.statusText + "</small>");
                    }
                }
            });
        });

        Ext.getCmp("oeCbOffering").on("select",function(combo, records, eOpts){

            var pr = Ext.getCmp('oeCbProcedure');
            pr.reset();
            pr.getStore().removeAll();
            pr.disable();

            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/offerings/{2}/procedures/operations/memberslist',
                    wa.url,Ext.getCmp('cmbServices').getValue(),combo.getValue()),
                scope: pr,
                method: "GET",
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (json.data.length>0) {
                        this.getStore().loadData(json.data);
                        this.enable();
                    }else{
                        this.disable();
                        Ext.Msg.alert("Server message", "\"" + json['message'] + "\"<br/><br/>" +
                                "<small>Status response: " + response.statusText + "</small>");
                    }
                }
            });
        });
        Ext.getCmp("btnTemplateFill").on("click",this.executeCopy,this);

        this.initSmlFieldPanel('smlIdentification');
        this.initSmlFieldPanel('smlCapabilities');
        this.initSmlFieldPanel('smlDocumentation');
        this.initSmlFieldPanel('smlInputs');

        var cmp = Ext.getCmp('smlOutputs');

        cmp.getComponent('frmSml').getComponent('btnAddSml').on('click',function(){
            var main = Ext.getCmp('smlOutputs');
            var form = main.getComponent('frmSml');
            var cmb = form.getComponent('cmbSml');
            var store = main.getComponent('gridSml').getStore();
            if (!form.getForm().isValid()) {
                Ext.MessageBox.show({
                    title: 'Warning',
                    msg: 'Mandatory params are not filled correctly',
                    buttons: Ext.MessageBox.OK,
                    animateTarget: form
                });
                return;
            }
            var json = form.getForm().getValues();
            // Check if optional quality index check is filled correctly
            if (json.ctype>0){
                var msg;
                switch (json.ctype) {
                    case 1: // Greater then
                        if (Ext.isEmpty(json['from'])){
                            msg = "You have to set the minimal value " +
                            "statisticallly accepted by this observed property";
                        }
                        break;
                    case 2: // Less then
                        if (Ext.isEmpty(json['to'])){
                            msg = "You have to set the maximal value " +
                            "statisticallly accepted by this observed property";
                        }
                        break;
                    case 3: // Between
                        if (Ext.isEmpty(json['from']) || Ext.isEmpty(json['to'])){
                            msg = "You have to set the interval value " +
                            "statisticallly accepted by this observed property";
                        }
                        break;
                    case 4: // List
                        if (Ext.isEmpty(json['list'])){
                            msg = "You have to set a numeric (comma separated) list " +
                            "accepted by this observed property";
                        }else{ // Check CSNum list
                            var vals = json['list'].split(',');
                            for (var c = 0; c < vals.length; c++){
                                if(!Ext.isNumeric(vals[c])){
                                    msg = "Value ("+vals[c]+") inserted is not " +
                                    "numeric, and it should be numeric";
                                    break;
                                }
                            }
                        }
                        break;
                }

                if (msg){
                    Ext.MessageBox.show({
                        title: 'Warning',
                        msg: msg,
                        buttons: Ext.MessageBox.OK,
                        animateTarget: form
                    });
                    return;
                }

            }

            var role = "urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable";

            var rec = cmb.findRecord('definition',cmb.getValue()), r = null;

            switch (json.ctype) {
                case 1: // Greater then
                    r = Ext.create('smlfield', {
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : json.uom,
                        "description" : json.description,
                        "role" : role,
                        "from" : json.from
                        //,"ctype": json.ctype
                    });
                    break;
                case 2: // Less then
                    r = Ext.create('smlfield', {
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : json.uom,
                        "description" : json.description,
                        "role" : role,
                        "to" : json.to
                        //,"ctype": json.ctype
                    });
                    break;
                case 3: // Between
                    r = Ext.create('smlfield', {
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : json.uom,
                        "description" : json.description,
                        "role" : role,
                        "to" : json['to'],
                        "from" : json['from']
                        //,"ctype": json.ctype
                    });
                    break;
                case 4: // List
                    r = Ext.create('smlfield', {
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : json.uom,
                        "description" : json.description,
                        "role" : role,
                        "list" : json.list.split(",").toString()
                        //,"ctype": json.ctype
                    });
                    break;
                default:
                    r = Ext.create('smlfield', {
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : json.uom,
                        "description" : json.description
                    });

            }


            var last = store.getCount();
            /*if (last>0) {
                last--;
            }*/
            store.insert(last, r);
            form.getForm().reset();

            //store.insert(0, r);
            form.getForm().reset();
        },this);

        cmp.getComponent('gridSml').getComponent('gridToolbar').getComponent(
            'btnRemoveSml').on('click',function(){
            this.removeSmlfield('smlOutputs',{
                "skipInsert":true
            });
        },this);

        Ext.getCmp('applicationType').on("select",function(){
            var cb = Ext.getCmp('cbDetailsDefinition');
            var tf = Ext.getCmp('cbDetailsMeasure');

            var v = cb.getValue();
            var rec = cb.findRecord(cb.valueField || cb.displayField, v);
            tf.setValue(rec.get("defaultMeasure"));
        });

        var caricami = function(field){
            field.store.load();
            field.un("focus",caricami);
        }
        Ext.getCmp('applicationType').on("focus", caricami);


    },
    checkRemaining: function(){
      console.log("checkRemaining > " + this.remaining2load);
      if(this.remaining2load==0){
          this.fireEvent("ready2load");
      }
    },
    executeCopy: function(){
        // Load data from a /istsos/services/this.istService/procedures/{name} GET request

        if (Ext.isEmpty(this.mask)) {
            this.mask = new Ext.LoadMask(this.body, {
                msg:"Please wait..."
            });
        }
        this.mask.show();
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/procedures/{2}',
                wa.url,
                Ext.getCmp('cmbServices').getValue(),
                Ext.getCmp('oeCbProcedure').getValue()),
            //url: 'app/data/procedure.json',
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    delete json.data.assignedSensorId;
                    delete json.data.system;
                    delete json.data.system_id;
                    if (!Ext.isEmpty(this.istForm)) {
                        this.istForm.loadJSON(json);
                    } else {
                        this.loadJSON(json,false);
                    }
                }
                this.mask.hide();
            }
        });
    },
    executeGet: function(){
        if(this.istForm.remaining2load>0){
          this.istForm.on("ready2load",this.istForm.executeGet,this);
        }else{
          if (Ext.isEmpty(this.mask)) {
            this.mask = new Ext.LoadMask(this.body, {
              msg:"Please wait..."
            });
          }
          this.mask.show();
          Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/procedures/{2}', wa.url,this.istService, this.istProcedure),
            scope: this,
            method: "GET",
            success: function(response){
              var json = Ext.decode(response.responseText);
              if (json.success) {
                this.istForm.loadJSON(json);
              }
              this.mask.hide();
            }
          });
        }
    },
    loadJSON: function(json, hidefield){

        //console.dir(json);
        if (!Ext.isBoolean(hidefield)) {
            hidefield=true;
        }
        if (hidefield) {
            Ext.getCmp('toolspanel').setVisible(false); // tools panel
            Ext.getCmp('asid').setVisible(true); // assigned sensor id field
            Ext.getCmp('frmSmlOutputs').setVisible(false); // Editing panel of observed properties
            Ext.getCmp('smlOutputs').getComponent('gridSml').removeDocked(Ext.getCmp('smlOutputs').getComponent('gridSml').getComponent('gridToolbar'),true);
        //Ext.getCmp('smlOutputs').getComponent('gridSml').getComponent('gridToolbar').setVisible(false); // Remove observed property button
        }

        this.loadedJson = json;

        // IDENTIFICATION
        var store = Ext.getCmp("smlIdentification").getComponent('gridSml').getStore();
        var c = json["data"]["identification"];
        for (var i in c) {
            var r = Ext.create('smlfield', Ext.apply({}, c[i]));
            store.insert(0, r);
        }

        // GENERAL INFORMATION
        Ext.getCmp('generalInfo').loadRecord(json);
        Ext.getCmp('procedureNameRO').setValue(Ext.getCmp('procedurename').getValue());

        // CLASSIFICATION
        var data = {}
        for (var i in json["data"]["classification"]) {
            var cl = json["data"]["classification"][i];
            if (cl["definition"]=='urn:ogc:def:classifier:x-istsos:1.0:systemType') {
                data["systemtype"]=cl["value"];
            }else if (cl["definition"]=='urn:ogc:def:classifier:x-istsos:1.0:sensorType') {
                data["sensortype"]=cl["value"];
            }
        }
        Ext.getCmp("classification").loadRecord({
            data: data
        });

        // CHARACTERISTICS
        Ext.getCmp('characteristics').loadRecord(json);

        // CONTACTS
        var data = {}
        for (var i in json["data"]["contacts"]) {
            var c = json["data"]["contacts"][i];
            if (c["role"]=='urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:owner') {
                Ext.getCmp("frmOwner").loadRecord({
                    data:c
                });
            }else if (c["role"]=='urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:manufacturer') {
                Ext.getCmp("frmManufacturer").loadRecord({
                    data:c
                });
            }else if (c["role"]=='urn:x-ogc:def:classifiers:x-istsos:1.0:contactType:operator') {
                Ext.getCmp("frmOperator").loadRecord({
                    data:c
                });
            }
        }

        // DOCUMENTATION
        store = Ext.getCmp("smlDocumentation").getComponent('gridSml').getStore();
        var c = json["data"]["documentation"];
        for (var i in c) {
            var r = Ext.create('smlfield', Ext.apply({}, c[i]));
            store.insert(0, r);
        }

        // LOCATION
        c = json["data"]["location"];
        var epsg = c["crs"]["properties"]['name'];
        if (Ext.isString(epsg)){
            epsg = epsg.replace("EPSG:", "");
        }
        Ext.getCmp("frmLocation").loadRecord({
            data:{
                x: c["geometry"]["coordinates"][0],
                y: c["geometry"]["coordinates"][1],
                z: c["geometry"]["coordinates"][2],
                epsg: epsg,
                name: c["properties"]['name']
            }
        });

        /*if (Ext.isEmpty(c["crs"]["properties"]['name'])) {
            Ext.getCmp('cbepsg').setValue(c["crs"]["properties"]['name']);
        }*/

        // INTERFACES
        Ext.getCmp('frmInterfaces').loadRecord(json);

        // INPUTS
        store = Ext.getCmp("smlInputs").getComponent('gridSml').getStore();
        store.removeAll();
        var c = json["data"]["inputs"];
        for (var i in c) {
            var r = Ext.create('smlfield', Ext.apply({}, c[i]));
            store.insert(0, r);
        }

        // OUTPUTS
        store = Ext.getCmp("smlOutputs").getComponent('gridSml').getStore();
        store.removeAll();
        var c = json["data"]["outputs"];

        for (var i = 0; i < c.length; i++) {
            if (c[i]['name']!='Time') {

                var cnf = {
                    "name" : c[i]['name'],
                    "definition" : c[i]['definition'],
                    "uom" : c[i]['uom'],
                    "description" : c[i]['description'],
                    "role" : "",
                    "from" : "",
                    "to": "",
                    "list": ""
                };

                if (c[i]['constraint']){
                    if (c[i]['constraint']["role"]){
                        cnf.role = c[i]['constraint']["role"];
                    }
                    if (c[i]['constraint']["interval"]){
                         cnf.from = c[i]['constraint']["interval"][0];
                         cnf.to = c[i]['constraint']["interval"][1];
                    }else if(c[i]['constraint']["valueList"]){
                         cnf.list = c[i]['constraint']["valueList"].join(", ");
                    }else if(c[i]['constraint']["max"]){
                         cnf.to = c[i]['constraint']["max"];
                    }else if(c[i]['constraint']["min"]){
                         cnf.from = c[i]['constraint']["min"];
                    }
                }

                var r = Ext.create('smlfield', cnf);
                store.insert(0, r);
            }
        }

        // CAPABILITIES
        store = Ext.getCmp("smlCapabilities").getComponent('gridSml').getStore();
        var c = json["data"]["capabilities"];
        for (var i in c) {
            if (c[i]['definition']=='urn:x-ogc:def:classifier:x-istsos:1.0:acquisitionTimeResolution') {

                // Set combo
                Ext.getCmp('atrCombo').setValue(c[i]['uom']);
                // Set value
                Ext.getCmp('atrValue').setValue(c[i]['value']);

                //Ext.getCmp("tfAcquisitionResolution").setValue(c[i]['value']);
            }else if (c[i]['definition']=='urn:x-ogc:def:classifier:x-istsos:1.0:samplingTimeResolution') {

                // Set combo
                Ext.getCmp('strCombo').setValue(c[i]['uom']);
                // Set value
                Ext.getCmp('strValue').setValue(c[i]['value']);

                //Ext.getCmp("tfSamplingResolution").setValue(c[i]['value']);
            }else if (c[i]['definition'].indexOf('urn:x-ogc:def:classifier:x-istsos:1.0:storageType')>-1) {

                // Set combo
                Ext.getCmp('storeTypeValue').setValue(c[i]['definition'].replace('urn:x-ogc:def:classifier:x-istsos:1.0:storageType:',''));

                //Ext.getCmp("tfSamplingResolution").setValue(c[i]['value']);
            }else{
                store.insert(0, Ext.create('smlfield', c[i]));
            }
        }

        // MQTT Broker configuration
        var form = Ext.getCmp('frmMqtt').loadRecord({
            data: json.data['mqtt']
        });
    },
    createJSON: function(){
        // Insert data from a /istsos/services/{name}/procedures POST request
        var jsonData = {};
        var me = null;
        if (!Ext.isEmpty(this.istForm)) {
            me = this.istForm;
        }else{
            me = this;
        }
        jsonData = Ext.apply(jsonData,me.getSystemInfo());

        jsonData = Ext.apply(jsonData,{
            "identification": me.getSmlStore("smlIdentification")
        });

        jsonData['classification']=me.getClassification();
        jsonData = Ext.apply(jsonData,me.getCharacteristics());

        jsonData['contacts']=me.getContacts();

        jsonData = Ext.apply(jsonData,{
            "documentation": me.getSmlStore("smlDocumentation")
        });

        jsonData = Ext.apply(jsonData,{
            "capabilities": me.getCapabilities()
        });

        jsonData['location']=me.getLocation();

        jsonData = Ext.apply(jsonData,me.getInterfaces());

        jsonData = Ext.apply(jsonData,{
            "inputs": me.getSmlStore("smlInputs")
        });

        jsonData = Ext.apply(jsonData,{
            "outputs": me.getOutputs()
        });

        jsonData = Ext.apply(jsonData,{
            "mqtt": me.getMqttBroker()
        });

        jsonData["history"] = [];

        return jsonData;

    },
    executePut: function(){
        try{
            if (Ext.isEmpty(this.mask)) {
                this.mask = new Ext.LoadMask(this.body, {
                    msg:"Please wait..."
                });
            }
            this.mask.show();

            var me = null;
            if (!Ext.isEmpty(this.istForm)) {
                me = this.istForm;
            }else{
                me = this;
            }

            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/procedures/{2}', wa.url,
                    this.istService, me.loadedJson['data']['system']),
                scope: this,
                method: "PUT",
                jsonData: this.istForm.createJSON(),
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    this.mask.hide();
                    this.fireEvent("operationSubmit",json);
                }
            });
        } catch (ex) {
            this.mask.hide();
            Ext.MessageBox.show({
                title: 'Warning',
                msg: ex.type,
                buttons: Ext.MessageBox.OK,
                animateTarget: ex.cmp
            });
        }
    },
    executePost: function(){
        // Insert data from a /istsos/services/{name}/procedures POST request
        var jsonData = {};
        var me = null;
        if (!Ext.isEmpty(this.istForm)) {
            me = this.istForm;
        }else{
            me = this;
        }
        try {
            if (Ext.isEmpty(this.mask)) {
                this.mask = new Ext.LoadMask(this.body, {
                    msg:"Please wait..."
                });
            }
            this.mask.show();

            jsonData = Ext.apply(jsonData,me.getSystemInfo());

            jsonData = Ext.apply(jsonData,{
                "identification": me.getSmlStore("smlIdentification")
            });

            jsonData['classification']=me.getClassification();
            jsonData = Ext.apply(jsonData,me.getCharacteristics());

            jsonData['contacts']=me.getContacts();

            jsonData = Ext.apply(jsonData,{
                "documentation": me.getSmlStore("smlDocumentation")
            });

            jsonData = Ext.apply(jsonData,{
                "capabilities": me.getCapabilities()
            });

            jsonData['location']=me.getLocation();

            jsonData = Ext.apply(jsonData,me.getInterfaces());

            jsonData = Ext.apply(jsonData,{
                "inputs": me.getSmlStore("smlInputs")
            });

            jsonData = Ext.apply(jsonData,{
                "outputs": me.getOutputs()
            });

            jsonData["history"] = [];

            jsonData['mqtt']=me.getMqttBroker();

            this.loadedJson = {
                data: jsonData
            };
            me.loadedJson = {
                data: jsonData
            };

            var posturl = Ext.String.format(
                '{0}/istsos/services/{1}/procedures',
                wa.url,this.istService
            );

            if (jsonData['classification']['systemtype']=='virtual'){
                posturl = Ext.String.format(
                    '{0}/istsos/services/{1}/virtualprocedures',
                    wa.url,this.istService
                );
            }

            Ext.Ajax.request({
                url: posturl,
                scope: this,
                method: "POST",
                jsonData: jsonData,
                success: function(response, request){
                    var json = Ext.decode(response.responseText);
                    this.mask.hide();
                    if (json.success) {
                        this.fireEvent("operationSubmit",json);
                        /*this.istFunction= {
                            onLoad: 'executeGet',
                            onSubmit: 'executePut'
                        }*/
                        istsos.engine.pageManager.openPage({
                            istTitle: 'Edit procedure',
                            istBody: ['istsos.view.procedure'],
                            istFooter: istsos.SUBMIT,
                            istService: this.istService,
                            istProcedure: request.jsonData.system,
                            istFunction: {
                                onLoad: 'executeGet',
                                onSubmit: 'executePut'
                            }
                        });
                    }
                }
            });

        } catch (ex) {
            this.mask.hide();
            Ext.MessageBox.show({
                title: 'Warning',
                msg: ex.message,
                buttons: Ext.MessageBox.OK,
                animateTarget: ex.cmp
            });
        }
    },
    getSystemInfo: function(){
        var form = Ext.getCmp('generalInfo').getForm();
        if (!form.isValid()) {
            throw {
                message: 'General info: mandatory params not filled.',
                cmp: "generalInfo"
            };
        }
        var json = form.getValues();
        return Ext.apply({
            'system_id': json['system']
        },json);
    },
    getCapabilities: function(){
        var ret = this.getSmlStore("smlCapabilities");
        var sr = Ext.getCmp("strValue");
        var ar = Ext.getCmp("atrValue");
        var str = Ext.getCmp("storeTypeValue");

        if (!Ext.isEmpty(sr.getValue())) {
            ret.push({
                "name": "Sampling time resolution",
                "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:samplingTimeResolution",
                "uom": Ext.getCmp("strCombo").getValue(),
                "value": ""+sr.getValue()
            });
        }

        if (!Ext.isEmpty(ar.getValue())) {
            ret.push({
                "name": "Acquisition time resolution",
                "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:acquisitionTimeResolution",
                "uom": Ext.getCmp("atrCombo").getValue(),
                "value": ""+ar.getValue()
            });
        }
        if (!Ext.isEmpty(str.getValue())) {
            ret.push({
                "name": "Storage Type",
                "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:storageType:" + str.getValue()
            });
        }

        /*var sr = Ext.getCmp("tfSamplingResolution");
        var ar = Ext.getCmp("tfAcquisitionResolution");
        if (sr.isDirty()) {
            ret.push({
                "name": "Sampling time resolution",
                "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:samplingTimeResolution",
                "uom": "iso8601",
                "value": sr.getValue()
            });
        }
        if (ar.isDirty()) {
            ret.push({
                "name": "Acquisition time resolution",
                "definition": "urn:x-ogc:def:classifier:x-istsos:1.0:acquisitionTimeResolution",
                "uom": "iso8601",
                "value": ar.getValue()
            });
        }*/
        return ret;
    },
    getClassification: function(){
        var form = Ext.getCmp('classification').getForm();
        if (!form.isValid()) {
            throw {
                message: 'Classification: mandatory params not filled.',
                cmp: "classification"
            };
        }
        var json = form.getValues();
        return [
        {
            "name" : "System Type",
            "definition" : "urn:ogc:def:classifier:x-istsos:1.0:systemType",
            "value" : json["systemtype"]
        },{
            "name" : "Sensor Type",
            "definition" : "urn:ogc:def:classifier:x-istsos:1.0:sensorType",
            "value" : json["sensortype"]
        }
        ];
    },
    getCharacteristics: function(){
        var form = Ext.getCmp('characteristics').getForm();
        if (!form.isValid()) {
            throw {
                message: 'Characteristics: mandatory params not filled.',
                cmp: "characteristics"
            };
        }
        return form.getValues();
    },
    getContacts: function(){
        var contacts = [];
        var form = Ext.getCmp('frmOwner').getForm();
        if (form.isDirty() && form.isValid()) {
            contacts.push(form.getValues());
        }
        form = Ext.getCmp('frmManufacturer').getForm();
        if (form.isDirty() && form.isValid()) {
            contacts.push(form.getValues());
        }
        form = Ext.getCmp('frmOperator').getForm();
        if (form.isDirty() && form.isValid()) {
            contacts.push(form.getValues());
        }
        return contacts;
    },
    getLocation: function(){

        var form = Ext.getCmp('frmLocation').getForm();
        if (!form.isValid()) {
            throw {
                message: 'Location: mandatory params not filled.',
                cmp: "frmLocation"
            };
        }
        var json = form.getValues();
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [json['x'],json['y'],json['z']]
            },
            "crs": {
                "type": "name",
                "properties": {
                    "name": json['epsg']
                }
            },
            "properties": {
                "name": json['name']
            }
        }
    },
    getInterfaces: function(){
        var form = Ext.getCmp('frmInterfaces').getForm();
        if (!form.isValid()) {
            throw {
                message: 'Interfaces: mandatory params not filled.',
                cmp: "frmInterfaces"
            };
        }
        return form.getValues();
    },
    getMqttBroker: function(){
        console.log("getMqttBroker");
        var form = Ext.getCmp('frmMqtt').getForm(),
            ret = null;
        if (form.isDirty() && !form.isValid()) {
            throw {
                type: 'MQTT Broker: URL and Topic are mandatory parameters.',
                cmp: "frmMqtt"
            };
        }else{
            var json = form.getValues();
            if(!Ext.isEmpty(json["broker_url"]) && !Ext.isEmpty(json["broker_topic"])){
                ret = json;
            }
        }
        return ret;
    },
    getOutputs: function(){
        var store = Ext.getStore("gridoutputs");
        if (store.getCount()==0) {
            throw {
                message: 'Outputs: at leas one oberved property must be added',
                cmp: "frmSmlOutputs"
            };
        }
        var ret = [
        {
            "name" : "Time",
            "definition" : wa.isodef,
            "uom" : "iso8601",
            "description" : "",
            "constraint" : {}
        }];
        for (var i = 0; i < store.getCount(); i++) {
            var rec = store.getAt(i);

            if (!Ext.isEmpty(rec.get('from')) && !Ext.isEmpty(rec.get('to'))){
                // Between
                ret.push({
                    "name" : rec.get('name'),
                    "definition" : rec.get('definition'),
                    "uom" : rec.get('uom'),
                    "description" : rec.get('description'),
                    "constraint" : {
                        "role" : rec.get('role'),
                        "interval" : [rec.get('from'), rec.get('to')]
                    }
                });
            }else if(!Ext.isEmpty(rec.get('from'))){
                // Greater then
                ret.push({
                    "name" : rec.get('name'),
                    "definition" : rec.get('definition'),
                    "uom" : rec.get('uom'),
                    "description" : rec.get('description'),
                    "constraint" : {
                        "role" : rec.get('role'),
                        "min" : rec.get('from')
                    }
                });
            }else if (!Ext.isEmpty(rec.get('to'))){
                // Less then
                ret.push({
                    "name" : rec.get('name'),
                    "definition" : rec.get('definition'),
                    "uom" : rec.get('uom'),
                    "description" : rec.get('description'),
                    "constraint" : {
                        "role" : rec.get('role'),
                        "max" : rec.get('to')
                    }
                });
            }else if (!Ext.isEmpty(rec.get('list'))){
                // List
                ret.push({
                    "name" : rec.get('name'),
                    "definition" : rec.get('definition'),
                    "uom" : rec.get('uom'),
                    "description" : rec.get('description'),
                    "constraint" : {
                        "role" : rec.get('role'),
                        "valueList" : rec.get('list').split(",")
                    }
                });
            }else{
                ret.push({
                    "name" : rec.get('name'),
                    "definition" : rec.get('definition'),
                    "uom" : rec.get('uom'),
                    "description" : rec.get('description'),
                    "constraint" : {}
                });
            }

            /*switch (rec.get('ctype')) {
                case 1: // Greater then
                    ret.push({
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : rec.get('uom'),
                        "description" : rec.get('description'),
                        "constraint" : {
                            "role" : rec.get('role'),
                            "min" : rec.get('from')
                        }
                    });
                    break;
                case 2: // Less then
                    ret.push({
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : rec.get('uom'),
                        "description" : rec.get('description'),
                        "constraint" : {
                            "role" : rec.get('role'),
                            "max" : rec.get('to')
                        }
                    });
                    break;
                case 3: // Between
                    ret.push({
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : rec.get('uom'),
                        "description" : rec.get('description'),
                        "constraint" : {
                            "role" : rec.get('role'),
                            "interval" : [rec.get('from'), rec.get('to')]
                        }
                    });
                    break;
                case 4: // List
                    ret.push({
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : rec.get('uom'),
                        "description" : rec.get('description'),
                        "constraint" : {
                            "role" : rec.get('role'),
                            "valueList" : rec.get('list').split(",")
                        }
                    });
                    break;
                default: // List
                    ret.push({
                        "name" : rec.get('name'),
                        "definition" : rec.get('definition'),
                        "uom" : rec.get('uom'),
                        "description" : rec.get('description'),
                        "constraint" : {}
                    });
                    break;
            }*/


        }
        return ret;
    },
    // Return the array of json of a given store
    getSmlStore: function(name){
        var main = Ext.getCmp(name);
        var store = main.getComponent('gridSml').getStore();
        var ret = [];
        for (var i = 0; i < store.getCount(); i++) {
            var rec = store.getAt(i);
            ret.push(rec.data);
        }
        return ret;
    },
    initSmlFieldPanel: function(name, config){
        var cmp = Ext.getCmp(name);
        var skipRemove = false;
        var skipInsert = false;
        if (Ext.isObject(config) && !Ext.isEmpty(config["removeCmb"])) {
            skipRemove = config["skipRemove"];
        }
        if (Ext.isObject(config) && !Ext.isEmpty(config["insertCmb"])) {
            skipInsert = config["skipInsert"];
        }
        cmp.getComponent('frmSml').getComponent('btnAddSml').on('click',function(){
            this.addSmlfield(name,skipRemove);
        },this);
        cmp.getComponent('gridSml').getComponent('gridToolbar').getComponent('btnRemoveSml').on('click',function(){
            var recs = Ext.getCmp('gridIdentification').getSelectionModel().getSelection();
            if (recs.length>0){
                if (recs[0].get('definition') == 'urn:ogc:def:identifier:OGC:uniqueID'){
                    Ext.MessageBox.show({
                        title: 'Warning',
                        msg: 'UniqueID is mandatory and cannot be removed',
                        buttons: Ext.MessageBox.OK
                    });
                    return
                }
            }
            this.removeSmlfield(name,skipInsert);
        },this);
    },
    addSmlfield: function(name, skipRemove){
        var main = Ext.getCmp(name);
        var form = main.getComponent('frmSml');
        var cmb = form.getComponent('cmbSml');
        var store = main.getComponent('gridSml').getStore();
        if (!form.getForm().isValid()) {
            Ext.MessageBox.show({
                title: 'Warning',
                msg: 'Mandatory params are not filled correctly',
                buttons: Ext.MessageBox.OK,
                animateTarget: form
            });
            return;
        }
        var json = form.getForm().getValues();
        var rec = cmb.findRecord(cmb.name,cmb.getValue());
        var r = Ext.create('smlfield', Ext.apply({}, json, rec.data));
        if (Ext.isEmpty(skipRemove) || skipRemove===false) {
            cmb.getStore().remove(rec);
        }
        var last = store.getCount();
        store.insert(last, r);
        form.getForm().reset();
    },
    removeSmlfield: function(name, skipInsert){
        var main = Ext.getCmp(name);
        var form = main.getComponent('frmSml');
        var cmb = form.getComponent('cmbSml');
        var grid = main.getComponent('gridSml');
        var store = grid.getStore();
        form.getForm().reset();
        var rec = grid.getSelectionModel().getSelection();
        if (Ext.isEmpty(skipInsert) || skipInsert===false) {
            cmb.getStore().insert(0,rec);
        }
        store.remove(rec);
    },
    openObsPropEditorWin: function(){
        var win = openObsPropEditorWin(this.istService);
        win.on("beforeclose",function(){
            Ext.getStore('cmbobservedproperties').removeAll();
            var cb = Ext.getCmp("cmbObservedProperty");
            cb.reset();
            cb.lastQuery = null;
        });
    },
    openUomsEditorWin: function(){
        var win = openUomsEditorWin(this.istService);
        win.on("beforeclose",function(){
            Ext.getStore('cmbuom').removeAll();
            var cb = Ext.getCmp("cmbUom");
            cb.reset();
            cb.lastQuery = null;
        });
    }
});
