/*
 * File: app/view/ProcedureGrid.js
 * Date: Mon Jan 21 2013 10:59:02 GMT+0100 (CET)
 *
 * This file was generated by Ext Designer version 1.2.3.
 * http://www.sencha.com/products/designer/
 *
 * This file will be generated the first time you export.
 *
 * You should implement event handling and custom methods in this
 * class.
 */

Ext.define('istsos.view.ProcedureGrid', {
    extend: 'istsos.view.ui.ProcedureGrid',
    alias: 'widget.proceduregrid',

    initComponent: function() {
        var me = this;
        me.callParent(arguments);
        this.addEvents('select','selectionchange','gridremoved');
    },
    resetConfig: function(conf){
        this.readOnlyGrid = false;
        this.observedProperty = null;
        if (Ext.isObject(conf)) {
            Ext.apply(this,conf);
        }
    },
    initEditorGrid: function(procedures, procedureName, observedProperty){
        
        this.resetConfig({
            readOnlyGrid: false,
            observedProperty: observedProperty
        });
        
        // @todo think something better and "shirker"
        this.procedures=procedures;
        var procedure = procedures[procedureName];
        this.procedure=procedure;
        
        if (!Ext.getStore('editorQiStore')) {
            Ext.create('Ext.data.Store', {
                storeId: 'editorQiStore',
                autoLoad: true,
                proxy: {
                    type: 'ajax',
                    url: Ext.String.format('{0}/istsos/services/{1}/dataqualities',wa.url, this.procedure.service),
                    reader: {
                        type: 'json',
                        idProperty: 'code',
                        root: 'data'
                    }
                },
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
            });
        }else{
            Ext.getStore('editorQiStore').getProxy().url = Ext.String.format('{0}/istsos/services/{1}/dataqualities',wa.url, this.procedure.service);
            Ext.getStore('editorQiStore').load();
        }
        
        
        
        
        Ext.get(this.id).mask("Initializing editor grid..");
        
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
                //xtype: 'numbercolumn',
                header: properties[i].name,
                dataIndex: procedure.storeConvertFieldToId[properties[i].definition],
                definition: properties[i].definition,
                flex: 0.4,
                editor: {
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
                //xtype: 'gridcolumn',
                header: 'qualityIndex',
                dataIndex: procedure.storeConvertFieldToId[properties[i].definition+':qualityIndex'],
                definition: Ext.String.format('{0}:qualityIndex',properties[i].definition),
                flex: 0.3,
                editor: {
                    xtype: 'combobox',
                    queryMode: 'local',
                    allowBlank: false,
                    hideLabel: true,
                    displayField: 'combo',
                    matchFieldWidth: false,
                    listConfig: {
                        minWidth: 200
                    },
                    store: 'editorQiStore',
                    valueField: 'code',
                    anchor: '100%'
                }
            });
            i++;
        }
        
        var observedProperty = this.observedProperty.definition;
        for (var i = 2; i < columns.length; i++) {
            if (//columns[i]['definition']==procedure.isodef && 
                columns[i]['definition']!=observedProperty && 
                columns[i]['definition']!=observedProperty+':qualityIndex') {
                columns[i]['hidden']=true;
            }
        }
        
        this.grid = Ext.create('Ext.grid.Panel', {
            xtype: 'grid',
            //id: 'oegrid',
            title: '',
            store: procedure.store,
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
            listeners: {
                select: function(grid, record, index, eOpts){
                    this.fireEvent("select", this, grid, record, index, eOpts);
                },
                selectionchange: function(grid, selected, eOpts){
                    this.fireEvent("selectionchange", this, grid, selected, eOpts);
                },
                scope: this
            },
            dockedItems: [
            {
                xtype: 'toolbar',
                dock: 'top',
                items: [
                /*{
                    xtype: 'filefield',
                    emptyText: 'Load CSV..',
                    labelWidth: 40
                },*/
                {
                    xtype: 'button',
                    flex: 1,
                    id: 'btnSave',
                    text: 'Save',
                    disabled: true,
                    handler: function(){
                        if (this.procedure.store.getUpdatedRecords().length>0) {
                            this.procedure.on("observationSaved",function(){
                                this.destroyGrid();
                            },this,{
                                single: true
                            });
                            this.procedure.insertObservation();
                        }else{
                            Ext.Msg.alert('Info', 'Nothing to save.');
                        }
                    },
                    scope: this
                },
                {
                    xtype: 'button',
                    flex: 1,
                    id: 'btnCancel',
                    text: 'Cancel',
                    handler: function(){
                        if (this.procedure.store.getUpdatedRecords().length>0) {
                            Ext.Msg.show({
                                title:'Confirm action',
                                msg: 'There are unsaved changes, are you sure you want to continue this action?',
                                buttons: Ext.Msg.YESNO,
                                icon: Ext.Msg.QUESTION,
                                fn: function(btn, text){
                                    if (btn == 'yes'){
                                        this.destroyGrid();
                                        this.procedure.rejectModifications();
                                    }
                                },
                                scope: this
                            });
                            
                        }else{
                            this.destroyGrid();
                        }
                    },
                    scope: this
                },
                {
                    xtype: 'button',
                    flex: 1,
                    id: 'btnCalc',
                    text: 'Calculator',
                    handler: function(){
                        this.calcWin = Ext.create('Ext.window.Window', {
                            title: 'Calculator',
                            height: 190,
                            width: 700,
                            layout: 'fit',
                            items: Ext.create('istsos.view.Calc',{
                                id: 'calcpanel',
                                grid: Ext.getCmp('proceduregrid').grid,
                                procedure: this.procedure,
                                procedures: this.procedures,
                                observedproperty: this.observedProperty.definition
                            })
                        });
                        this.calcWin.show();
                    },
                    scope: this
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
        this.removeAll();
        this.add(this.grid);
        
        this.procedure.store.on('update',function(){
            this.enable();
        },Ext.getCmp('btnSave'));
        this.procedure.store.on('seriesupdated',function(){
            this.enable();
        },Ext.getCmp('btnSave'));
        
        Ext.get(this.id).unmask();
        
        
    },
    destroyGrid: function(){
        Ext.getCmp('btnSave').disable();
        this.removeAll();
        delete this.grid;
        this.fireEvent("gridremoved", this);
    },
    /*
 * procedures is a dictionary of istsos.Sensor objects
 * 
 * {
 *    "T_BIASCA": {istsos.Sensor}
 * }
 */
    initReadOnlyGrid: function(procedures, observedProperty){
        // @todo: Check if procedures has loaded some data
        
        this.resetConfig({
            readOnlyGrid: true,
            observedProperty: observedProperty
        });
        this.procedures = procedures;
        
        Ext.get('gridpanel').mask("Initializing read only grid..");
        
        var keys = Object.keys(procedures);
        keys = keys.sort();
        
        // Initialization of the grid store and the data model *****************
        var modelFields = [
        {
            name: 'micro', 
            type: 'int'
        },

        {
            name: 'iso8601', 
            type: 'string'
        }            
        ];
        var template = {
            micro: null,
            iso8601: null
        }
        for (var c = 0; c < keys.length; c++) {
            var key = keys[c];
            if (Ext.Array.contains(procedures[key].getObservedProperties(),observedProperty)) {
                modelFields.push({
                    name: key, 
                    type: 'string'
                },{
                    name: key+'_qi', 
                    type: 'string'
                });
                template[key] = "-";
                template[key+'_qi'] = "-";
            }
        }
        // Creating data model
        Ext.define('procedureGridDatamodel', {
            extend: 'Ext.data.Model',
            idProperty: "micro",
            fields: modelFields
        });
        // Creating the store
        this.store = Ext.create('Ext.data.Store', {
            model: 'procedureGridDatamodel',
            proxy: {
                type: 'memory',
                reader: {
                    type: 'array',
                    idProperty: 'micro'
                }
            }
        });
        // Suspends the firing of all events:
        // Pass as true to queue up suspended events to be fired after 
        // the resumeEvents call instead of discarding all suspended events.
        this.store.suspendEvents(false);
        // Merging loaded data to this grid store
        
        for (var c = 0; c < keys.length; c++) {
            var key = keys[c];
            if (Ext.Array.contains(procedures[key].getObservedProperties(),observedProperty)) {
                
                var recs = procedures[key].store.getRange();
                
                for (var j = 0, l = recs.length; j < l; j++) {
                    
                    var rec = null;
                    var idx = this.store.indexOfId(recs[j].get("micro"));
                    
                    if (idx==-1) { // If record does not exist create a new one
                        rec = Ext.create('procedureGridDatamodel', template);
                        rec.set("micro",recs[j].get("micro"));
                        rec.set("iso8601",recs[j].get("iso8601"));
                        this.store.add(rec);
                    }else{// if record exists then use it
                        rec = this.store.getAt(idx);
                    }
                    
                    // Set the property choosen in the chart store in the right column
                    var v = parseFloat(recs[j].get(procedures[key].storeConvertFieldToId[observedProperty]));
                    rec.set(key,v);
                    rec.set(key+"_qi", recs[j].get(procedures[key].storeConvertFieldToId[observedProperty+":qualityIndex"]));   
                    rec.commit(true);
                }
            }
        }
        this.store.sort('micro');
        this.store.resumeEvents();
        
        
        // Initialization of the two always present columns ********************
        var columns = [{
            xtype: 'numbercolumn',
            dataIndex: 'micro',
            hidden: true,
            hideable: false,
            sortable: false,
            header: 'id'
        },{
            xtype: 'gridcolumn',
            dataIndex: 'iso8601', // isodate is always present at position one
            sortable: false,
            hideable: false,
            width: 200,
            //flex: 0.7,
            header: 'Date'
        }];
        for (var c = 0; c < keys.length; c++) {
            var key = keys[c];
            // check if procedures loaded have the requested observed property
            if (Ext.Array.contains(procedures[key].getObservedProperties(),observedProperty)) {
                columns.push({
                    xtype: 'gridcolumn',
                    //xtype: 'numbercolumn',
                    //format: "0'000.000000",
                    dataIndex: key,
                    hideable: false,
                    sortable: false,
                    //flex: 0.4,
                    text: key
                },{
                    xtype: 'gridcolumn',
                    dataIndex: key + "_qi",
                    sortable: false,
                    hideable: false,
                    width: 40,
                    flex: (c+1) == keys.length ? 1: null,
                    text: 'QI'
                });
            }else{
                console.log("Procedure \""+key+"\" has not the desired observed property: " + observedProperty);
            }
        }
        this.grid = Ext.create('Ext.grid.Panel', {
            xtype: 'grid',
            store: this.store,
            autoRender: true,
            autoScroll: true,
            viewConfig: {
            
            },
            columns: columns,
            selModel: Ext.create('Ext.selection.RowModel', {
                allowDeselect: true,
                mode: 'MULTI'
            }),
            listeners: {
                select: function(grid, record, index, eOpts){
                    this.fireEvent("select", this, grid, record, index, eOpts);
                },
                selectionchange: function(grid, selected, eOpts){
                    this.fireEvent("selectionchange", this, grid, selected, eOpts);
                },
                scope: this
            },
            dockedItems: [
                {
                    xtype: 'toolbar',
                    //dock: 'bottom',
                    layout: {
                        align: 'middle',
                        //pack: 'center',
                        type: 'hbox'
                    },
                    items: [
                        {
                            xtype: 'button',
                            text: 'Show CSV',
                            handler: this.showCsv,
                            scope: this
                        }
                    ]
                }
            ]
        });
        
        this.removeAll();
        this.add(this.grid);
        
        Ext.get('gridpanel').unmask();
        
    },
    showCsv: function(){
        //chartdata
        var ret = [this.observedProperty];
        
        var keys = Object.keys(this.procedures);
        keys = keys.sort();
        
        var lineStr = ['DATETIME'];
        for (var c = 0; c < keys.length; c++) {
            var key = keys[c];
            // check if procedures loaded have the requested observed property
            if (Ext.Array.contains(this.procedures[key].getObservedProperties(),this.observedProperty)) {
                lineStr.push(key);
                lineStr.push(key+"_QI");
            }
        }
        ret.push(lineStr.join(","));
        
        var records = this.store.getRange();
        for (var cnta = 0; cnta < records.length; cnta++){
            var rec = records[cnta];
            lineStr = [rec.get('iso8601')];
            for (var c = 0; c < keys.length; c++) {
                var key = keys[c];
                lineStr.push(rec.get(key));
                lineStr.push(rec.get(key+"_qi"));
            }
            ret.push(lineStr.join(","));
        }
        Ext.create('Ext.window.Window', {
            title: 'CSV data',
            height: 400,
            width: 300,
            layout: 'fit',
            modal: true,
            items: {  // Let's put an empty grid in just to illustrate fit layout
                xtype: 'form',
                border: false,
                layout: 'fit',
                items: {
                    xtype     : 'textareafield',
                    //grow      : true,
                    anchor    : '100%',
                    value: ret.join("\n")
                }
            }
        }).show();
        console.log(ret.join("\n"));
    },
    /*
 * MicroArray can be of two type:
 * 1. one array with an integer representing a micro id to be highlighted
 *    example: [1351326600000000] 
 * 2. one array with two integers representing an interval of micro ids to be highlighted
 *    example: [1351326000000000,1351327000000000] 
 */
    updateGridSelection: function(microArray){
        if (!Ext.isEmpty(this.grid)) {
            var selectionModel, store;
            this.suspendEvents(false);
            if (microArray.length==2) {
                selectionModel = this.grid.getSelectionModel();
                store = this.grid.getStore();
                var idx1 = store.find('micro',microArray[0]);
                var idx2 = store.find('micro',microArray[1]);
                selectionModel.selectRange(idx1,idx2);
            }else if (microArray.length==1) {
                selectionModel = this.grid.getSelectionModel();
                store = this.grid.getStore();
                var idx1 = store.find('micro',microArray[0]);
                selectionModel.select(idx1);
            }
            this.resumeEvents();
        }
    },
    removeProcedure: function(procedure){
        delete this.procedures[procedure.getName()];
        if (Ext.Object.getSize(this.procedures)==0) {
            this.removeAll();
        }else{
            if (this.readOnlyGrid) {
                this.initReadOnlyGrid(
                    this.procedures,
                    this.observedProperty);
            }
        }
    }
});