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

Ext.define('istsos.view.ProcedureChart', {
    extend: 'istsos.view.ui.ProcedureChart',
    alias: 'widget.procedurechart',

    initComponent: function() {
        var me = this;

        Ext.create('istsos.store.ObservedProperties');
        Ext.create('istsos.store.AggregateFunctionStore').loadData([
            ['AVG'],['SUM'],['COUNT'],['MAX'],['MIN']
        ]);
        this.procedures = {};

        me.callParent(arguments);

        this.addEvents('queueLoaded','observedPropertyIsSet','clickCallback','pointClickCallback', 'seriesSelected', 'underlayCallback');

        //var offset = (new Date()).getTimezoneOffset()/-60;

        //var tz = (parseInt(offset)>=0?'+':'-') + this.pad(parseInt(offset)) + ':' + this.pad(Math.abs(((offset - parseInt(offset)) * 60 )));

        //var tz = ((offset > 0) ? "+"+this.pad(offset) : this.pad(offset));
        //Ext.getCmp('oeBeginTime').format = 'H:i ['+tz+']';

        Ext.getCmp('oeTZ').setValue(istsos.utils.minutesToTz());

        Ext.getCmp('oeBeginTime').setValue(Ext.Date.parse("00:00", 'H:i'));
        //Ext.getCmp('oeEndTime').format = 'H:i ['+tz+']';
        Ext.getCmp('oeEndTime').setValue(Ext.Date.parse("00:00", 'H:i'));

        Ext.getCmp("btnPlot").on("click",this.loadObservation, this);
        this.on("queueLoaded",this.rederChart, this);

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
            this.chart.updateOptions({
                'dateWindow': [range[0], range[1]]
            });
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


        this.on("resize",function(panel, adjWidth, adjHeight, eOpts){
            if(this.chart){
                this.chart.resize();
            }
        });

        Ext.getCmp('oeCbObservedProperty').on("select",function(combo, records, eOpts){
            var op = null;
            if (records.length==1) {
                op = records[0].data;
            }
            this.fireEvent("observedPropertyIsSet", this, op);
        },this);

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
    rederChart: function(){

        this.obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        var procs = [];
        // get the json rapresentation of the tree menu of procedures
        //var checked = Ext.getCmp('proceduresTree').getValues();
        var visibility = []; // Initialize the chart series visibility

        this.labels = ["isodate"];
        this.colors = [];
        var template = [];

        this.chartStore = {};

        var valueFormatter = {

        }
        var cc = 1;

        var keys = Object.keys(this.procedures);
        keys = keys.sort();

        //for (var key in this.procedures) {
        for (var c = 0; c < keys.length; c++) {
            var key = keys[c];
            // check if procedures loaded have the requested observed property
            if (Ext.Array.contains(this.procedures[key].getObservedProperties(),this.obsprop)) {
                procs.push(this.procedures[key]);
                // Preparing labels and single native row template
                template.push(null);
                this.labels.push(key);
                this.colors.push(this.procedures[key].color);
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
        //for (var key in procs) {
        for (var c = 0; c < procs.length; c++) {
            var p = procs[c];

            p.store.on("update",this._storeUpdated,this);
            p.store.on("seriesupdated",this._storeSeriesUpdated,this);

            var recs = p.store.getRange();
            for (var j = 0, l = recs.length; j < l; j++) {
                if (Ext.isEmpty(this.chartStore[recs[j].get("micro") ])) {
                    this.chartStore[recs[j].get("micro")] = Ext.Array.clone(template);
                }
                // Set the property choosen in the chart store in the right column
                var v = parseFloat(recs[j].get(p.storeConvertFieldToId[this.obsprop]));
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
        var initChart = true;
        if (initChart) {
            Ext.getCmp("btnRangeDay").toggle(false,true);
            Ext.getCmp("btnRangeWeek").toggle(false,true);
            Ext.getCmp("btnRangeAll").toggle(true,true);
            this.chart = new Dygraph(
                document.getElementById("chartCnt-body"),
                this.chartdata,
                {
                    labels: this.labels,
                    colors: this.colors,
                    strokeWidth: 2,
                    digitsAfterDecimal: 6,
                    connectSeparatedPoints: true,
                    //visibility: visibility,
                    legend: 'always',
                    title: this.obsprop,
                    showRangeSelector: true,
                    showRoller: true,
                    rangeSelectorHeight: 30,
                    rangeSelectorPlotStrokeColor: 'black',
                    rangeSelectorPlotFillColor: 'green',
                    labelsDivStyles: {
                        'padding': '4px',
                        'border': '1px solid black',
                        'borderRadius': '3px',
                        'boxShadow': '4px 4px 4px #888',
                        'right': '10px'
                    },
                    labelsDivWidth: "100%",
                    axisLineColor: 'green',
                    axisLabelFontSize: 12,
                    axisLabelWidth: 150,
                    xAxisLabelWidth: 150,
                    highlightCircleSize: 4,
                    axes: Ext.apply({
                        x: {
                            valueFormatter: function(ms) {
                                return istsos.utils.micro2iso(ms,istsos.utils.tzToMinutes(Ext.getCmp('oeTZ').getValue()));
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
                                    if (date.getHours()==0
                                        && date.getMinutes()==0
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d');
                                    }else{
                                        return Ext.Date.format(date,'H:i:s')+clip(micro);
                                    }
                                }else if(delta<1000000*60*60) { // less the an hour
                                    if (date.getHours()==0
                                        && date.getMinutes()==0
                                        && date.getSeconds()==0) {
                                        return Ext.Date.format(date,'Y-m-d');
                                    }else{
                                        return Ext.Date.format(date,'H:i');
                                    }
                                }else if(delta<1000000*60*60*24) { // less the a day
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
                    clickCallback: function(e, x, pts) {
                        var chartpanel = Ext.getCmp('chartpanel');
                        // Series selectd
                        if (e.shiftKey && chartpanel.lastClick) {
                            Ext.callback(function(e, x, pts){
                                this.fireEvent("seriesSelected", this, e, x, this.lastClick, pts);
                            }, chartpanel, [e, x, pts]);

                        }else{ // Single point selected
                            chartpanel.lastClick = x;
                            Ext.callback(function(e, x, pts){
                                this.fireEvent("clickCallback", this, e, x, pts);
                            }, chartpanel, [e, x, pts]);
                        }

                    },
                    pointClickCallback: function(e, p) {



                        var chartpanel = Ext.getCmp('chartpanel');
                        Ext.callback(function(e, p){
                            this.fireEvent("clickCallback", this, e, p['xval']);
                        }, chartpanel, [e, p]);
                    },
                    underlayCallback: function(canvas, area, g) {
                        var chartpanel = Ext.getCmp('chartpanel');
                        Ext.callback(function(canvas, area, g){
                            this.fireEvent("underlayCallback", this, canvas, area, g);
                        }, chartpanel, [canvas, area, g]);
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
        Ext.get('chartCnt-body').removeCls("viewerChart");
        Ext.get('chartCnt').unmask();
    },
    highlightRegion: function(startMicro, endMicro){
        if (this.chart) {
            if (startMicro==null && endMicro==null) {
                this.chart.updateOptions({
                    "underlayCallback": function(canvas, area, chart) {

                    }
                });
            }else if (endMicro==null) {
                this.chart.updateOptions({
                    "underlayCallback": function(canvas, area, chart) {
                        //canvas.fillStyle = "rgba(194, 232, 184, 1)";
                        canvas.fillStyle = "rgba(0, 255, 0, 0.8)";
                        var canvas_left_x = chart.toDomXCoord(startMicro)-1;
                        var canvas_width = 3;
                        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);

                        // Border left
                        canvas.fillStyle = "rgba(0, 0, 0, 1)";
                        canvas_left_x = chart.toDomXCoord(startMicro)-2;
                        canvas_width = 1;
                        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);

                        // Border right
                        canvas_left_x = chart.toDomXCoord(startMicro)+2;
                        canvas_width = 1;
                        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);
                    }
                });
            }else{
                this.chart.updateOptions({
                    "underlayCallback": function(canvas, area, chart) {
                        //canvas.fillStyle = "rgba(194, 232, 184, 1)";
                        canvas.fillStyle = "rgba(0, 255, 0, 1)";
                        var canvas_left_x = chart.toDomXCoord(startMicro);
                        var canvas_right_x = chart.toDomXCoord(endMicro);
                        var canvas_width = canvas_right_x - canvas_left_x;
                        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);


                        // Border left
                        canvas.fillStyle = "rgba(0, 0, 0, 1)";
                        canvas_left_x = chart.toDomXCoord(startMicro);
                        canvas_width = 1;
                        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);

                        // Border right
                        canvas_left_x = chart.toDomXCoord(endMicro)-1;
                        canvas_width = 1;
                        canvas.fillRect(canvas_left_x, area.y, canvas_width, area.h);
                    }
                });
            }
        }
    },
    addAnnotation: function(micro, annotation){
        var series = Ext.getCmp('oeCbEditableProcedures').getValue();
        var annotations = this.chart.annotations();
        var a = {
            series: series,
            x: micro,
            shortText: '\\/',
            text: 'long test',
            tickHeight: 10
        };
        if (!Ext.isEmpty(annotation)) {
            Ext.apply(a,{
                shortText: annotation
            });
        }
        annotations.push(a);
        this.chart.setAnnotations(annotations);
    },
    /*
     * Remove all annotatione from the chart
     */
    removeAnnotations: function(){
        this.chart.setAnnotations([]);
    },
    /*
     * Load the observation for added procedures according to user configuration:
     *  - begin / end
     *  - observed property
     */
    loadObservation: function(){

        // validation

        if(!Ext.getCmp('plotdatafrm').form.isValid()){
            Ext.Msg.show({
                 title:'Warning',
                 msg: 'Request parameters are not valid please check date ranges and observed properties',
                 buttons: Ext.Msg.OK,
                 icon: Ext.Msg.WARNING
            });
            return;
        }

        // Mask the container with loading message
        Ext.get('chartCnt').mask("Initializing chart..");

        var begin = Ext.getCmp('oeBegin').getValue();
        var bt = Ext.getCmp('oeBeginTime').getValue();
        begin.setHours(bt.getHours());
        begin.setMinutes(bt.getMinutes());

        var end = Ext.getCmp('oeEnd').getValue();
        var et = Ext.getCmp('oeEndTime').getValue();
        end.setHours(et.getHours());
        end.setMinutes(et.getMinutes());

        this.tz = Ext.getCmp('oeTZ').getValue();

        // Load data based on the date-time fields
        this.loading = [];
        for (var key in this.procedures) {
            this.loading.push(key);
            this.procedures[key].on("observationLoaded",function(p){
                Ext.Array.remove(this.loading,p.getName());
                if (this.loading.length==0) {
                    this.fireEvent("queueLoaded",this);
                }
            },this,{
                single: true
            });
            this.procedures[key].getObservation(begin,end,
                this.tz, // Setted timezoe
                (Ext.isObject(this.procedures[key].aggregation)?this.procedures[key].aggregation:null) // Aggregation configuration
            );
        }
    },
    _colorChanged: function(p, newColor, oldColor){
        if (this.chart) {
            var colors = this.chart.getColors();
            var labels = this.chart.getLabels();
            var index = Ext.Array.indexOf(labels, p.getName());
            colors[index-1] = newColor;
            this.chart.updateOptions( {
                'colors': colors
            });
        }
    },
    _visibilityChanged: function(p, visibile){
        if (this.chart) {
            var labels = this.chart.getLabels();
            var index = Ext.Array.indexOf(labels, p.getName())-1;
            this.chart.setVisibility(index,visibile);
        }
    },
    _storeUpdated: function( store, record){
        var procedure = this.procedures[store.name];
        var rec = [];
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
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
    _storeSeriesUpdated: function( store, records){
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        var procedure = this.procedures[store.name];
        var field = procedure.storeConvertFieldToId[obsprop];
        var colIdx = this.chart.indexFromSetName(store.name);
        for (var c = 0, i = 0; i < this.chartdata.length && c < records.length ; i++) {
            if (this.chartdata[i][0]==records[c].get('micro')) {
                this.chartdata[i][colIdx]=records[c].get(field);
                c++;
            }
        }
        this.chart.updateOptions({
            file: this.chartdata
        });
    },
    /*
    * Configure the plot panel loading the observed properties into the combo
    * and setting begin e end limits according to the procedures metadata.
    */
    addProcedure: function(procedure){
        this.procedures[procedure.getName()] = procedure;
        procedure.on("colorchanged",this._colorChanged,this);
        procedure.on("visibilitychanged",this._visibilityChanged,this);
        this.reconfigure();
    },
    removeProcedure: function(procedure){
        procedure.un("colorchanged",this._colorChanged,this);
        delete this.procedures[procedure.getName()];
        this.reconfigure();
        if (this.chart) {
            if (Ext.Object.getSize(this.procedures)==0) {
                Ext.destroy(Ext.get('chartCnt-body').child('*'));
                Ext.get('chartCnt-body').addCls("viewerChart");
                delete this.chart;
            }else{
                this.rederChart();
            }
        }
    },
    reconfigure: function(){
        var oeBegin = Ext.getCmp('oeBegin'),
        oeEnd = Ext.getCmp('oeEnd'),
        os = Ext.getStore('observedproperties');
        os.removeAll();
        oeBegin.setMaxValue(null);
        oeBegin.setMinValue(null);
        oeEnd.setMaxValue(null);
        oeEnd.setMinValue(null);
        if (Ext.Object.getSize(this.procedures)==0) {
            Ext.getCmp('oeCbObservedProperty').reset();
            Ext.getCmp("btnPlot").disable();
            oeBegin.reset();
            oeEnd.reset();
            return;
        }

        for (var key in this.procedures) {
            var procedure = this.procedures[key], begin, end;

            var meta = procedure.meta;
            for (var i = 0; i < meta.outputs.length; i++) {
                if (meta.outputs[i]["definition"]==procedure.isodef) {
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
            if (!Ext.isEmpty(begin)) {
                if (!Ext.isEmpty(oeBegin.minValue)) {
                    if (oeBegin.minValue.getTime()>begin.getTime()) {
                        oeBegin.setMinValue(begin);
                        oeEnd.setMinValue(begin);
                    }
                }else{
                    oeBegin.setMinValue(begin);
                    oeEnd.setMinValue(begin);
                }
            }


            if (!Ext.isEmpty(end)) {

                var endCopy = Ext.Date.add(Ext.Date.clone(end), Ext.Date.DAY, +1); //Ext.Date.clone(end);
                var beginCopy = Ext.Date.add(Ext.Date.clone(end), Ext.Date.DAY, -7);
                if(beginCopy<begin){
                  beginCopy = Ext.Date.clone(begin);
                }

                if (!Ext.isEmpty(oeBegin.maxValue)) {
                    if (oeBegin.maxValue.getTime()<end.getTime()) {
                        oeBegin.setMaxValue(endCopy);
                        oeEnd.setMaxValue(endCopy);
                        oeBegin.setValue(beginCopy);
                        oeEnd.setValue(endCopy);//end);
                    }
                }else{
                    oeBegin.setMaxValue(endCopy);
                    oeEnd.setMaxValue(endCopy);
                    oeBegin.setValue(beginCopy);
                    oeEnd.setValue(endCopy);
                }

            }
        }
        if (os.data.length==1) {
            Ext.getCmp('oeCbObservedProperty').setValue(os.getAt(0));
            this.fireEvent("observedPropertyIsSet", this, os.getAt(0).data);
        }
        //Ext.getCmp('oeCbObservedProperty').enable();
        Ext.getCmp("btnPlot").enable();
    }
});
