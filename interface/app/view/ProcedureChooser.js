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
            "procedureRemoved" : true
        });
        
        Ext.create('istsos.store.Offerings');
        Ext.create('istsos.store.gridProceduresList');
        var ssrv = Ext.create('istsos.store.Services');
        ssrv.getProxy().url = Ext.String.format('{0}/istsos/services',wa.url);
        
        this.procedures = {};
        
        me.callParent(arguments);
        
        Ext.getCmp("cmbServices").on("select",function(combo, records, eOpts){
            var pr = Ext.getCmp('oeCbProcedure');
            pr.reset();
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
            
        /*o.disable();
            o.getStore().load({
                url: Ext.String.format('{0}/istsos/services/{1}/offerings/operations/getlist',
                    wa.url,combo.getValue()),
                callback: function(records, operation, success){
                    this.enable();
                },
                scope: o
            });*/
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
            /*
            pr.getStore().load({
                url: Ext.String.format('{0}/istsos/services/{1}/offerings/{2}/procedures/operations/memberslist',
                    wa.url,Ext.getCmp('cmbServices').getValue(),combo.getValue()),
                callback: function(records, operation, success){
                    this.enable();
                },
                scope: pr
            });*/
        });
        
        Ext.getCmp("btnAdd").on("click",function(btn, e, eOpts){
            
            // Add an istsos.Procedure in the this.procedures array
            // every row contains some describeSensor data
            var service = Ext.getCmp("cmbServices").getValue();
            var offering = Ext.getCmp("oeCbOffering").getValue();
            var procedure = Ext.getCmp("oeCbProcedure").getValue();
            
            this.procedures[procedure] = Ext.create('istsos.Sensor', 
                service, offering, procedure, {
                    listeners: {
                        metadataLoaded: this._getProcedureDetails,
                        scope: this
                    }
                });
            
        },this);
    },
    _getProcedureDetails: function(proc){
        var obsprop = [];
        for (var i = 0; i < proc.meta.outputs.length; i++) {
            if (proc.meta.outputs[i]['definition']!=proc.isodef) {
                obsprop.push(proc.meta.outputs[i]['name'] + " (" + proc.meta.outputs[i]['uom']+ ")");
            }
        }
        proc.color = this.color.get(true);
        var idVisible = Ext.id(), idColor = Ext.id(), idRemove = Ext.id();
        var cmp = Ext.getCmp('proceduresTree').add({
            xtype: 'panel',
            //id: 'fs-'+proc.getName(),
            border: false,
            istsos: {
                procedure: proc,
                idVisible: idVisible,
                idColor: idColor,
                idRemove: idRemove,
                chooser: this
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
                        
                        console.log("Afterrender: " + procedureDetailsPanel.istsos.procedure.getName());
                        
                        var v = Ext.get(procedureDetailsPanel.istsos.idVisible);
                        v.on("click",function(){
                            if (this.istsos.procedure.getVisibility()) {
                                Ext.get(this.istsos.idVisible).addCls("pchooserBtnNotVisible");
                            }else{
                                Ext.get(this.istsos.idVisible).removeCls("pchooserBtnNotVisible");
                            }
                            this.istsos.procedure.setVisibility(!this.istsos.procedure.getVisibility());
                        },procedureDetailsPanel);
                    
                        var c = Ext.get(procedureDetailsPanel.istsos.idColor);
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
                    
                    
                        var d = Ext.get(procedureDetailsPanel.istsos.idRemove);
                        d.on("click",function(){
                            var pchoose = this.ownerCt.ownerCt;
                            this.ownerCt.remove(this);
                            pchoose.fireEvent("procedureRemoved", proc);
                        },procedureDetailsPanel,{
                            single: true
                        });
                    
                    },
                    scope: this,
                    options: {
                        single: true
                    }
                }
            },
            html: 
            "<div class='pchooser'>" +
            "   <div style='border-bottom: thin solid white; padding: 2px; background-color: green; color: white; text-align: center;'>" +
            "       <span style='font-weight: bold; font-size: 14px;'>" + proc.getName() + "</span>" +
            "       <div id='"+idVisible+"' class='pchooserBtnVisible'></div>" +
            "       <div id='"+idColor+"' class='pchooserBtnColor' style='background-color: "+proc.color+";'></div>" +
            "       <div id='"+idRemove+"' class='pchooserBtnRemove'>x</div>" +
            "   </div>" +
            "   <div style='font-size: 12px; border-bottom: thin solid green; padding: 2px; background-color: white; color: black; text-align: center;'>" +
            "       <span style='font-style: italic;'>" + proc.service + ":" + proc.offering + "</span><br/>" +
            "       <span>Fr:" + proc.getBeginPosition() + "</span><br/>" +
            "       <span>To:" + proc.getEndPosition() + "</span><br/>" +
            "       <span style='font-weight: bold;'>" + obsprop.join("<br>") + "</span>" +
            "   </div>" +
            "</div>"
        });
        
        
    }
});