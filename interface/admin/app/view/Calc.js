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

Ext.define('istsos.store.CalcQiStore', {
    extend: 'Ext.data.Store',
    constructor: function(cfg) {
        var me = this;
        cfg = cfg || {};
        me.callParent([Ext.apply({
            storeId: 'calcQiStore',
            fields: [
            {
                name: 'code'
            },
            {
                name: 'combo',
                convert: function(v, record){
                    return record.get('code')  + " - " + record.get('name');
                }
            },
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

Ext.define('istsos.view.Calc', {
    extend: 'istsos.view.ui.Calc',
    msgs: {
        interpolation: 'Your calculation cannot be applied using values from procedure {0}'
    + ', it is not synchronized with procedure {1}.<br><br>' 
    + '<small>Tip: apply a linear interpolation on {0}.</small>'
    },
    initComponent: function() {
        
        var me = this;
        
        if (Ext.isEmpty(Ext.getStore('editableProcedure'))) {
            Ext.create('Ext.data.Store',{
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
        }
        
        this.qis = Ext.create('istsos.store.CalcQiStore',{
            autoLoad: true,
            proxy: {
                type: 'ajax',
                url: Ext.String.format('{0}/istsos/services/{1}/dataqualities',wa.url, this.procedure.service),
                reader: {
                    type: 'json',
                    idProperty: 'code',
                    root: 'data'
                }
            }
        });
        
        me.callParent(arguments);
        
        Ext.getCmp('pEditing').setValue(this.procedure.getName()+" = ");
        
        this.code = Ext.create('Ext.ux.form.field.CodeMirror', {
            fieldLabel: 'Operation',
            anchor:     '100%',
            flex: 1,
            mode:       'text/javascript',
            hideLabel:  true,
            enableLineNumbers: false
        });
       
        Ext.getCmp('codePanel').add(this.code);
        
        this.stats = {};
        
        Ext.getCmp('editableProcedureGrid').getView().on('itemdblclick',
            function(view, record, item, index, ev, eOpts){                
                var pos = this.code.editor.getCursor(true);
                this.code.editor.replaceRange(record.get("name"), pos, pos);
                this.code.editor.focus();            
            },this);
            
        Ext.getCmp('btnExecute').on("click",function(){
            
            this.cnt = new Date().getTime();
            
            // Apply function
            var pKeys = Ext.Object.getKeys(this.procedures);
            var tmp = Ext.Array.clone(pKeys);
            var func = this.code.getValue();
            
            // Removing procedures that are not involved
            for (var i = 0; i < tmp.length; i++) {
                if (func.indexOf(tmp[i])==-1) {
                    pKeys = Ext.Array.remove(pKeys,tmp[i]);
                }
            }
            
            // Get an array of the currently selected records.
            //var recs = this.chartpanel.grid.getSelectionModel().getSelection();
            var recs = this.grid.getSelectionModel().getSelection();
            
            var st = {};
            
            this.procedure.store.suspendEvents();
            
            var qi = Ext.getCmp('calcQiCombo').getValue();
            
            // Updating STORE --------------------
            for (var i = 0; i < recs.length; i++) {
                
                var vars = "";
                var field = this.procedure.storeConvertFieldToId[this.observedproperty];
                var fieldQi = this.procedure.storeConvertFieldToId[this.observedproperty+":qualityIndex"];
                
                for (var c = 0; c < pKeys.length; c++) {
                    var os = this.procedures[pKeys[c]].store;
                    var rec = os.getById(recs[i].get('micro'));
                    if (rec==null) {
                        Ext.Msg.alert('Warning', Ext.String.format(this.msgs.interpolation, pKeys[c], this.procedure.sensor));
                        for (; i >= 0; i--) {
                            recs[i].reject();
                        }
                        this.procedure.store.resumeEvents();                    
                        return;
                    }
                    vars += "var "+pKeys[c]+"="+rec.get(this.procedures[pKeys[c]].storeConvertFieldToId[this.observedproperty])+"; ";
                    eval(vars);
                }
                
                if (!Ext.isEmpty(func)) {
                    var x = eval(func);
                    recs[i].set(field,x);
                }
                if (!Ext.isEmpty(qi)) {
                    recs[i].set(fieldQi,qi);
                }
            }
            
            // Refreshing GRID --------------------
            this.procedure.store.resumeEvents();
            this.grid.getView().refresh();
            
            // Refreshing CHART --------------------
            this.procedure.store.fireEvent(
                "seriesupdated", 
                this.procedure.store, recs);
                
            
        },this);
        
        Ext.getCmp('plus').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("+", pos, pos);
            this.code.editor.focus();
        },this);
        
        Ext.getCmp('minus').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("-", pos, pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('less').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("<", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('moltiply').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("*", pos, pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('divide').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("/", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('grater').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange(">", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('sqrt').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.sqrt()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('cos').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.cos()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('equal').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("=", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('sin').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.sin()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('asin').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.asin()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('lesseq').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("<=", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('exp').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("^", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('tan').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.tan()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('gretereq').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange(">=", pos, pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('acos').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.acos()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
        
        Ext.getCmp('atan').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("Math.atan()", pos, pos);
            pos = this.code.editor.getCursor(true);
            pos.ch = pos.ch - 1;
            this.code.editor.setCursor(pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('andop').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("&&", pos, pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('openparentesis').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("(", pos, pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('closedparentesis').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange(")", pos, pos);
            this.code.editor.focus();  
        },this);
       
        Ext.getCmp('orop').on("click",function(){
            var pos = this.code.editor.getCursor(true);
            this.code.editor.replaceRange("||", pos, pos);
            this.code.editor.focus();  
        },this);
        
    },
    // Return and interpolated record for milli value, between the too given records
    interpolate: function(x, rec0, rec1){
        var obsprop = Ext.getCmp("oeCbObservedProperty").getValue();
        //var x0=rec0.get(wa.isodef).getTime();
        var x0=rec0.get('micro');
        var y0=rec0.get(obsprop);
        //var x1=rec1.get(wa.isodef).getTime();
        var x1=rec1.get('micro');
        var y1=rec1.get(obsprop);
        // Interpolation function
        var y = y0 + ( (x-x0)*y1 - (x-x0)*y0) / ( x1 - x0);
        var ret = rec0.copy();
        //ret.set(wa.isodef,Ext.Date.parse(x, "U"));
        ret.set('micro',Ext.Date.parse(x, "U").getTime());
        ret.set(obsprop,y);
    }
});
