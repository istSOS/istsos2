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

Ext.define('istsos.view.Chart', {
    
    extend: 'istsos.view.ui.Chart',
    
    initComponent: function() {
        
        Ext.create('istsos.store.Offerings');
        Ext.create('istsos.store.gridProceduresList');
        Ext.create('istsos.store.ObservedProperties');
        
        var ssrv = Ext.create('istsos.store.Services');
        ssrv.getProxy().url = Ext.String.format('{0}/istsos/services',wa.url);
        
        
        /*Ext.create('istsos.store.gridProceduresList',{
            storeId: 'editableProcedure'
        });*/
        
        Ext.create('Ext.data.Store', {
            storeId: 'editableProcedure',
            proxy: {
                type: 'ajax',
                reader: {
                    type: 'json',
                    idProperty: 'name',
                    root: 'data'
                }
            },
            fields: [
            {
                name: 'name',
                sortType: 'asText',
                type: 'string'
            },
            {
                name: 'offerings'
            },
            {
                name: 'observedproperties'
            }
            ]
        });
        
        this.procedures = {};
        
        this.callParent(arguments);
        
        Ext.getCmp('calccnt').add(Ext.create('istsos.view.Calc',{
            id: 'calcpanel',
            chartpanel: this
        }));
        
        this.addEvents('seriesSelected','procedureAdded','queueLoaded');
        
        var offset = (new Date()).getTimezoneOffset()/-60;
        var tz = ((offset > 0) ? "+"+pad(offset) : pad(offset));
        Ext.getCmp('oeBeginTime').format = 'H:i ['+tz+']';
        Ext.getCmp('oeBeginTime').setValue(Ext.Date.parse("00:00", 'H:i'));
        Ext.getCmp('oeEndTime').format = 'H:i ['+tz+']';
        Ext.getCmp('oeEndTime').setValue(Ext.Date.parse("00:00", 'H:i'));
        
        
        // ********************************************************************
        // Initializing events for "choose procedure" panel"
        
        /*Ext.getCmp("cmbServices").on("select",function(combo, records, eOpts){
            var o = Ext.getCmp('oeCbOffering');
            o.reset();
            o.disable();
            Ext.getCmp('oeCbObservedProperty').disable();
            o.getStore().load({
                url: Ext.String.format('{0}/istsos/services/{1}/offerings/operations/getlist',
                    wa.url,combo.getValue()),
                callback: function(records, operation, success){
                    this.enable();
                },
                scope: o
            });
        });
        
        Ext.getCmp("oeCbOffering").on("select",function(combo, records, eOpts){
            
            var pr = Ext.getCmp('oeCbProcedure');
            pr.reset();
            pr.disable();
            
            var ob = Ext.getCmp('oeCbObservedProperty');
            ob.reset();
            ob.disable();
            
            pr.getStore().load({
                url: Ext.String.format('{0}/istsos/services/{1}/offerings/{2}/procedures/operations/memberslist',
                    wa.url,Ext.getCmp('cmbServices').getValue(),combo.getValue()),
                callback: function(records, operation, success){
                    this.enable();
                },
                scope: pr
            });
        });*/
        
        
        /*Ext.getCmp('pchoose').on("procedureAdded",function(procedure) {
            this.addProcedure(procedure);
        },Ext.getCmp('chartpanel'));*/
        
        /*Ext.getCmp("btnAdd").on("click",function(btn, e, eOpts){
            
            // Add an istsos.Procedure in the this.procedures array
            // every row contains some describeSensor data
            var service = Ext.getCmp("cmbServices").getValue();
            var offering = Ext.getCmp("oeCbOffering").getValue();
            var procedure = Ext.getCmp("oeCbProcedure").getValue();
            
            this.procedures[procedure] = Ext.create('istsos.Sensor', 
                service, offering, procedure, {
                    listeners: {
                        metadataLoaded: this.addProcedure,
                        scope: this
                    }
                });
                       
        },this);*/
        
        //this.on("procedureAdded",this.redrawProcedures, this);
        
        
        
        // ********************************************************************
        // Initializing events for "PLOT DATA" panel"
        
        Ext.getCmp("btnPlot").on("click",function(){
            
            var begin = Ext.getCmp('oeBegin').getValue();
            var bt = Ext.getCmp('oeBeginTime').getValue();
            begin.setHours(bt.getHours());
            begin.setMinutes(bt.getMinutes());
            
            var end = Ext.getCmp('oeEnd').getValue();
            var et = Ext.getCmp('oeEndTime').getValue();
            end.setHours(et.getHours());
            end.setMinutes(et.getMinutes());
            
            // Load data based on the date-time fields
            this.loading = [];
            for (var key in this.procedures) {
                this.loading.push(key);
                this.procedures[key].on("observationLoaded",function(p){
                    console.log("Loaded: " + p.getName());
                    Ext.Array.remove(this.loading,p.getName());
                    if (this.loading.length==0) {
                        console.log("Queue Loaded.");
                        this.fireEvent("queueLoaded",this);
                    }
                },this,{
                    single: true
                });
                this.procedures[key].getObservation(begin,end);
            }
        }, this);
        this.on("queueLoaded",this._initChartStore, this);
        
        Ext.getCmp("btnCancelEditor").on("click",function(btn, e, eOpts){
            Ext.getCmp('plotcalc').getLayout().setActiveItem(0);
            Ext.getCmp('chartgridcnt').removeAll();
            Ext.getCmp('btnStartEditor').setText('Start editing');
            Ext.getCmp('btnStartEditor').enable();
            btn.setVisible(false);
        });
        
        Ext.getCmp("btnStartEditor").on("click",function(btn, e, eOpts){
            
            var sel = Ext.getCmp('oeCbEditableProcedures').getValue();
            var proc = this.procedures[sel];
            
            if (btn.getText() == 'Start editing') {
                
                var obsProp = Ext.getCmp('oeCbObservedProperty').getValue();
                //var grid = proc.getGrid(obsProp);
                var grid = this._getGrid(sel);
                
                grid.on("selectionchange",function(model, records, eOpts) {
                    
                    if (records[0]) {
                        
                        var rec, p = {};
                        if (records.length==1) {
                            rec = records[0];
                            p['xval'] = rec.get('micro');
                            this.pointClickCallback({
                                'shiftKey': false
                            },p,true);
                        
                        }else if (records.length>1) {
                            
                            if(model.store.data.length==records.length){
                                records = model.store.getRange();
                            }
                            
                            this.chart.setAnnotations([]);
                            
                            rec = records[0];
                            p['xval'] = rec.get('micro');
                            this.pointClickCallback({
                                'shiftKey': false
                            },p,true);
                            
                            rec = records[records.length-1];
                            p['xval'] = rec.get('micro');
                            this.pointClickCallback({
                                'shiftKey': true
                            },p,true);
                        }
                    }
                    
                },this);
                
                Ext.getCmp("btnCancelEditor").setVisible(true);
                btn.disable();
                btn.setText('Apply changes');
                
                grid.getStore().on("update",function(s, e){
                    this.enable();
                },btn,{
                    single: true
                });
                grid.getStore().on("seriesupdated",function(s, e){
                    this.enable();
                },btn,{
                    single: true
                });
                
                grid.getStore().on("update",this._editedRowUpdate,this);
            
                grid.getStore().on("seriesupdated",this._editedSeriesUpdate,this);
            
                Ext.getCmp('chartgridcnt').add(grid);
            
                //Ext.getCmp('plotdatafrm').setVisible(false);
                        
                var style = {};
            
                // Set thin style for all
                for (var key in this.procedures) {
                    style[key] = {
                        strokeWidth: 0.5,
                        strokeBorderWidth: 0,
                        //pointSize: 1,
                        highlightCircleSize: 3,
                        drawPoints: false
                    };
                }
                // Set bold style for edited procedure
                style[sel] = {
                    strokeWidth: 1.5,
                    strokeBorderWidth: 1,
                    //pointSize: 3,
                    highlightCircleSize: 4,
                    drawPoints: false
                };
            
                this.chart.updateOptions(style);
                this.checkCalculator();
            
            } else if (btn.getText() == 'Apply changes') {
                
                var recs = proc.store.getRange();
                var fields = proc.storeFields;
                var values = [];
                for (var r = 0; r < recs.length; r++) {
                    var row = [];
                    for (var i = 0; i < fields.length; i++) {
                        // skip isodate microseconds are more accurate
                        //if (fields[i].name==wa.isodef) {
                        if (fields[i].name==proc.iso8601Field) {
                            continue;
                        }else if (fields[i].name=='micro') {
                            row.push(istsos.utils.micro2iso(recs[r].get(fields[i].name)));
                        }else{
                            row.push(""+(recs[r].get(fields[i].name)));
                        }
                    }
                    values.push(row);
                }
                
                proc.data.result.DataArray.values = values;
                proc.data.result.DataArray.elementCount = ""+values.length;
                
                proc.data.samplingTime.beginPosition = istsos.utils.micro2iso(recs[0].get('micro'));
                    
                proc.data.samplingTime.endPosition = istsos.utils.micro2iso(recs[recs.length-1].get('micro'));
                
                Ext.Ajax.request({
                    url: Ext.String.format('{0}/istsos/services/{1}/operations/insertobservation',wa.url,proc.service),
                    scope: this,
                    method: "POST",
                    jsonData: {
                        "AssignedSensorId" : proc.getId(),
                        "ForceInsert" : "true",
                        "Observation" : proc.data
                    },
                    success: function(response){
                        var json = Ext.decode(response.responseText);
                        if (json.success) {
                            Ext.getCmp('plotcalc').getLayout().setActiveItem(0);
                            Ext.getCmp("btnCancelEditor").setVisible(false);
                            Ext.getCmp('btnStartEditor').setText('Start editing');
                            Ext.getCmp('chartgridcnt').removeAll();
                            Ext.getCmp('btnStartEditor').enable();
                            Ext.getCmp("btnPlot").fireEvent("click");
                            delete this.grid;
                        }else{
                            
                        }
                    }
                });
            }
        },this);
            
            
        Ext.getCmp("btnRangeDay").on("click",function(btn, e, eOpts){
            // 86400000 ms = 1 day
            var range = this.chart.xAxisRange();
            var extreme = this.chart.xAxisExtremes();
            range[1] = range[0]+86400000000;
            if (extreme[1]<range[1]) {
                range[0] = extreme[1]-86400000000;
                range[1] = extreme[1];
            }
            btn.toggle(true,true);
            this.chart.updateOptions( {
                'dateWindow': [range[0], range[1]]
            } );
        },this);
        
        Ext.getCmp("btnRangeWeek").on("click",function(btn, e, eOpts){
            var range = this.chart.xAxisRange();
            var extreme = this.chart.xAxisExtremes();
            range[1] = range[0]+604800000000;
            if (extreme[1]<range[1]) {
                range[0] = extreme[1]-604800000000;
                range[1] = extreme[1];
            }
            btn.toggle(true,true);
            this.chart.updateOptions( {
                'dateWindow': [range[0], range[1]]
            } );
        },this);
        
        Ext.getCmp("btnRangeAll").on("click",function(btn, e, eOpts){
            btn.toggle(true,true);
            this.chart.updateOptions( {
                'dateWindow': this.chart.xAxisExtremes()
            } );
        },this);
        
    },
    _editedSeriesUpdate: function( store, records){
        var idx = store.indexOf(records[0]);
        var rec = [];
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        var procedure = this.procedures[store.name];
        var field = procedure.storeConvertFieldToId[obsprop];
        //var proc = Ext.getCmp("oeCbProcedure").getValue();
        var colIdx = this.chart.indexFromSetName(store.name);
        for (var c = 0, i = 0; i < this.chartdata.length && c < records.length ; i++) {
            if (this.chartdata[i][0]==records[c].get('micro')) {
                this.chartdata[i][colIdx]=records[c].get(field);
                //this.chartdata[i][colIdx]=records[c].get(obsprop);
                c++;
            }
        }
        this.chart.updateOptions({
            file: this.chartdata
        });
    },
    _editedRowUpdate: function( store, record){
        var idx = store.indexOf(record);
        var procedure = this.procedures[store.name];//
        var rec = [];
                
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        //var proc = Ext.getCmp("oeCbProcedure").getValue();
                
        var colIdx = this.chart.indexFromSetName(store.name);
                
        rec.push(record.get('micro'));
        
        // @todo sync NaN with istSOS configuration
        if (record.get(procedure.storeConvertFieldToId[obsprop])<-900) {
            rec.push(NaN);
        }else{
            rec.push(record.get(procedure.storeConvertFieldToId[obsprop]));
        }
        
        for (var i = 0; i < this.chartdata.length; i++) {
            if (this.chartdata[i][0]==rec[0]) {
                this.chartdata[i][colIdx]=rec[1];
                break;
            }
        }
        
        this.chart.updateOptions({
            file: this.chartdata
        });
        
    },
    addProcedure: function(proc){
        
        var ps = Ext.getStore("editableProcedure");
        
        
        // Append the procedure name in the store used by combos
        ps.loadData([{
            name: proc.getName()
        }],true);
        
        if (ps.data.length==1) {
            Ext.getCmp('oeCbEditableProcedures').setValue(ps.getAt(0));
        }
        
        this._configurePlotPanel();
        
        var cnt = Ext.getCmp('proceduresTree');
        
        // Adding details in the panel listing selected procedures
        var item = Ext.getCmp('proceduresTree').add(this._getProcedureDetails(proc));
        
        var func = "Ext.callback(Ext.getCmp(\""+this.id+"\").removeProcedure, Ext.getCmp(\""+this.id+"\"), [\""+item["title"]+"\"]);";
        Ext.create('Ext.tip.ToolTip', {
            target: item["id"],
            id: "tip-"+proc.getName(),
            anchor: 'right',
            html: "<div class='softLink' onclick='"+func+"'>remove</div>",
            style: {
                'background-color': 'white !important'
            },
            hideDelay: 1000
        });
        Ext.getCmp(item["id"]).on("expand",function(fs, o){
            var labels = this.chart.getLabels();
            var idx = Ext.Array.indexOf(labels,fs.title);
            if (idx>0) {
                this.chart.setVisibility(idx-1,true);
            }
        },this);
        Ext.getCmp(item["id"]).on("collapse",function(fs, o){
            var labels = this.chart.getLabels();
            var idx = Ext.Array.indexOf(labels,fs.title);
            if (idx>0) {
                this.chart.setVisibility(idx-1,false);
            }
        },this);
    },
    _getProcedureDetails: function(proc){
        return {
            xtype: 'fieldset',
            id: 'fs-'+proc.getName(),
            layout: {
                type: 'column'
            },
            padding: 10,
            collapsible: false,
            checkboxToggle: true,
            checkboxName: proc.getName(),
            title: proc.getName(),
            defaults: {
                labelWidth: 70,
                xtype: 'displayfield',
                anchor: '100%',
                columnWidth: 1
            },
            items: [
            {
                fieldLabel: 'From',
                value: proc.getBeginPosition()
            },
            {
                fieldLabel: 'To',
                value: proc.getEndPosition()
            },
            {
                fieldLabel: 'Observed',
                value: proc.getObservedProperties().join(", ")
            },
            {
                fieldLabel: 'Resolution',
                itemId: 'resolution',
                hidden: true,
                value: ""
            },
            {
                fieldLabel: 'Loaded',
                itemId: 'loaded',
                hidden: true,
                value: ""
            },
            {
                fieldLabel: 'Interpolate',
                itemId: 'interpolate',
                xtype: 'checkbox',
                hidden: true,
                value: false,
                listeners: {
                    change: function (field, newValue, oldValue, eOpts) {
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
    /**
     * For every procedure loaded, configure the panel plotter.
     */
    _configurePlotPanel: function(){
        // Analising max begin and end position, used to set 
        //  limits on datitime fields
        var begin, end, os = Ext.getStore('observedproperties');
        for (var key in this.procedures) {
            var meta = this.procedures[key].meta;
            for (var i = 0; i < meta.outputs.length; i++) {
                if (meta.outputs[i]["definition"]==this.procedures[key].isodef) {
                    if (!Ext.isEmpty(meta.outputs[i]['constraint']['interval'])) {
                        var interval = Ext.Array.clone(meta.outputs[i]['constraint']['interval']);
                        try{
                            interval[0] = Ext.Date.parse(interval[0],"c");
                            if (Ext.isEmpty(begin) || (Ext.isDate(begin) && begin>interval[0])) {
                                begin = Ext.Date.clone(interval[0]);
                            }
                        }catch (e){
                            console.error("Unable to parse allowed begin date interval");
                        }
                        try{
                            interval[1] = Ext.Date.parse(interval[1],"c");
                            if (Ext.isEmpty(end) || (Ext.isDate(end) && end<interval[1])) {
                                end = Ext.Date.clone(interval[1]);
                            }
                        }catch (e){
                            console.error("Unable to parse allowed end date interval");
                        }
                    }
                }else if (os.find('definition',meta.outputs[i]["definition"])==-1) {
                    var data = [[
                    meta.outputs[i]["name"],
                    meta.outputs[i]["description"],
                    meta.outputs[i]["uom"],
                    meta.outputs[i]["definition"]
                    ]];
                    os.loadData(data,true);
                }
            }
        }
        if (!Ext.isEmpty(begin)) {
            Ext.getCmp('oeBegin').setMinValue(begin); 
            Ext.getCmp('oeEnd').setMinValue(begin); 
        }
        if (!Ext.isEmpty(end)) {
            var endCopy = Ext.Date.clone(end);
            var beginCopy = Ext.Date.add(Ext.Date.clone(end), Ext.Date.DAY,-7);
            Ext.getCmp('oeBegin').setMaxValue(endCopy); 
            Ext.getCmp('oeEnd').setMaxValue(endCopy); 
            Ext.getCmp('oeBegin').setValue(beginCopy); 
            Ext.getCmp('oeEnd').setValue(end);
        }
        if (os.data.length==1) {
            Ext.getCmp('oeCbObservedProperty').setValue(os.getAt(0));
        }
        
        
        Ext.getCmp('oeCbObservedProperty').enable();
        Ext.getCmp("btnPlot").enable();
    },
    redrawProcedures: function(procedures){
        var items = [];
        var begin, end;
        var cbEdStr = Ext.getStore("editableProcedure");
        cbEdStr.removeAll();
        var obsprop = Ext.getStore('observedproperties');
        obsprop.removeAll();
        for (var key in this.procedures) {
            cbEdStr.loadData([{
                name: key
            }],true);
            var p = this.procedures[key];
            var d = p.description;      
            for (var i = 0; i < d.outputs.length; i++) {
                if (d.outputs[i]["definition"]==wa.isodef) {
                    if (!Ext.isEmpty(d.outputs[i]['constraint']['interval'])) {
                        var interval = Ext.Array.clone(d.outputs[i]['constraint']['interval']);
                        try{
                            interval[0] = Ext.Date.parse(interval[0],"c");
                            if (Ext.isEmpty(begin) || (Ext.isDate(begin) && begin>interval[0])) {
                                begin = Ext.Date.clone(interval[0]);
                            }
                        }catch (e){
                            console.error("Unable to parse allowed begin date interval");
                        }
                        try{
                            interval[1] = Ext.Date.parse(interval[1],"c");
                            if (Ext.isEmpty(end) || (Ext.isDate(end) && end<interval[1])) {
                                end = Ext.Date.clone(interval[1]);
                            }
                        }catch (e){
                            console.error("Unable to parse allowed end date interval");
                        }
                    }
                }else if (obsprop.find('definition',d.outputs[i]["definition"])==-1) {
                    var data = [[
                    d.outputs[i]["name"],
                    d.outputs[i]["description"],
                    d.outputs[i]["uom"],
                    d.outputs[i]["definition"]
                    ]];
                    obsprop.loadData(data,true);
                }
            }
            //console.log(begin,end);
            var b = d.outputs
            
            var node = p.getCheckbox();
            items.push(node);
        }
        if (!Ext.isEmpty(begin)) {
            Ext.getCmp('oeBegin').setMinValue(begin); 
            Ext.getCmp('oeEnd').setMinValue(begin); 
        }
        if (!Ext.isEmpty(end)) {
            var endCopy = Ext.Date.clone(end);
            var beginCopy = Ext.Date.add(Ext.Date.clone(end), Ext.Date.DAY,-7);
            Ext.getCmp('oeBegin').setMaxValue(endCopy); 
            Ext.getCmp('oeEnd').setMaxValue(endCopy); 
            Ext.getCmp('oeBegin').setValue(beginCopy); 
            Ext.getCmp('oeEnd').setValue(end);
        }
        Ext.getCmp('oeCbObservedProperty').enable();
        Ext.getCmp("btnPlot").enable();
        var cnt = Ext.getCmp('proceduresTree');
        cnt.removeAll();
        cnt.add(items);
        for (i = 0; i < items.length; i++) {
            var func = "Ext.callback(Ext.getCmp(\""+this.id+"\").removeProcedure, Ext.getCmp(\""+this.id+"\"), [\""+items[i]["title"]+"\"]);";
            Ext.create('Ext.tip.ToolTip', {
                target: items[i]["id"],
                id: "tip-"+items[i]["id"],
                anchor: 'right',
                html: "<div class='softLink' onclick='"+func+"'>remove</div>",
                style: {
                    'background-color': 'white !important'
                },
                hideDelay: 1000
            });
            Ext.getCmp(items[i]["id"]).on("expand",function(fs, o){
                var labels = this.chart.getLabels();
                var idx = Ext.Array.indexOf(labels,fs.title);
                if (idx>0) {
                    this.chart.setVisibility(idx-1,true);
                }
            },this);
            Ext.getCmp(items[i]["id"]).on("collapse",function(fs, o){
                var labels = this.chart.getLabels();
                var idx = Ext.Array.indexOf(labels,fs.title);
                if (idx>0) {
                    this.chart.setVisibility(idx-1,false);
                }
            },this);
        }
        Ext.QuickTips.init();
    },
    removeProcedure: function(procedure){
        Ext.getCmp("tip-"+this.procedures[procedure].getName()).setVisible(false);
        Ext.QuickTips.unregister("tip-"+this.procedures[procedure].getName());
        Ext.getCmp('proceduresTree').remove('fs-'+this.procedures[procedure].getName());
        delete this.procedures[procedure];
        this._initChartStore(false);
    },
    _initChartStore: function(initChart){
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        var procs = [];
        // get the json rapresentation of the tree menu of procedures
        var checked = Ext.getCmp('proceduresTree').getValues();
        var visibility = []; // Initialize the chart series visibility
        
        this.labels = ["isodate"];
        var template = [];
        
        this.chartStore = {};
        
        var valueFormatter = {
            
        }
        var cc = 1;
        for (var key in this.procedures) {
            // check if procedures loaded have the requested observed property
            if (Ext.Array.contains(this.procedures[key].getObservedProperties(),obsprop)) {
                procs.push(this.procedures[key]);
                if (!Ext.isEmpty(checked[key])) { // if the checkbox is selected
                    visibility.push(true);
                }else{
                    visibility.push(false);
                }
                // Preparing labels and single native row template
                template.push(null);
                this.labels.push(key);
                
                valueFormatter[cc == 1 ? 'y': 'y'+cc] = {
                    valueFormatter: function(ms, fn, p) {
                        return ' '+ ms + ' '+ Ext.getCmp('chartpanel').procedures[p].getUomCode(
                            Ext.getCmp("oeCbObservedProperty").getValue()    
                            );
                    }
                } 
                
            }
        }
        // merging data
        var idx = 0;
        for (var key in procs) {
            
            var p = procs[key];
            var recs = p.store.getRange();
            
            for (var j = 0, l = recs.length; j < l; j++) {
                
                if (Ext.isEmpty(this.chartStore[ recs[j].get("micro") ])) {
                    this.chartStore[recs[j].get("micro")] = Ext.Array.clone(template);
                }
                // Set the property choosen in the chart store in the right column
                
                var v = parseFloat(recs[j].get(p.storeConvertFieldToId[obsprop]));
                if (v<-900) {
                    this.chartStore[recs[j].get("micro")][idx] = NaN;  
                }else{
                    this.chartStore[recs[j].get("micro")][idx] = v;          
                }
            }
            idx++;
        }
        
        // Sorting array by dates
        var sorted = Ext.Array.sort(Ext.Object.getKeys(this.chartStore), 
            function (d1, d2) {
                d1 = parseInt(d1);
                d2 = parseInt(d2);
                if (d1 > d2) return 1;
                if (d1 < d2) return -1;
                return 0;
            });
        this.chartdata = [];
        for (var i = 0; i < sorted.length; i++) {
            var rec = [];
            rec.push(parseInt(sorted[i]));
            var vals = this.chartStore[sorted[i]];
            rec = rec.concat(vals);
            this.chartdata.push(rec);
        }
        initChart = true;
        if (initChart) {
            Ext.getCmp("btnRangeDay").toggle(false,true);
            Ext.getCmp("btnRangeWeek").toggle(false,true);
            Ext.getCmp("btnRangeAll").toggle(true,true);
            this.chart = new Dygraph(
                document.getElementById("chartCnt"),
                this.chartdata,
                {
                    labels: this.labels,
                    digitsAfterDecimal: 6,
                    visibility: visibility,
                    legend: 'always',
                    title: this.obsprop,
                    showRangeSelector: true,
                    showRoller: true,
                    rangeSelectorHeight: 30,
                    rangeSelectorPlotStrokeColor: 'black',
                    rangeSelectorPlotFillColor: 'green',
                    //
                    // drawGapEdgePoints: Draw points at the edges of gaps in the data. 
                    // This improves visibility of small data segments or 
                    // other data irregularities.
                    
                    //connectSeparatedPoints: true,
                    //drawGapEdgePoints: true,
                    labelsDivStyles: {
                        'padding': '4px',
                        'border': '1px solid black',
                        'borderRadius': '3px',
                        'boxShadow': '4px 4px 4px #888',
                        'right': '10px'
                    },
                    labelsDivWidth: "100%",
                    axes: Ext.apply({
                        /*y: {
                            valueFormatter: function(ms) {
                                console.log("ciao");
                                return 'fica';
                            }
                        },*/
                        x: {
                            valueFormatter: function(ms) {
                                return istsos.utils.micro2iso(ms);
                            },
                            axisLabelFormatter: function(ms, gran, b, chart){
                        
                                // Get unix time in seconds
                                var unix = parseInt(ms/1000000);
                                // Extract microseconds only
                                var micro = ms-(unix*1000000);
                                // Date object without considering microseconds
                                var date = Ext.Date.parse(unix,'U');
                        
                                var range = chart.xAxisRange();
                                var delta = range[1]-range[0];
                                   
                                var clip = function(m){
                                    return (parseFloat('0.'+m)+"").substring(1);
                                }
                                if (delta<500000) { // less then a seconds range
                                    //chart.updateOptions({axes: {x: {pixelsPerLabel: 50}}})
                                    if (micro == 0) {
                                        if (date.getHours()==0 
                                            && date.getMinutes()==0  
                                            && date.getSeconds()==0) {
                                            return Ext.Date.format(date,'Y-m-d');
                                        }else{
                                            return Ext.Date.format(date,'H:i:s')+clip(micro);
                                        }
                                    }else{
                                        if (micro==200000 || micro==400000 || micro==600000 || micro==800000) {
                                            return Ext.Date.format(date,'H:i:s')+clip(micro);
                                        }else{
                                            return micro/1000;
                                        }
                                    }
                                }else if (delta<1000000) { // less then a seconds range
                                    //chart.updateOptions({axes: {x: {pixelsPerLabel: 50}}})
                                    if (micro == 0) {
                                        if (date.getHours()==0 
                                            && date.getMinutes()==0  
                                            && date.getSeconds()==0) {
                                            return Ext.Date.format(date,'Y-m-d');
                                        }else{
                                            return Ext.Date.format(date,'H:i:s')+clip(micro);
                                        }
                                    }else{
                                        if (micro==500000) {
                                            return Ext.Date.format(date,'H:i:s')+clip(micro);
                                        }else{
                                            return micro/1000;
                                        }
                                    }
                                }else if(delta<1000000*60) { // less the a minute
                                    //chart.updateOptions({axes: {x: {pixelsPerLabel: 80}}})
                                    if (date.getHours()==0 
                                        && date.getMinutes()==0  
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d');
                                    }else{
                                        return Ext.Date.format(date,'H:i:s')+clip(micro);
                                    }
                                }else if(delta<1000000*60*60) { // less the an hour
                                    //chart.updateOptions({axes: {x: {pixelsPerLabel: 100}}})
                                    if (date.getHours()==0 
                                        && date.getMinutes()==0  
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d');
                                    }else{
                                        return Ext.Date.format(date,'H:i');
                                    }
                                }else if(delta<1000000*60*60*24) { // less the a day
                                    //chart.updateOptions({axes: {x: {pixelsPerLabel: 120}}})
                                    if (date.getHours()==0 
                                        && date.getMinutes()==0  
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d');
                                    }else if (date.getHours()==12 
                                        && date.getMinutes()==0  
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d') + "T" +
                                        Ext.Date.format(date,'H:i');
                                    }else{
                                        return Ext.Date.format(date,'H:i');
                                    }
                                }else if(delta<1000000*60*60*24*4) { // less the a day
                                    //chart.updateOptions({axes: {x: {pixelsPerLabel: 120}}})
                                    if (date.getHours()==0 
                                        && date.getMinutes()==0  
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d');
                                    }else if (date.getHours()==12) {
                                        return Ext.Date.format(date,'Y-m-d') + "<br>" +
                                        Ext.Date.format(date,'H:i');
                                    }else{
                                        return Ext.Date.format(date,'H:i');
                                    }
                                }else  { // less the a day
                                    return Ext.Date.format(date,'Y-m-d');
                                }
                        
                            }
                        }
                    },valueFormatter),
                    axisLineColor: 'green',
                    axisLabelFontSize: 12,
                    axisLabelWidth: 150,
                    xAxisLabelWidth: 150,
                    /*xAxisHeight: 80,
                    xLabelHeight: 80,*/
                    //xAxisLabelFormatter: ,
                    clickCallback: function(e, x, pts) {
                        var chartpanel = Ext.getCmp('chartpanel');
                        Ext.callback(chartpanel.clickCallback, chartpanel, [e, x, pts]);
                        Ext.callback(chartpanel.updateGridSelection, chartpanel, [chartpanel.chart.annotations()]);
                    },
                    pointClickCallback: function(e, p) {
                        var chartpanel = Ext.getCmp('chartpanel');
                        Ext.callback(chartpanel.pointClickCallback, chartpanel, [e, p]);
                        Ext.callback(chartpanel.updateGridSelection, chartpanel, [chartpanel.chart.annotations()]);
                    },
                    underlayCallback: function(canvas, area, g) {
                        var chartpanel = Ext.getCmp('chartpanel');
                        Ext.callback(chartpanel.highlight_period, chartpanel, [canvas, area, g]);
                    }
                }
                );
        }else if (!Ext.isEmpty(this.chart)) {
            this.chart.updateOptions({
                file: this.chartdata,
                visibility: visibility,
                labels: this.labels
            });
        }
        
    },
    /**
     * Create a grid that fit the internal store
     */
    _getGrid: function(procedureName){
        
        var procedure = this.procedures[procedureName];
        var properties = procedure.data.result.DataArray.field;
        
        var columns = [{
            xtype: 'numbercolumn',
            dataIndex: 'micro',
            hidden: true,
            hideable: false,
            header: 'id'
        },{
            xtype: 'gridcolumn',
            dataIndex: procedure.iso8601Field, // isodate is always present at position one
            flex: 0.7,
            header: 'Date'
        }];
        
        for (var i = 1; i < properties.length; i++) {
            
            columns.push({
                xtype: 'numbercolumn',
                format: "0'000.000000",
                dataIndex: procedure.storeConvertFieldToId[properties[i].definition],
                definition: properties[i].definition,
                //dataIndex: properties[i].definition,
                flex: 0.4,
                text: properties[i].name,
                field: {
                    xtype: 'numberfield',
                    decimalPrecision: 6,
                    hideLabel: true,
                    listeners: {
                        change: function(form, newValue, oldValue, eOpts){
                            //console.log("change: ");
                            //console.dir(arguments);
                        }
                    }
                }
            },{
                xtype: 'gridcolumn',
                dataIndex: procedure.storeConvertFieldToId[properties[i].definition+':qualityIndex'],
                definition: Ext.String.format('{0}:qualityIndex',properties[i].definition),
                //dataIndex: Ext.String.format('{0}:qualityIndex',properties[i].definition),
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
        
        var observedProperty = Ext.getCmp("oeCbObservedProperty").getValue();
        for (var i = 1; i < columns.length; i++) {
            if (columns[i]['definition']==wa.isodef && 
                columns[i]['definition']!=observedProperty && 
                columns[i]['definition']!=observedProperty+':qualityIndex') {
                columns[i]['hidden']=true;
            }
        }
        
        this.grid = Ext.create('Ext.grid.Panel', {
            xtype: 'grid',
            //id: 'oegrid',
            title: '',
            store: this.procedures[procedureName].store,
            autoRender: true,
            autoScroll: true,
            viewConfig: {
            
            },
            columns: columns,
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
                    emptyText: 'Load CSV..',
                    labelWidth: 40/*,
                    listeners: {
                        change: this.loadCsv,
                        scope: this
                    }*/
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
    // Initializing store for each visible procedure 
    //   if they have the requested observed property
    initProcedureStore: function(obsColl){
        this.obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        var checked = Ext.getCmp('proceduresTree').getValues(); // Check checkbox from left menu
        for (var key in this.procedures) {
            var p = this.procedures[key];
            var d = p.description;
            for (var i = 0; i < obsColl.length; i++) {
                if (obsColl[i].name==key) {
                    p.initStore(obsColl[i]);
                    Ext.Array.remove(this.loadingQueue[p.service],p.description.system_id);
                    if (this.loadingQueue[p.service].length==0) {
                        delete this.loadingQueue[p.service];
                    }
                    if (Ext.Object.getKeys(this.loadingQueue[p.service]).length==0) {
                        this.fireEvent("queueLoaded",true);
                    }
                    break;
                }
            }
        }
    },
    /*_chartobservationsUpdate: function(store, record, operation, eOpts){
        
        var idx = store.indexOf(record);
            
        var rec = [];
        rec.push(record.get(store.idProperty));
        rec.push(record.get(this.obsprop));
            
        this.chartdata[idx]=rec;
        this.chart.updateOptions({
            file: this.chartdata
        });
    },*/
    clickCallback: function(e, x, pts){
        //console.log("clickCallback", arguments);
        var grid = this.grid;
        if (!Ext.isEmpty(grid)) {
            var series = Ext.getCmp('oeCbEditableProcedures').getValue();
            for (var i = 0; i < pts.length; i++) {
                if (pts[i]['name']==series) {
                    this.pointClickCallback(e, pts[i]);
                    return;
                }
            }
        }
    },
    pointClickCallback: function(e, p, disableGridSelection){
        //console.log("pointClickCallback", arguments);
        
        var series = Ext.getCmp('oeCbEditableProcedures').getValue();
        var annotations;
        var a = {
            series: series,
            x: p['xval'],
            shortText: '\\/',
            text: 'long test',
            tickHeight: 10
        };
        if (e.shiftKey) {
            annotations = this.chart.annotations();
            if (annotations.length==2) {
                if (annotations[0]['x'] > p['xval']) {
                    //annotations[1] = annotations[0];
                    annotations[0] = a;
                }else{
                    annotations[1] = a;
                }
                annotations[0].shortText = ">";
                annotations[1].shortText = "<";
            }else if (annotations.length==1) {
                if (annotations[0]['x'] > p['xval']) {
                    annotations.push(annotations[0]);
                    annotations[0] = a;
                }else{
                    annotations.push(a);
                }
                annotations[0].shortText = ">";
                annotations[1].shortText = "<";
            }else{
                annotations.push(a);
            }
        }else{
            annotations = [];
            annotations.push(a);
        }
        this.chart.setAnnotations(annotations);
        
        if (annotations.length==2) {
            this.fireEvent("seriesSelected", annotations);
        }
        this.checkCalculator();
        
    },
    updateGridSelection: function(annotations){
        var grid = this.grid;
        if (!Ext.isEmpty(grid)) {
            var selectionModel = grid.getSelectionModel(), store = grid.getStore();
            if (annotations.length==2) {
                // Get first annotation time
                /*var d1 = Ext.Date.parse(annotations[0].x/1000, "U");
                var d2 = Ext.Date.parse(annotations[1].x/1000, "U");
                var idx1 = store.find(wa.isodef,d1);
                var idx2 = store.find(wa.isodef,d2);*/
                
                var idx1 = store.find('micro',annotations[0].x);
                var idx2 = store.find('micro',annotations[1].x);
                
                selectionModel.selectRange(idx1,idx2);
                
            }else if (annotations.length==1) {
                
                var d1 = annotations[0].x;
                var idx1 = store.find('micro',annotations[0].x);
                selectionModel.select(idx1);
                
            // Get first annotation time
            /*var d1 = Ext.Date.parse(annotations[0].x/1000, "U");
                var idx1 = store.find(wa.isodef,d1);
                selectionModel.select(idx1);*/
            }
        }
    },
    checkCalculator: function(){
        var grid = this.grid;
        if (!Ext.isEmpty(grid)) {
            
            var sel = Ext.getCmp('oeCbEditableProcedures').getValue();
            var proc = this.procedures[sel];
            
            Ext.getCmp('pEditing').setValue(Ext.getCmp('oeCbEditableProcedures').getValue()+" = ");
            
            Ext.getStore("calcQiStore").load({
                url: Ext.String.format('{0}/istsos/services/{1}/dataqualities',wa.url,proc.service)
            });
            
            Ext.getCmp('plotcalc').getLayout().setActiveItem(1);
            
            Ext.getCmp('calcpanel').code.editor.focus();  
            /*
            var annotations = this.chart.annotations();
            if (annotations.length==2) {
                Ext.getCmp('plotcalc').getLayout().getActiveItem(1).enable();
            }else if (annotations.length<2) {
                Ext.getCmp('plotcalc').getLayout().getActiveItem(1).disable();
            }*/
        }else{
            Ext.getCmp('plotcalc').getLayout().setActiveItem(0);
        }
    },  
    highlight_period: function(canvas, area, g) {
        if (this.chart) {
            var annotations = this.chart.annotations();
            if (annotations.length==2) {
                canvas.fillStyle = "rgba(194, 232, 184, 0.8)";
                var canvas_left_x = g.toDomXCoord(annotations[0].x);
                var canvas_right_x = g.toDomXCoord(annotations[1].x);
                var canvas_width = canvas_right_x - canvas_left_x;
                canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);
            }
        }
    }
});