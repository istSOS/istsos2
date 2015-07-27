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
            "visibilitychanged" : true,
            "aggregationchanged" : true
        });
        
        this.service = service;
        this.offering = offering;
        this.sensor = sensor;
        
        Ext.applyIf(this, config);
        this.callParent(arguments);
        this._loadMetadata();
        
        
    },
    // can be an iso8601 date string, a Date object or microseconds in unix time
    getObservation: function(from, to, tz, aggregateObj){
        /*
            [optional] 
            aggregateObj = {
                f: 'SUM', //aggregatefunction
                i: 'SUM', //aggregateinterval
                nd: '-999.9', //aggregatenodata
                ndqi: '210' //aggregatenodataqi
            }
        */
        
        var params = {};
        
        var format = Ext.isEmpty(tz) ? "c": "Y-m-d\\TH:i:s";
        
        if (Ext.isDate(from)) {
            from = Ext.Date.format(from,format);
            if(!Ext.isEmpty(tz)){
                from = from + (Ext.isString(tz) ? tz: istsos.utils.minutesToTz(tz));
            }
        }else if (Ext.isNumber(from)) {
            if (Ext.isEmpty(tz)){
                from = istsos.utils.micro2iso(from);
            }else{
                from = istsos.utils.micro2iso(from, (Ext.isString(tz) ? istsos.utils.minutesToTz(tz) : tz));
            }
            //from = istsos.utils.micro2iso(from);
        }else{
            // Check that is a valid string in iso format
            var d = Ext.Date.parse(from,'c');
            throw "Error in istsos.utils.getObservation";
        }
        
        if (Ext.isDate(to)) {
            to = Ext.Date.format(to,format);
            if(!Ext.isEmpty(tz)){
                to = to + (Ext.isString(tz) ? tz: istsos.utils.minutesToTz(tz));
            }
        }else if (Ext.isNumber(to)) {
            if (Ext.isEmpty(tz)){
                to = istsos.utils.micro2iso(to);
            }else{
                to = istsos.utils.micro2iso(to, (Ext.isString(tz) ? istsos.utils.minutesToTz(tz) : tz));
            }
        }else{
            // Check that is a valid string in iso format
            var d = Ext.Date.parse(to,'c');
            throw "Error in istsos.utils.getObservation";
        }
        
        
        if (Ext.isObject(aggregateObj)){
            params = Ext.apply(params,{
                aggregatefunction: aggregateObj.f,
                aggregateinterval: aggregateObj.i,
                aggregatenodata: aggregateObj.nd,
                aggregatenodataqi: aggregateObj.ndqi
            });
        }
        
        Ext.Ajax.request({
            url: Ext.String.format(
                '{0}/istsos/services/{1}/operations/getobservation/' +
                'offerings/{2}/procedures/{3}/observedproperties/{4}/' +
                'eventtime/{5}/{6}', wa.url, this.service,  this.offering,
                this.sensor, this.getObservedProperties().join(','), from, to),
            scope: this,
            method: "GET",
            params: params,
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
    
        var recs = this.store.getUpdatedRecords(),
          fields = this.data.result.DataArray.field,
          values = [[]]
          prev = null;
          
        for (var r = 0; r < recs.length; r++) {
        
          var rec = recs[r];
          var idx = this.store.indexOf(rec);
          var row = [];
          
          for (var i = 0; i < fields.length; i++) {
            var def = fields[i].definition;
            if (def == this.isodef) {
              row.push(istsos.utils.micro2iso(rec.get('micro')));
            }else{
              row.push(""+(rec.get(this.storeConvertFieldToId[def])));
            }
          }
          
          if (prev == null || (prev+1)==idx){
            values[values.length-1].push(row);
          }else{
            values.push([]);
            values[values.length-1].push(row);
          }
          prev = idx;
          
        }
        
        var queue = {
          procedure: this,
          values: values,
          insert: function(response){
          
            if(this.values.length>0){
            
              var value = this.values.shift();
            
              this.procedure.data.result.DataArray.values = value;
              this.procedure.data.result.DataArray.elementCount = ""+value.length;
              this.procedure.data.samplingTime.beginPosition = value[0][0];
              this.procedure.data.samplingTime.endPosition = value[value.length-1][0];
            
              Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/operations/insertobservation',wa.url,this.procedure.service),
                scope: this,
                method: "POST",
                jsonData: {
                  "AssignedSensorId" : this.procedure.getId(),
                  "ForceInsert" : "true",
                  "Observation" : this.procedure.data
                },
                success: function(response){
                  this.insert(response);
                }
              });
              
            }else{
              var json = Ext.decode(response.responseText);
              this.procedure.commitModifications();
              this.procedure.fireEvent("observationSaved", this.procedure, json);
            }
          }
        }
        
        queue.insert(null);
        
        console.log(values);
        
        /*var recs = this.store.getRange();
        
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
        */
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
    },
    setAggregation: function(aggregation){
        this.aggregation = aggregation;
        this.fireEvent("aggregationchanged", this, this.aggregation);
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
        minutesToTz: function(offset){
            if (Ext.isEmpty(offset)){
                offset = (new Date()).getTimezoneOffset()/-60;
            }
            return (parseInt(offset)>=0?'+':'-') + this.pad(parseInt(offset)) + ':' + this.pad(Math.abs(((offset - parseInt(offset)) * 60 )));
        },
        tzToMinutes: function(tz){
            var hm = tz.split(':');
            return (parseInt(hm[0])*60) + parseInt(hm[1]);
        },
        validateTz: function (value){
            /*
                Validating TZ string:
                Example: +02:00
            */
            var tz = "TZ format shall be +HH:MM";
            if (value.length!=6) {
                return tz;
            }
            if (value[0]!='-' && value[0]!='+') {
                return tz;
            }
            if (value.indexOf(':')!=3){
                return tz;
            }
            var h = parseInt( (value[1]+value[2]));
            var m = parseInt( (value[4]+value[5]));
            
            if (h>23){
                return tz;
            }
            if (m>59){
                return tz;
            }
            return true;
        },
        pad: function(n){
            if (n>=0 && n<10) {
                return '0'+n;
            }else if(n<0 && n>-10){
                return '-0'+(-1*n);
            }
            return n;
            // return n<10 ? '0'+n : n
        },
        // Extract microseconds from an isodate string 
        //  > iso date with micro seconds: "2012-10-28T01:00:00.123456+0100"
        //  > iso date with micro seconds: "2012-10-28T01:00:00+0100"
        iso2micro: function(iso){
            
            // iso = "2012-10-28T00:50:00.123456+0100" | "2012-10-28T00:50:00+0100"
            // iso = "2012-10-28T00:50:00.123456+0100" | "2012-10-28T00:50:00+01:00" << After OGC compl. tests
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
                
                if (splitted[splitted.length-1].indexOf(":")>-1){
                    splitted[splitted.length-1] = splitted[splitted.length-1].replace(":","");
                }
            
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
            if (match != null && ( Ext.Array.contains(match, '.') || Ext.Array.contains(match, ','))) {
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
