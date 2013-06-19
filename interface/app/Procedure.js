/**
 * istSOS WebAdmin - Istituto Scienze della Terra
 * Copyright (C) 2013 Massimiliano Cannata, Milan Antonovic
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 */

Ext.define('istsos.store.ObservationEditor', {
    extend: 'Ext.data.Store',
    constructor: function(cfg) {
        var me = this;
        cfg = cfg || {};
        me.callParent([Ext.apply({
            proxy: {
                type: 'memory',
                reader: {
                    type: 'array',
                    idProperty: 'micro'
                }
            }
        }, cfg)]);
        this.addEvents('seriesupdated');
    }
});

Ext.define('istsos.store.EditorQiStore', {
    extend: 'Ext.data.Store',
    constructor: function(cfg) {
        var me = this;
        cfg = cfg || {};
        me.callParent([Ext.apply({
            storeId: 'editorQiStore',
            fields: [
            {
                name: 'name'
            },
            {
                name: 'description'
            }
            ]
        }, cfg)]);
    }
});

Ext.define('istsos.Sensor', {
    extend: 'Ext.util.Observable',
    service: null,
    offering: null,
    sensor: null,
    beginPosition: null,
    endPosition: null,
    meta: null,
    data: null,
    store: null,
    iso8601Field: 'iso8601',
    visible: true,
    color: "#000000",
    configsections: {},
    /**
     * {Array} storeFields
     * Array used to initialize an Ext.data.Model object.
     * 
     * storeFields = [
     *   {
     *       name: "micro",
     *       type: "int"
     *   },
     *   {
     *       name: "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601",
     *       type: "string"
     *   },
     *   {
     *       name: "urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
     *       type: "string"
     *   }
     * ]
     * 
     */
    storeFields: [],
    constructor: function(service, offering, sensor, config){
        
        if (Ext.isEmpty(service) || Ext.isEmpty(offering) || Ext.isEmpty(sensor) ) {
            throw "Service, offering and sensor parameters are mandatory!"
        }
        
        this.addEvents({
            "metadataLoaded" : true,
            "observationLoaded" : true,
            "observationSaved" : true,
            "colorchanged" : true,
            "visibilitychanged" : true
        });
        
        this.service = service;
        this.offering = offering;
        this.sensor = sensor;
        
        Ext.applyIf(this, config);
        this.callParent(arguments);
        this._loadMetadata();
        
        
    },
    // can be an iso8601 date string, a Date object or microseconds in unix time
    getObservation: function(from, to){
        
        if (Ext.isDate(from)) {
            from = Ext.Date.format(from,'c');
        }else if (Ext.isNumber(from)) {
            from = istsos.utils.micro2iso(from);
        }else{
            // Check that is a valid string in iso format
            var d = Ext.Date.parse(from,'c');
        }
        
        if (Ext.isDate(to)) {
            to = Ext.Date.format(to,'c');
        }else if (Ext.isNumber(to)) {
            to = istsos.utils.micro2iso(to);
        }else{
            // Check that is a valid string in iso format
            var d = Ext.Date.parse(to,'c');
        }
        
        Ext.Ajax.request({
            url: Ext.String.format(
                '{0}/istsos/services/{1}/operations/getobservation/' +
                'offerings/temporary/procedures/{2}/observedproperties/{3}/' +
                'eventtime/{4}/{5}', wa.url, this.service, this.sensor, 
                this.getObservedProperties().join(','), from, to),
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    for (var i = 0; i < json.data.length; i++) {
                        if (json.data[i]['name']==this.sensor) {
                            this.loadObservation(json.data[i]);
                            break;
                        }
                    }
                }
            }
        });
        
    },
    loadObservation: function(data){
        if (data['name']!=this.sensor) {
            throw "wrong data object. The data belong to " + data['name'];
        }
        this.data = data;
        var records = [], 
        values = this.data['result']['DataArray']['values'],
        field = this.data['result']['DataArray']['field'],
        fieldIdx = {};
        for (var f = 0; f < field.length; f++) {
            fieldIdx[field[f]['definition']]=f;
        }
        for (var i = 0; i < values.length; i++) {
            var row = [];
            // Estrazione dei microsecondi dalla data
            var micro = istsos.utils.iso2micro(values[i][0]);
            row.push(micro, values[i][0]);
            for (var f = 2; f < this.storeFields.length; f++) {
                
                var fieldName = this.storeConvertIdToField[this.storeFields[f]['name']];
                row.push(parseFloat(values[i][fieldIdx[fieldName]]));
                
            //row.push(parseFloat(values[i][fieldIdx[this.storeFields[f]['name']]]));
            }
            records.push(row);
        }
        this.store.loadData(records);
        this.fireEvent("observationLoaded", this);
    },
    insertObservation: function(){
        var recs = this.store.getRange();
        //var fields = this.storeFields;
        var fields = this.data.result.DataArray.field;
        var values = [];
        for (var r = 0; r < recs.length; r++) {
            var row = [];
            for (var i = 0; i < fields.length; i++) {
                
                var def = fields[i].definition;
                if (def == this.isodef) {
                    row.push(istsos.utils.micro2iso(recs[r].get('micro')));
                }else{
                    row.push(""+(recs[r].get(this.storeConvertFieldToId[def])));
                }
                
                /*
                if (fields[i].name==this.iso8601Field) {
                    continue;
                }else if (fields[i].name=='micro') {
                    row.push(istsos.utils.micro2iso(recs[r].get(fields[i].name)));
                }else{
                    row.push(""+(recs[r].get(fields[i].name)));
                }*/
            }
            values.push(row);
        }
        this.data.result.DataArray.values = values;
        this.data.result.DataArray.elementCount = ""+values.length;
        this.data.samplingTime.beginPosition = istsos.utils.micro2iso(recs[0].get('micro'));
        this.data.samplingTime.endPosition = istsos.utils.micro2iso(recs[recs.length-1].get('micro'));
                
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/operations/insertobservation',wa.url,this.service),
            scope: this,
            method: "POST",
            jsonData: {
                "AssignedSensorId" : this.getId(),
                "ForceInsert" : "true",
                "Observation" : this.data
            },
            success: function(response){
                var json = Ext.decode(response.responseText);
                
                this.commitModifications();
                
                this.fireEvent("observationSaved", this, json);
            }
        });
        
    },
    rejectModifications: function(){
        var recs = this.store.getUpdatedRecords();
        for (var i = 0; i < recs.length; i++) {
            recs[i].reject();
        }
    },
    commitModifications: function(){
        var recs = this.store.getUpdatedRecords();
        for (var i = 0; i < recs.length; i++) {
            recs[i].commit();
        }
    },
    // This is a call to wa service for the describeSensor method
    _loadMetadata: function(){
        // First getting some sensors's service config
        Ext.Ajax.request({          
            url: Ext.String.format('{0}/istsos/services/{1}/configsections',wa.url,this.service),
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (!json.success) {
                    throw "Error retreiving general service config";
                }
                this.configsections = json.data;
                this.isodef = this.configsections.urn.time;
                Ext.Ajax.request({
                    url: Ext.String.format('{0}/istsos/services/{1}/procedures/{2}',wa.url,this.service,this.sensor),
                    scope: this,
                    method: "GET",
                    success: function(response){
                        var json = Ext.decode(response.responseText);
                        this.storeConvertFieldToId = ["'"+this.isodef+"': '"+this.iso8601Field+"'"];
                        this.storeConvertIdToField = ["'"+this.iso8601Field+"': '"+this.isodef+"'"];
                        if (json.success) {
                            this.meta = json.data;
                            // Configuring store fields
                            this.storeFields = [{
                                name: "micro", // Unixtime in µs
                                type: 'int'
                            },{
                                name: this.iso8601Field,
                                //name: this.isodef,
                                type: 'string'
                            }];
                            for (var i = 1; i < this.meta.outputs.length; i++) {
                                
                                var one = Ext.id(), two = Ext.id();
                                this.storeConvertFieldToId.push(
                                    "'"+this.meta.outputs[i].definition+"': '"+one+"'",
                                    "'"+this.meta.outputs[i].definition+":qualityIndex': '"+two+"'"
                                    );
                                this.storeConvertIdToField.push(
                                    "'"+one+"': '"+this.meta.outputs[i].definition+"'",
                                    "'"+two+"': '"+this.meta.outputs[i].definition+":qualityIndex"+"'"
                                    );
                                this.storeFields.push({
                                    name: one,
                                    type: 'float'
                                },{
                                    name: two,
                                    type: 'float'
                                });
                            }
                            this.storeConvertFieldToId = Ext.decode("{"+this.storeConvertFieldToId.join(',')+"}");
                            this.storeConvertIdToField = Ext.decode("{"+this.storeConvertIdToField.join(',')+"}");
                            
                            Ext.define(this.service+'-'+this.sensor+'-model', {
                                extend: 'Ext.data.Model',
                                idProperty: "micro",
                                fields: this.storeFields
                            });
                            this.storeId = Ext.id();
                            this.store = Ext.create('istsos.store.ObservationEditor',{
                                model: this.service+'-'+this.sensor+'-model',
                                name: this.sensor
                            });
                            this.fireEvent("metadataLoaded", this);
                        }
                    }
                });
            }
        });
    },
    getDuration: function(){
        if (!Ext.isObject(this.data)) {
            throw "Duration unknown. Observation object not loaded.";
        }
        return this.data["samplingTime"]["duration"]
    },
    getId: function(){
        if (Ext.isEmpty(this.meta)) {
            throw "Sensor metadata are not initialized at all!";
        }
        return this.meta['assignedSensorId'];
    },
    getName: function(){
        return this.sensor;    
    },
    // return insitu-fixed-point, insitu-mobile-point or virtual
    getSystemType: function(){
        if (Ext.isEmpty(this.meta)) {
            throw "Sensor metadata are not initialized at all!";
        }
        for (var i = 0; i < this.meta.classification.length; i++) {
            if (this.meta.classification[i]['definition']=='urn:ogc:def:classifier:x-istsos:1.0:systemType') {
                return this.meta.classification[i]['value'];
            }
        }
    },
    // The name of the sensor type
    getSensorType: function(){
        if (Ext.isEmpty(this.meta)) {
            throw "Sensor metadata are not initialized at all!";
        }
        for (var i = 0; i < this.meta.classification.length; i++) {
            if (this.meta.classification[i]['definition'].indexOf('urn:ogc:def:classifier:x-istsos:1.0:sensorType')) {
                return this.meta.classification[i]['value'];
            }
        }
    },
    getGeoJSON: function(){
        if (Ext.isEmpty(this.meta)) {
            throw "Sensor metadata are not initialized at all!";
        }
        return this.meta['location']
    },
    getObservedProperties: function(){
        var ret = [];
        for (var i = 0; i < this.meta.outputs.length; i++) {
            if (this.meta.outputs[i]['definition']!=this.isodef) {
                ret.push(this.meta.outputs[i]['definition']);
            }
        }
        return ret;
    },
    getObservedPropertiesName: function(){
        var ret = [];
        for (var i = 0; i < this.meta.outputs.length; i++) {
            if (this.meta.outputs[i]['definition']!=this.isodef) {
                ret.push(this.meta.outputs[i]['name']);
            }
        }
        return ret;
    },
    getUomCode: function(definition){
        for (var i = 0; i < this.meta.outputs.length; i++) {
            if (this.meta.outputs[i]['definition']==definition) {
                return this.meta.outputs[i]['uom'];
            }
        }
    },
    getBeginPosition: function(){
        var ret = [];
        for (var i = 0; i < this.meta.outputs.length; i++) {
            if (this.meta.outputs[i]['definition']==this.isodef) {
                if (Ext.isArray(this.meta.outputs[i]['constraint']['interval']) 
                    && this.meta.outputs[i]['constraint']['interval'].length==2) {
                    return this.meta.outputs[i]['constraint']['interval'][0];
                }
            }
        }
        return ret;
    },
    getEndPosition: function(){
        var ret = [];
        for (var i = 0; i < this.meta.outputs.length; i++) {
            if (this.meta.outputs[i]['definition']==this.isodef) {
                if (Ext.isArray(this.meta.outputs[i]['constraint']['interval']) 
                    && this.meta.outputs[i]['constraint']['interval'].length==2) {
                    return this.meta.outputs[i]['constraint']['interval'][1];
                }
            }
        }
        return ret;
    },
    getDefaultQI: function(){
        return this.configsections.getobservation.defaultqi;
    },
    getDefaultNoData: function(){
        return parseFloat(this.configsections.getobservation.aggregatenodata);
    },
    /*
     * Change the color representing this procedure.
     * If silent = true then the event will NOT be thrown
     */
    setColor: function(color, silent){
        if (silent != true) {
            silent = false;
        }
        var old = this.color;
        this.color = color;
        if (!silent && this.color != old) {
            this.fireEvent("colorchanged", this, this.color, old);
        }
    },
    getColor: function(){
        return this.color;
    },
    /*
     * Change the visibility of this procedure.
     * If silent = true then the event will NOT be thrown
     */
    setVisibility: function(visible, silent){
        if (silent != true) {
            silent = false;
        }
        var old = this.visible;
        this.visible = visible;
        if (!silent && this.visible != old) {
            this.fireEvent("visibilitychanged", this, this.visible);
        }
    },
    getVisibility: function(){
        return this.visible;
    }
});

Ext.define('istsos.utils', {
    extend: 'Ext.util.Observable',
    statics: {
        // Convert microseconds number to isodate string
        // If offset in minutes is not given UTC will be returned
        micro2iso: function(m, offset){
            
            var offsetObj = new Date();
            offsetObj.setHours(0);
            offsetObj.setMinutes(0);
            var sign = "+";
            
            var date = new Date(parseInt(m/1000));
            var micro = parseFloat("0."+m);
            
            
            if (offset!=null) {
                date.setUTCMinutes(date.getUTCMinutes()+offset);
                if (offset<0) {
                    sign = "-";
                    offset = -1 * offset;
                    offsetObj.setMinutes(offset);
                }else{
                    offsetObj.setMinutes(offset);
                }
            }
            
            var year = date.getUTCFullYear();
            var month = (date.getUTCMonth()+1)<10?"0"+(date.getUTCMonth()+1):(date.getUTCMonth()+1);
            var day = date.getUTCDate()<10?"0"+date.getUTCDate():date.getUTCDate();
            var hour = date.getUTCHours()<10?"0"+date.getUTCHours():date.getUTCHours();
            //hour = hour + offsetObj.getHours();
            var minute = date.getUTCMinutes()<10?"0"+date.getUTCMinutes():date.getUTCMinutes();
            //minute = minute + offsetObj.getMinutes();
            
            var second = date.getUTCSeconds()<10?"0"+date.getUTCSeconds():date.getUTCSeconds();
            var micro = (""+parseFloat((""+(m/1000000)).replace(parseInt(m/1000000),"0"))).replace("0","");
            
            var tz = offset==null?"Z":sign+(offsetObj.getHours()<10?"0"+offsetObj.getHours():offsetObj.getHours())+(offsetObj.getMinutes()<10?"0"+offsetObj.getMinutes():offsetObj.getMinutes());
            
            return year + "-" + month + "-"  + day + "T" + hour+ ":" + minute + ":" + second + "" + micro + "" + tz;
            
        },
        // Extract microseconds from an isodate string 
        //  > iso date with micro seconds: "2012-10-28T01:00:00.123456+0100"
        //  > iso date with micro seconds: "2012-10-28T01:00:00+0100"
        iso2micro: function(iso){
            
            // iso = "2012-10-28T00:50:00.123456+0100" | "2012-10-28T00:50:00+0100"
            //                0      1     2        3          4        5
            // splitted = ["2012", "10", "28", "00:50:00", "123456", "0100"]
            // splitted = ["2012", "10", "28", "00:50:00", "0100"]
            var splitted = iso.split(/[T]|[.]|[,]|[+]|[-]|[z]|[Z]/g);
            
            // Splitting hours
            var hours = splitted[3].split(":");
            
            // Calculating offset
            var hoffset = 0;
            var moffset = 0;
            if (iso.match(/[Z]/g)==null) { // Already UTC
                hoffset = parseInt(parseInt(splitted[splitted.length-1])/100);
                moffset = parseInt(splitted[splitted.length-1]) - (hoffset*100);
                if (iso.match(/[+]/g)==null) {
                    hoffset = -1 * hoffset;
                    moffset = -1 * moffset;
                }
            }
            
            var milli = Date.UTC(
                parseInt(splitted[0]), // years
                parseInt(splitted[1])-1, // months
                parseInt(splitted[2]), // days
                parseInt(hours[0])-hoffset, // hours
                parseInt(hours[1])-moffset, // minutes
                parseInt(hours[2]) // seconds
                );
                    
            var match = iso.match(/[.]|[,]/g);
            if (Ext.Array.contains(match, '.') || Ext.Array.contains(match, ',')) {
                var micro = parseFloat("0."+splitted[4]);
                
                //console.log(istsos.utils.micro2iso((milli * 1000) + (micro * 1000000)));
                return (milli * 1000) + (micro * 1000000);
            } else {
                //console.log(istsos.utils.micro2iso( milli*1000));
                return milli*1000;
            }
            
        },
        getStore: function(procedure){
            
            var meta = procedure.meta;
            var service = procedure.service;
            var sensor = procedure.sensor;
            
            var storeFields = [{
                name: "micro", // Tagliamo la testa al toro -> i mems misurano ogni mezzo millisecondo (500µs)!!
                type: 'int'
            },{
                name: this.isodef,
                type: 'string'
            }];
        
            for (var i = 1; i < meta.outputs.length; i++) {
                storeFields.push({
                    name: meta.outputs[i].definition,
                    type: 'float'
                },{
                    name: meta.outputs[i].definition+":qualityIndex",
                    type: 'float'
                });
            }
            
            Ext.define(service+'-'+sensor+'-model', {
                extend: 'Ext.data.Model',
                idProperty: this.isodef,
                fields: storeFields
            });
            
            /*return Ext.create('istsos.store.ObservationEditor',{
                model: service+'-'+sensor+'-model',
                name: sensor
            });*/
            
            return Ext.create('Ext.data.Store', {
                model: service+'-'+sensor+'-model',
                name: sensor,
                proxy: {
                    type: 'memory',
                    reader: {
                        type: 'array',
                        idProperty: this.isodef
                    }
                }
            });
            
        },
        validatefilename: function(procedure, filename){
            var tmp = filename.split(/[\\/]/);
            if (tmp.length<2 || !Ext.isArray(tmp)) {
                throw "File path error";
            }
            var ext  = tmp[tmp.length-1].split(".")[1];
            if (ext != 'dat') {
                throw "File extension wrong (must be *.dat)";
            }
            tmp = tmp[tmp.length-1].split(".")[0];
            var ep = tmp.split("_");
            if (ep.length<2 || !Ext.isArray(ep)) {
                throw "File name format error";
            }
            ep = ep[ep.length-1];
            // tmp = tmp.replace("_"+ep,"");
            // Extracting the end position date
            //  > date in file names are always in Greenwich time (GMT)
            ep = Ext.Date.parse(ep+"0", "YmdHisZ");
            // Checking File nema prefix must be equal the procedure name
            if (tmp!=procedure.getName()) {
                throw "File name format error, '" + tmp + "'"
                + " is is not valid for '" + procedure.getName() + "' procedure";
            }
            return true;
        },
        parsecsvfile: function(procedure, fileList, filename, callback){
            this.getParser().parsecsvfile(procedure, fileList, filename, function(progressEvent){
                callback(istsos.utils.parsecsvstring(procedure, progressEvent.target.result));
            });
        },
        // Return an object that can read the csv file and throw an event when finisched
        getParser: function(){
            return Ext.create('Ext.util.Observable', {
                events: ['csvfileparsed'],
                parsecsvfile: function(procedure, fileList, filename, callback){
                    if (Ext.isFunction(callback)) {
                        this.callback = callback;
                    }else{
                        delete this.callback;
                    }
                    var reader = new FileReader();
                    try {
                        for (var i = 0; i < fileList.length; i++) {
                            reader.parser = this;
                            reader.addEventListener('load', function (e) {
                                if (Ext.isFunction(this.parser.callback)) {
                                    this.parser.callback(e);
                                }
                                this.parser.fireEvent('csvfileparsed', e.target.result);
                            }, false);     
                            reader.readAsText(fileList[i]);
                        }
                    } catch (exception) { 
                        Ext.Msg.alert('Warning', exception);           
                    } 
                }
            });
        },
        // Convert microseconds number to isodate string
        /*
         * Parse a csv and return an object like this:
         * {
         *      "data": [
         *          [
         *              {
         *                  "micro": 123234253456, // microseconds
         *                  "urn:ogc:def:parameter:x-istsos::time:iso8601": "2012-12-09T14:12Z",
         *                  "urn:ogc:def:parameter:x-istsos::foobar": "12.5",
         *                  "urn:ogc:def:parameter:x-istsos::foobar:qualityIndex": "100"
         *              },
         *              ...
         *          ]
         *      ],
         *      "total": 23,
         *      "begin": "2012-12-09T14:12Z",
         *      "end": "2012-12-10T14:00Z"
         * }
         */
        parsecsvstring: function(procedure, csvstring){            
            var lines = csvstring.split(/[\r\n|\n]+/);             
            var ret = {
                data: [],
                header: ["micro"],
                total: 0,
                begin: null, 
                end: null,
                isregular: true,
                timeresolutions: [],
                timeresolutionscheck: []
            }, header = lines[0].split(",");                
            try {                
                if (lines.length<2) {
                    throw "CSV file contain less then the minimal 2 line (header + value)";
                }
                // Detecting procedure's observation properties order
                var opcomposition = [];
                var properties = procedure.meta.outputs;
                for (c = 0; c < properties.length ; c++) {                    
                    // Check if the output observed properties exist in the CSV
                    if(!Ext.Array.contains(
                        header, properties[c].definition) ){
                        throw "CSV observed properties in header are not correct"
                    }                    
                    if (properties[c].definition == this.isodef) {
                        opcomposition.push(properties[c].definition);
                    }else{
                        opcomposition.push(
                            properties[c].definition,
                            properties[c].definition+":qualityIndex"
                            );
                    }
                }             
                ret.header = ret.header.concat(opcomposition);
                // Getting the time column position in the csv file
                var idx = Ext.Array.indexOf(header, this.isodef);                
                // csv begin position
                var bp = Ext.Date.parse(lines[1].split(",")[idx],"c");                
                // Get microseconds of first date
                ret.begin = istsos.utils.iso2micro(lines[1].split(",")[idx]);                
                // csv end position
                var ep;
                // reverse loop because sometimes last rows are empty
                for(var c=(lines.length-1);c>0;c--) {
                    if (lines[c].split(",").length==header.length) {
                        ep = Ext.Date.parse(lines[c].split(",")[idx],"c");
                        // Get microseconds of last date
                        ret.end = istsos.utils.iso2micro(lines[1].split(",")[idx]);
                        break;
                    }
                }
                // statistics counters
                var updated = 0, inserted = 0;
                try {
                    var idxStart=0;      
                    var lastDate;
                    for(c=1;c<lines.length;c++) { // start looping csv lines >>
                        var row = [];
                        var line = lines[c].split(",");
                        // csv observed properties must be lenght exacly as 
                        //   the procedure observed property 
                        if (line.length!=header.length) {
                            // Skip empty rows
                            if (line.length==1 && line[0]=="") {
                                continue;
                            }
                            throw ("Length mismatch from header definition");
                        }
                        for (var i = 0; i < opcomposition.length; i++) {
                            // finding the observed property position in the csv
                            idx = Ext.Array.indexOf(header, opcomposition[i]);      
                            if (idx < 0) { // CSV does not have observed property
                                if (opcomposition[i].indexOf(":qualityIndex")<0) {
                                    // Quality index are not mandatory, other output obs.prop are mandatory
                                    throw ("Mandatory procedures output observed property \"" + opcomposition[i] + "\" is not present in the CSV text");
                                }
                                row.push(parseInt(procedure.getDefaultQI()));
                            }else{
                                if (opcomposition[i]==this.isodef) { // If isodate field
                                    var micro = istsos.utils.iso2micro(line[idx]);
                                    //var date = Ext.Date.parse(line[idx],"c");
                                    row.push(micro, line[idx]);
                                    // Prepare info about time resolutions of this timeseries
                                    if (lastDate) {
                                        var delta = micro - lastDate;
                                        if (!Ext.Array.contains(ret.timeresolutions, delta)) {
                                            ret.isregular = false;
                                            ret.timeresolutions.push(delta);
                                            ret.timeresolutionscheck.push(line[idx]);
                                        }
                                    }
                                    lastDate = micro;
                                }else{
                                    if(line[idx]!=''){ // All other observed properties
                                        row.push(parseFloat(line[idx]));
                                    }
                                }
                            }
                        }
                        ret.total += 1;
                        ret.data.push(row);
                    }
                } catch (exception) { 
                    throw "Riga [" + (c+1) + "]:" + exception;
                }
            } catch (exception) { 
                Ext.Msg.alert('Warning', exception);   
            }
            return ret;
        }
    }
});


/*
Ext.define('istsos.Procedure', {
    extend: 'Ext.util.Observable',
    constructor: function(config){
        
        
        this.addEvents({
            "saved" : true,
            "loaded" : true
        });
        
        Ext.applyIf(this, config);
        
        var qis = Ext.create('istsos.store.EditorQiStore',{
            storeId: this.id+'-editorQiStore',
            proxy: {
                type: 'ajax',
                url: Ext.String.format("{0}/istsos/services/{1}/dataqualities", wa.url,this.service),
                reader: {
                    type: 'json',
                    root: 'data'
                }
            }
        });
        qis.load();
        
        // init store
        this.store = null;
        this.callParent(arguments)
    },
    load: function(begin, end){
    
    },
    commit: function(){
    
    },
    isDirty: function(){
        return true;
    },
    initStore: function(obsColl){
        
        this.template = obsColl;
        
        
        // ***********************************************
        // Initializing grid columns
        //   dynamic column grid initialization
        // ***********************************************
        this.columns = [{
            xtype: 'datecolumn',
            dataIndex: wa.isodef, // isodate is always present at position one
            flex: 0.7,
            header: 'Date',
            format: 'c'
        }];
        
        var properties = obsColl.result.DataArray.field;
        for (var i = 1; i < properties.length; i++) {
            
            this.columns.push({
                xtype: 'numbercolumn',
                format: '0,000.000000',
                dataIndex: properties[i].definition,
                flex: 0.4,
                text: properties[i].name,
                field: {
                    xtype: 'numberfield',
                    decimalPrecision: 6,
                    hideLabel: true,
                    listeners: {
                        change: function(form, newValue, oldValue, eOpts){
                            console.log("change: ");
                            console.dir(arguments);
                        }
                    }
                }
            },{
                xtype: 'gridcolumn',
                dataIndex: Ext.String.format('{0}:qualityIndex',properties[i].definition),
                flex: 0.3,
                text: 'qualityIndex',
                //text: Ext.String.format('{0}:qualityIndex',properties[i].name),
                field: {
                    xtype: 'combobox',
                    queryMode: 'local',
                    allowBlank: false,
                    hideLabel: true,
                    displayField: 'name',
                    store: this.id+'-editorQiStore',
                    valueField: 'name',
                    anchor: '100%'
                }
            });
            i++;
        }
        
        
        // ***********************************************
        // Initializing store fields
        // ***********************************************
        // Dynamic fields store initialization
        this.strFields = [{
            dateFormat: 'c',
            name: wa.isodef,
            type: 'date'
        }];
        
        //var properties = obsColl.result.DataArray.field;
        for (var i = 1; i < properties.length; i++) {
            this.strFields.push({
                name: properties[i].definition,
                type: 'float'
            });
        }
        
        
        Ext.define(this.description.system_id+'Model', {
            extend: 'Ext.data.Model',
            idProperty: wa.isodef,
            fields: this.strFields
        });
        
        this.storeId = Ext.id();
        var obs = obsColl.result.DataArray.values;
        this.store = Ext.create('istsos.store.ObservationEditor',{
            storeId: this.storeId,
            name: obsColl.name,
            model: this.description.system_id+'Model',
            totalCount: obs.length
        });
        var data = [];
        
        // *****************************************************
        // When loading data some extra statistics are collected
        // *****************************************************
        // 1. Number of observations
        this.total = obs.length;
        // 2. Time resolution/interval 
        //this.timeresolution = null;
        this.timeresolutions = [];
        if(obs.length>=2){
            //this.timeresolution = Ext.Date.parse(obs[1][0], "c").getTime()-Ext.Date.parse(obs[0][0], "c").getTime();
            this.timeresolutions = [Ext.Date.parse(obs[1][0], "c").getTime()-Ext.Date.parse(obs[0][0], "c").getTime()];
        }
        // 3. regular or irregular timeseries boolean
        this.isregular = true;
        this.bp = Ext.Date.parse(obs[0][0], "c");
        this.ep = Ext.Date.parse(obs[obs.length-1][0], "c");
        for (i = 0; i < obs.length; i++) {
            var rec = [];
            rec.push(Ext.Date.parse(obs[i][0], "c"));
            //chartStore[rec[0]]=[];
            for (var c = 1; c < obs[i].length; c++) {
                rec.push(parseFloat(obs[i][c]));
            //chartStore[rec[0]].push(parseFloat(obs[i][c]));
            }
            data.push(rec);
            // Check resolution
            if (i>=1) {
                var res = data[i][0].getTime()-data[i-1][0].getTime();
                if (!Ext.Array.contains(this.timeresolutions, res)) {
                    console.log(data[i][0]);
                    this.isregular = false;
                    this.timeresolutions.push(res);
                }
            }
        }
        this.store.loadData(data);
        
        this.timeresolutions = Ext.Array.unique(this.timeresolutions);
        
        var f = Ext.getCmp(this.resid);
        
        var tr = [];
        for (i = 0; i < this.timeresolutions.length; i++) {
            if (this.timeresolutions[i]>10) {
                tr.push(centisecsToISODuration(this.timeresolutions[i]/10));
            }
        }
        
        f.setValue(tr.join(", "));
        f.setVisible(true);
        
        f = Ext.getCmp(this.obsid);
        f.setValue(this.total + " observations");
        f.setVisible(true);
        
        if (!this.isregular) {
            f = Ext.getCmp(this.intid);
            f.setVisible(true);
        }
    
    },
    //Create a grid that fit the internal store
    getGrid: function(observedProperty){
        for (var i = 1; i < this.columns.length; i++) {
            if (this.columns[i]['dataIndex']!=observedProperty && 
                this.columns[i]['dataIndex']!=observedProperty+':qualityIndex') {
                this.columns[i]['hidden']=true;
            }
        }
        this.grid = Ext.create('Ext.grid.Panel', {
            xtype: 'grid',
            id: 'oegrid',
            title: '',
            store: this.storeId,
            autoRender: true,
            autoScroll: true,
            viewConfig: {
            
            },
            columns: this.columns,
            plugins: [Ext.create('Ext.grid.plugin.CellEditing')],
            selModel: Ext.create('Ext.selection.RowModel', {
                allowDeselect: true,
                mode: 'MULTI'
            }),
            dockedItems: [
            {
                xtype: 'toolbar',
                dock: 'top',
                items: [
                {
                    xtype: 'filefield',
                    //fieldLabel : 'CSV',
                    emptyText: 'Load CSV..',
                    labelWidth: 40,
                    listeners: {
                        change: this.loadCsv,
                        scope: this
                    }
                },
                {
                    xtype: 'button',
                    flex: 1,
                    id: 'btnSelectAll',
                    text: 'Select all',
                    handler: function(){
                        var selectionModel = this.grid.getSelectionModel();
                        selectionModel.selectAll(true);
                    },
                    scope: this
                }
                ]
            }
            ]
        });
        return this.grid;
    },
    loadCsv: function(field, value, eOpts){
        console.dir(arguments);
        var files = field.fileInputEl.dom.files;
        var reader = new FileReader();
        try {
            
            // Checking file path format
            var tmp = value.split(/[\\/]/);
            if (tmp.length<2 || !Ext.isArray(tmp)) {
                throw "File path error";
            }
            // Checking the file name format
            tmp = tmp[tmp.length-1].split(".")[0];
            // getting end position
            var ep = tmp.split("_");
            
            if (ep.length<2 || !Ext.isArray(ep)) {
                throw "File name format error";
            }
            
            ep = ep[ep.length-1];
            tmp = tmp.replace("_"+ep,"");
            
            // Extracting the end position date
            //  > date in file names are always in Greenwich time (GMT)
            ep = Ext.Date.parse(ep+"0", "YmdHisZ");
            console.log(ep);
            
            // Checking File nema prefix must be equal the procedure name
            if (tmp!=this.description.system_id) {
                throw "File name format error, '" + tmp + "'"
                + " is different from '" + this.description.system_id + "'";
            }
            
            for (var i = 0; i < files.length; i++) {
                reader.istProcedure = this;
                reader.addEventListener('load', function (e) {
                    this.istProcedure.parseCSV(e.target.result);
                }, false);     
                reader.readAsText(files[i]);
            }
        
        } catch (exception) { 
            Ext.Msg.alert('Warning', exception);           
        } 
    },
    parseCSV: function(csvstring){
        var lines = csvstring.split(/[\r\n|\n]+/); 
        try {
            if (lines.length<2) {
                throw "CSV file contain less then the minimal 2 line (header + value)";
            }
            // Comparing CSV obsprop and real procedure's obsprop
            var csvObsProp = lines[0].split(",");
            // Detecting local store observation properties order
            var tplObsprop = [];
            var properties = this.template.result.DataArray.field;
            for (c = 0; c < properties.length ; c++) {
                tplObsprop.push(properties[c].definition);
                if(!Ext.Array.contains(
                    csvObsProp, properties[c].definition) ){
                    throw "CSV observed properties in header are not correct"
                }
            }
            
            // Getting the time column position in the csv file
            var idx = Ext.Array.indexOf(csvObsProp, wa.isodef);
            // csv begin position
            var bp = Ext.Date.parse(lines[1].split(",")[idx],"c");
            // csv end position
            var ep;
            // loop because sometimes last rows are empty
            for(var c=(lines.length-1);c>0;c--) { 
                if (lines[c].split(",").length==tplObsprop.length) {
                    ep = Ext.Date.parse(lines[c].split(",")[idx],"c");
                    break;
                }
            }
            
            // Some statistics counter
            var updated = 0, inserted = 0;
            
            var data = [];
            this.store.suspendEvents();
            try {
                var idxStart=0;      
                var lastDate;
                for(c=1;c<lines.length;c++) { // start looping csv lines >>
                    var row = [];
                    var line = lines[c].split(",");
                    // csv observed properties must be exacly as 
                    //   the procedure observed property 
                    if (line.length==tplObsprop.length) { 
                        var id;
                        for (var i = 0; i < tplObsprop.length; i++) {
                            // finding the csv observed property position
                            idx = Ext.Array.indexOf(csvObsProp, tplObsprop[i]);                    
                            if (tplObsprop[i]==wa.isodef) {
                                id = Ext.Date.parse(line[idx],"c");
                                row.push(Ext.Date.clone(id));
                                // check regularity
                                if (lastDate) {
                                    var res = id.getTime() - lastDate;
                                    if (!Ext.Array.contains(this.timeresolutions, res)) {
                                        console.log(data[i][0]);
                                        this.isregular = false;
                                        this.timeresolutions.push(res);
                                    }
                                }
                                lastDate = id.getTime();
                            }else{
                                if(line[idx]!=''){
                                    row.push(parseFloat(line[idx]));
                                }
                            }
                        }
                        
                        if (this.bp.getTime() > id.getTime() || 
                            this.ep.getTime() < id.getTime()) {
                            //this.store.loadData([row],true);
                            data.push(row);
                            inserted++;
                        }else{
                            var index = this.store.find(wa.isodef,id,idxStart);
                            if (index==-1) {
                                //this.store.loadData([row],true);
                                data.push(row);
                                inserted++;
                            }else{
                                var rec = this.store.getAt(index);
                                rec.beginEdit();
                                for (i = 0; i < tplObsprop.length; i++) {
                                    if (tplObsprop[i]!=wa.isodef) {
                                        rec.set(tplObsprop[i],row[i]);
                                    }
                                }
                                rec.endEdit(true);
                                idxStart = index+1;
                                updated++;
                            }
                        }
                    }
                };
                this.store.loadData(data,true);
                
                if (this.bp.getTime() > bp.getTime()){
                    this.bp = bp;
                }
                
                if (this.ep.getTime() < ep.getTime()){
                    this.ep = ep;
                }
                
            } catch (exception) { 
                throw "Riga [" + (c+1) + "]:" + exception;
            } finally {
                console.log("Sorting.. and resuming events.");
                this.store.sort(wa.isodef, 'ASC');
                this.store.resumeEvents();        
            }
            
            console.log("CSV stats:");
            console.log("Updated: " + updated);
            console.log("Inserted: " + inserted);
            
            var f = Ext.getCmp(this.resid);
            var tr = [];
            for (i = 0; i < this.timeresolutions.length; i++) {
                if (this.timeresolutions[i]>10) {
                    tr.push(centisecsToISODuration(this.timeresolutions[i]/10));
                }
            }
            f.setValue(tr.join(", "));
        
            Ext.getCmp('chartpanel').initChartStore(false);
            
            
        // Check empty / no data holes ;)
            
            
            
            
        } catch (exception) { 
            Ext.Msg.alert('Warning', exception);   
        }
    
    },
    getCheckbox: function(){
        this.formid = "proc-" + Ext.id();
        this.resid = Ext.id();
        this.obsid = Ext.id();
        this.intid = Ext.id();
        var begin, end;
        var obsprop = [];
        var d = this.description;      
        for (var i = 0; i < d.outputs.length; i++) {
            if (d.outputs[i]["definition"]==wa.isodef) {
                if (!Ext.isEmpty(d.outputs[i]['constraint']['interval'])) {
                    var interval = Ext.Array.clone(d.outputs[i]['constraint']['interval']);
                    try{
                        //begin = Ext.Date.format(interval[0],'c');
                        begin = interval[0];
                    }catch (e){
                        begin = "null";
                    }
                    try{
                        //end = Ext.Date.format(interval[1],'c');
                        end = interval[1];
                    }catch (e){
                        end = "null";
                    }
                }
            }else{
                obsprop.push(d.outputs[i]["name"]);
            }
        }
        
        return {
            xtype: 'fieldset',
            layout: {
                type: 'column'
            },
            id: this.formid,
            padding: 10,
            collapsible: false,
            checkboxToggle: true,
            checkboxName: this.description.system_id,
            title: this.description.system_id,
            defaults: {
                labelWidth: 70,
                xtype: 'displayfield',
                anchor: '100%',
                columnWidth: 1
            },
            items: [
            {
                fieldLabel: 'From',
                value: begin
            },
            {
                fieldLabel: 'To',
                value: end
            },
            {
                fieldLabel: 'Observed',
                value: obsprop.join(", ")
            },
            {
                fieldLabel: 'Resolution',
                id: this.resid,
                hidden: true,
                value: ""
            },
            {
                fieldLabel: 'Loaded',
                id: this.obsid,
                hidden: true,
                value: ""
            },
            {
                fieldLabel: 'Interpolate',
                id: this.intid,
                xtype: 'checkbox',
                hidden: true,
                value: false,
                listeners: {
                    change: function (field, newValue, oldValue, eOpts) {
                        console.log(arguments, "id: " + this.intid);
                        if(newValue){
                            this.interpolate();
                        }
                    },
                    scope: this
                }
            }
            ]
        };
    },
    getObservedProperties: function(){
        var out = this.description.outputs;
        var ret = [];
        for (var i = 0; i < out.length; i++) {
            if (out[i].definition!=wa.isodef) {
                ret.push(out[i].definition);
            }
        }
        return ret;
    },
    interpolate: function(){
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        var chart = Ext.getCmp('chartpanel');
        var cd = chart.chartdata;
        var colIdx = chart.chart.indexFromSetName(this.store.name);
        if(cd[0][colIdx]==null){
            Ext.Msg.alert('Warning', 'Interpolation not possible if the series stars with no value.');
        }
        var templ = [];
        var obsIdx = null; //Ext.Array.indexOf(this.strFields,obsprop);
        for (i = 0; i < this.strFields.length; i++) {
            if (this.strFields[i].name==obsprop) {
                obsIdx = i;
            }
            templ.push(null);
        }
        this.store.suspendEvents();
        for (var i = 1; i < cd.length; i++) {
            if (cd[i][colIdx]==null) {
                var id1 = i-1;
                var id2 = id1+1;
                var x = cd[i][0].getTime();
                var rec0 = this.store.getAt(id1);
                var rec1 = this.store.getAt(id2);
                //var rec1 = this.store.findRecord(wa.isodef,id2);
                var x0=rec0.get(wa.isodef).getTime();
                var y0=rec0.get(obsprop);
                var x1=rec1.get(wa.isodef).getTime();
                var y1=rec1.get(obsprop);
                // Interpolation function
                var y = y0 + ((y1-y0)/(x1-x0))*(x-x0);
                
                var data = Ext.Array.clone(templ);
                data[0] = Ext.Date.clone(cd[i][0]);
                data[obsIdx] = y;
                this.store.loadData([data],true);
            }
        }
        this.store.sort(wa.isodef, 'ASC');
        this.store.resumeEvents();
        
        chart._editedSeriesUpdate(this.store, this.store.getRange());
    
    }
});*/


