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


/*
 * https://github.com/sterlingwes/RandomColor
 */
(function(root,factory){
    if(typeof exports==='object'){
        module.exports=factory;
    }else if(typeof define==='function'&&define.amd){
        define(factory);
    }else{
        root.RColor=factory();
    }
}(this,function(){
    var RColor=function(){
        this.hue=Math.random(),this.goldenRatio=0.618033988749895;
    };
    RColor.prototype.hsvToRgb=function(h,s,v){
        var h_i=Math.floor(h*6),f=h*6- h_i,p=v*(1-s),q=v*(1-f*s),t=v*(1-(1-f)*s),r=255,g=255,b=255;
        switch(h_i){
            case 0:
                r=v,g=t,b=p;
                break;
            case 1:
                r=q,g=v,b=p;
                break;
            case 2:
                r=p,g=v,b=t;
                break;
            case 3:
                r=p,g=q,b=v;
                break;
            case 4:
                r=t,g=p,b=v;
                break;
            case 5:
                r=v,g=p,b=q;
                break;
        }
        return[Math.floor(r*256),Math.floor(g*256),Math.floor(b*256)];
    };
    RColor.prototype.get=function(hex,saturation,value){
        this.hue+=this.goldenRatio;
        this.hue%=1;
        if(typeof saturation!=="number")saturation=0.5;
        if(typeof value!=="number")value=0.95;
        var rgb=this.hsvToRgb(this.hue,saturation,value);
        if(hex)
            return"#"+rgb[0].toString(16)+rgb[1].toString(16)+rgb[2].toString(16);else
            return rgb;
    };
    return RColor;
}));

Ext.define('istsos.view.ProcedureChooser', {
    extend: 'istsos.view.ui.ProcedureChooser',
    alias: 'widget.procedurechooser',

    initComponent: function() {

        var me = this;
        this.color = new RColor;

        this.addEvents({
            "procedureAdded" : true,
            "procedureRemoved" : true,
            "serviceSelected" : true,
            "offeringSelected" : true,
            "procedureSelected" : true
        });

        Ext.create('istsos.store.Offerings');
        Ext.create('istsos.store.gridProceduresList');
        var ssrv = Ext.create('istsos.store.Services');
        ssrv.getProxy().url = Ext.String.format('{0}/istsos/services',wa.url);

        this.procedures = {};
        this.configsections = {};

        me.callParent(arguments);

        Ext.getCmp("wResetObservedProperties").on("click", function(){
          this._offeringSelected(Ext.getCmp('oeCbOffering'));
        },this);

        Ext.getCmp("cmbServices").on("select",this._serviceSelected,this);

        Ext.getCmp("oeCbOffering").on("select",this._offeringSelected,this);

        Ext.getCmp("oeCbProcedure").on("select",function(combo, records, eOpts){
          this.fireEvent("procedureSelected", combo.getValue());
        },this);

        Ext.getCmp("btnAdd").on("click",function(btn, e, eOpts){
            this._addProcedure(
              Ext.getCmp("cmbServices").getValue(),
              Ext.getCmp("oeCbOffering").getValue(),
              Ext.getCmp("oeCbProcedure").getValue()
            );
        },this);
    },
    _addProcedure: function(service, offering, procedure){
      // Add an istsos.Procedure in the this.procedures array
      // every row contains some describeSensor data
      this.procedures[procedure] = Ext.create('istsos.Sensor',
        service, offering, procedure, {
            listeners: {
                metadataLoaded: this._getProcedureDetails,
                scope: this
            }
        });
    },
    _getProcedureDetails: function(proc){
        var obsprop = [];
        for (var i = 0; i < proc.meta.outputs.length; i++) {
            if (proc.meta.outputs[i]['definition']!=proc.isodef) {
                obsprop.push(proc.meta.outputs[i]['name'] + " (" + proc.meta.outputs[i]['uom']+ ")");
            }
        }
        proc.color = this.color.get(true);
        var idVisible = Ext.id(), idColor = Ext.id(), idRemove = Ext.id(),
                        idBtnAggregation = Ext.id(), idAggregation = Ext.id(), idToggleAggregation = Ext.id(),
                        idDetailsAggregation = Ext.id(), idBtnAggregationReset = Ext.id(), idDownload = Ext.id(),
                        idBtnAggregationAll = Ext.id();

        var cmp = Ext.getCmp('proceduresTree').add({
            xtype: 'panel',
            //id: 'fs-'+proc.getName(),
            border: false,
            istsos: {
                procedure: proc,
                idVisible: idVisible,
                idColor: idColor,
                idRemove: idRemove,
                chooser: this,
                idToggleAggregation: idToggleAggregation,
                toggleAggregation: false,
                idAggregation: idAggregation,
                idBtnAggregation: idBtnAggregation,
                idBtnAggregationAll: idBtnAggregationAll,
                idBtnAggregationReset: idBtnAggregationReset,
                idDetailsAggregation: idDetailsAggregation,
                idDownload: idDownload
            },
            listeners: {
                "added": {
                    fn: function(panel, container, pos, eOpts){
                        this.fireEvent("procedureAdded", proc);
                    },
                    scope: this,
                    options: {
                        single: true
                    }
                },
                "afterrender": {
                    fn: function(procedureDetailsPanel, layout, eOpts ){

                        //console.log("Afterrender: " + procedureDetailsPanel.istsos.procedure.getName());

                        var v = Ext.get(procedureDetailsPanel.istsos.idVisible);
                        v.on("click",function(){
                            if (this.istsos.procedure.getVisibility()) {
                                Ext.get(this.istsos.idVisible).addCls("pchooserBtnNotVisible");
                            }else{
                                Ext.get(this.istsos.idVisible).removeCls("pchooserBtnNotVisible");
                            }
                            this.istsos.procedure.setVisibility(!this.istsos.procedure.getVisibility());
                        },procedureDetailsPanel);

                        var c = Ext.get(procedureDetailsPanel.istsos.idDownload);
                        c.on("click",function(){
                            var from = Ext.getCmp('oeBegin').getValue();
                            var bt = Ext.getCmp('oeBeginTime').getValue();
                            from.setHours(bt.getHours());
                            from.setMinutes(bt.getMinutes());

                            var to = Ext.getCmp('oeEnd').getValue();
                            var et = Ext.getCmp('oeEndTime').getValue();
                            to.setHours(et.getHours());
                            to.setMinutes(et.getMinutes());

                            var attachment = this.istsos.procedure.getName()+ "_" + Ext.Date.format(to, 'YmdHi') + "00000.csv";

                            var ob = this.istsos.procedure.getObservedProperties();

                            var tz = Ext.getCmp('oeTZ').getValue();
                            var format = Ext.isEmpty(tz) ? "c": "Y-m-d\\TH:i:s";

                            from = Ext.Date.format(from,format);
                            if(!Ext.isEmpty(tz)){
                                from = from + (Ext.isString(tz) ? tz: istsos.utils.minutesToTz(tz));
                            }

                            to = Ext.Date.format(to,format);
                            if(!Ext.isEmpty(tz)){
                                to = to + (Ext.isString(tz) ? tz: istsos.utils.minutesToTz(tz));
                            }

                            var params = {
                                "request": "GetObservation",
                                "attachment": attachment,
                                "offering": this.istsos.procedure.offering,
                                "procedure": this.istsos.procedure.getName(),
                                "eventTime": from+"/"+to,
                                "observedProperty": ob.join(','),
                                "qualityIndex": "True",
                                "responseFormat": "text/plain",
                                "service": "SOS",
                                "version": "1.0.0"
                            };

                            if (Ext.isObject(this.istsos.procedure.aggregation)){
                                params = Ext.apply(params, {
                                    aggregatefunction: this.istsos.procedure.aggregation.f,
                                    aggregateinterval: this.istsos.procedure.aggregation.i,
                                    aggregatenodata: this.istsos.procedure.aggregation.nd,
                                    aggregatenodataqi: this.istsos.procedure.aggregation.ndqi
                                });
                            }
                            params = Ext.Object.toQueryString(params);

                            window.open(Ext.String.format('{0}{1}?{2}', wa.basepath, this.istsos.procedure.service, params));

                            //console.log(params);


                        },procedureDetailsPanel);

                        c = Ext.get(procedureDetailsPanel.istsos.idColor);
                        c.on("click",function(){
                            Ext.create('Ext.window.Window', {
                                title: this.istsos.procedure.getName() + ': color',
                                height: 110,
                                width: 200,
                                closeAction: 'destroy',
                                modal: true,
                                layout: 'fit',
                                items: Ext.create('Ext.picker.Color', {
                                    listeners: {
                                        select: function(picker, selColor) {
                                            this.istsos.procedure.setColor("#"+selColor);
                                            Ext.get(this.istsos.idColor).setStyle("background-color", "#"+selColor);
                                            picker.ownerCt.close();
                                        },
                                        scope: this
                                    }
                                })
                            }).show();
                        },procedureDetailsPanel);


                        c = Ext.get(procedureDetailsPanel.istsos.idRemove);
                        c.on("click",function(){
                            var pchoose = this.ownerCt.ownerCt;
                            this.ownerCt.remove(this);
                            pchoose.fireEvent("procedureRemoved", proc);
                        },procedureDetailsPanel,{
                            single: true
                        });


                        // AGGREGATION FUNCTIONALITIES <<<<<<<<<<<<<<<<<<<<<<<<<

                        procedureDetailsPanel.istsos.procedure.on('aggregationchanged',function(procedure, aggregation){
                            var det = Ext.get(this.istsos.idDetailsAggregation);
                            if (Ext.isObject(aggregation)){
                                det.update(aggregation.f + ", " + aggregation.i + ", " + aggregation.nd + ", " + aggregation.ndqi );
                            }else{
                                det.update("no");
                            }
                            this.istsos.toggleAggregation = false;
                            Ext.getCmp(this.istsos.idAggregation).setVisible( this.istsos.toggleAggregation);
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            form.form.setValues(aggregation);
                        },procedureDetailsPanel);

                        c = Ext.get(procedureDetailsPanel.istsos.idToggleAggregation);
                        c.on("click",function(){
                            this.istsos.toggleAggregation = !this.istsos.toggleAggregation;
                            Ext.getCmp(this.istsos.idAggregation).setVisible( this.istsos.toggleAggregation );
                        },procedureDetailsPanel);

                        c = Ext.getCmp(procedureDetailsPanel.istsos.idBtnAggregation);
                        c.on('click',function(btn){
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            var values = form.getValues();
                            this.istsos.procedure.setAggregation(values);
                        },procedureDetailsPanel);

                        c = Ext.getCmp(procedureDetailsPanel.istsos.idBtnAggregationAll); // APPLY TO ALL
                        c.on('click',function(btn){
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            var values = form.getValues();
                            for ( var k in this.istsos.chooser.procedures) {
                              this.istsos.chooser.procedures[k].setAggregation(values);
                            }
                        },procedureDetailsPanel);

                        c = Ext.getCmp(procedureDetailsPanel.istsos.idBtnAggregationReset);
                        c.on('click',function(btn){
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            form.getForm().reset();
                            this.istsos.procedure.setAggregation(null);
                        },procedureDetailsPanel);
                    },
                    scope: this,
                    options: {
                        single: true
                    }
                }
            },
            cls: 'pchooser',
            items: [
                {
                    xtype: 'panel',
                    border: false,
                    html:
                        "<div>" +
                        "   <div style='border-bottom: thin solid white; padding: 2px; background-color: green; color: white; text-align: center;'>" +
                        "       <span style='font-weight: bold; font-size: 14px;'>" + proc.getName() + "</span>" +
                        "       <div id='"+idVisible+"' class='pchooserBtnVisible' title='Hide this procedure'></div>" +
                        "       <div id='"+idDownload+"' class='pchooserBtnDownload' title='Download CSV data of selected interval'>&nbsp;</div>" +
                        "       <div id='"+idColor+"' class='pchooserBtnColor' style='background-color: "+proc.color+";' title='Choose color'></div>" +
                        "       <div id='"+idRemove+"' class='pchooserBtnRemove' title='Remove this procedure'>&nbsp;</div>" +
                        "   </div>" +
                        "   <div style='font-size: 12px; border-bottom: thin solid green; padding: 2px; background-color: white; color: black; text-align: center;'>" +
                        "       <span style='font-style: italic;'>" + proc.service + ":" + proc.offering + "</span><br/>" +
                        "       <span>Fr:" + proc.getBeginPosition() + "</span><br/>" +
                        "       <span>To:" + proc.getEndPosition() + "</span><br/>" +
                        "       <span style='font-weight: bold;'>" + obsprop.join("<br>") + "</span>" +
                        "   </div>" +
                        "   <div style='font-size: 12px; border-bottom: thin solid green; padding: 2px; background-color: white; color: black; text-align: center;'>" +
                        "       <span id='"+idToggleAggregation+"' style='color: green; cursor: pointer;'>Aggregation: </span>" +
                        "       <span id='"+idDetailsAggregation+"'>no</span>" +
                        "   </div>" +
                        "</div>"
                },
                {
                    xtype: 'form',
                    border: false,
                    hidden: true,
                    id: idAggregation,
                    /*collapsible: true,
                    collapsed: true,
                    hideCollapseTool: true,
                    titleCollapse: true,*/
                    padding: 8,
                    items: [
                        {
                            xtype: 'combobox',
                            //id: 'oeFunction',
                            name: 'f',
                            fieldLabel: 'Function',
                            displayField: 'name',
                            forceSelection: true,
                            queryMode: 'local',
                            store: 'aggregatefunctionstore',
                            valueField: 'name',
                            anchor: '100%'
                        },
                        {
                            xtype: 'textfield',
                            fieldLabel: 'Interval',
                            name: 'i',
                            emptyText: 'PT10M, P1DT',
                            anchor: '100%'
                        },
                        {
                            xtype: 'textfield',
                            value: this.configsections.getobservation.aggregatenodata,
                            name: 'nd',
                            fieldLabel: 'No Data Value',
                            anchor: '100%'
                        },
                        {
                            xtype: 'textfield',
                            value: this.configsections.getobservation.aggregatenodataqi,
                            name: 'ndqi',
                            fieldLabel: 'No Data QI',
                            anchor: '100%'
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: 'toolbar',
                            dock: 'bottom',
                            layout: {
                                align: 'middle',
                                pack: 'center',
                                type: 'hbox'
                            },
                            items: [
                                {
                                    id: idBtnAggregationAll,
                                    xtype: 'button',
                                    text: 'Apply to all'
                                },
                                {
                                    id: idBtnAggregation,
                                    xtype: 'button',
                                    text: 'Apply'
                                },
                                {
                                    id: idBtnAggregationReset,
                                    xtype: 'button',
                                    text: 'Reset'
                                }
                            ]
                        }
                    ]
                }
            ]

        });


    },
    _serviceSelected: function(combo, records, eOpts){
        var pr = Ext.getCmp('oeCbProcedure');
        pr.reset();
        pr.disable();

        var o = Ext.getCmp('oeCbOffering');
        o.reset();
        o.getStore().removeAll();
        o.disable();

        this.fireEvent("serviceSelected", combo.getValue());

        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/offerings/operations/getlist',
                wa.url,combo.getValue()),
            scope: this,
            method: "GET",
            success: function(response){
                var o = Ext.getCmp('oeCbOffering');
                var json = Ext.decode(response.responseText);
                if (json.data.length>0) {
                    o.getStore().loadData(json.data);
                    o.enable();
                    if(json.data.length==1){
                      o.select(o.getStore().getAt(0));
                      this._offeringSelected(Ext.getCmp('oeCbOffering'));
                    }
                }else{
                    o.disable();
                    Ext.Msg.alert("Server message", "\"" + json['message'] + "\"<br/><br/>" +
                            "<small>Status response: " + response.statusText + "</small>");
                }
            }
        });

        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/configsections',wa.url, combo.getValue()),
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    this.configsections = json.data;
                }
            }
        });

    },
    _offeringSelected: function(combo, records, eOpts){
        var pr = Ext.getCmp('oeCbProcedure');
        pr.reset();
        pr.getStore().removeAll();
        pr.disable();

        this.fireEvent("offeringSelected", combo.getValue());

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
                    if(json.data.length==1){
                      this.select(this.getStore().getAt(0));
                    }
                }else{
                    this.disable();
                    Ext.Msg.alert("Server message", "\"" + json['message'] + "\"<br/><br/>" +
                            "<small>Status response: " + response.statusText + "</small>");
                }
            }
        });
    }
});
