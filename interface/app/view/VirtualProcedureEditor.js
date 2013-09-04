Ext.define('istsos.view.VirtualProcedureEditor', {
    extend: 'istsos.view.ui.VirtualProcedureEditor',
    alias: 'widget.virtualprocedureeditor',

    initComponent: function() {
        var me = this;
        
        // Store for the rating curve grid
        var ratingCurveStore = Ext.create('istsos.store.RatingCurve');
        Ext.define('ratingCurveModel', {
            extend: 'Ext.data.Model',
            fields: [
                {
                    name: 'from',
                    type: 'date'
                },
                {
                    name: 'to',
                    type: 'date'
                },
                {
                    name: 'low_val',
                    type: 'float'
                },
                {
                    name: 'up_val',
                    type: 'float'
                },
                {
                    name: 'A',
                    type: 'float'
                },
                {
                    name: 'B',
                    type: 'float'
                },
                {
                    name: 'C',
                    type: 'float'
                },
                {
                    name: 'K',
                    type: 'float'
                }
            ]
        });
        
        // Store for combo listing virtual procedures
        var plist = Ext.create('istsos.store.gridProceduresList');
        plist.getProxy().url = Ext.String.format(
            '{0}/istsos/services/{1}/virtualprocedures/operations/getlist', 
            wa.url, this.istService
        );
        
        me.callParent(arguments);
        
        var ratingCurveGrid = Ext.getCmp('vpgridratingcurve');
        
        // Add row on rating curve grid at end
        Ext.getCmp('vpbtnaddrc').on('click',function(){
            var r = Ext.create('ratingCurveModel');
            var row = this.store.getCount();
            this.store.insert(row, r);
            this.editingPlugin.startEditByPosition({row: row, column: 0});
        },ratingCurveGrid);
        
        // Add row on rating curve grid above selection
        Ext.getCmp('vpbtnaddbelowrc').on('click',function(){
            var r = Ext.create('ratingCurveModel');
            var sm = this.getSelectionModel();
            var firstSelection = sm.selected.items[0];
            var row = this.store.indexOf(firstSelection)+1;
            this.store.insert(row, r);
            this.editingPlugin.startEditByPosition({row: row, column: 0});
        },ratingCurveGrid);
        
        // Add row on rating curve grid below selection
        Ext.getCmp('vpbtnaddaboverc').on('click',function(){
            var r = Ext.create('ratingCurveModel');
            var sm = this.getSelectionModel();
            var firstSelection = sm.selected.items[0];
            var row = this.store.indexOf(firstSelection);
            this.store.insert(row, r);
            this.editingPlugin.startEditByPosition({row: row, column: 0});
        },ratingCurveGrid);
        
        // Remove selected row from rating curve grid
        Ext.getCmp('vpbtnremoverc').on('click',function(){
            var r = Ext.create('ratingCurveModel');
            var sm = this.getSelectionModel();
            var firstSelection = sm.selected.items[0];
            this.store.remove(sm.selected.items[0]);
            Ext.getCmp('vpbtnaddbelowrc').disable();
            Ext.getCmp('vpbtnaddaboverc').disable();
            Ext.getCmp('vpbtnremoverc').disable();
        },ratingCurveGrid);
        
        // Enable buttons when grid rows selected
        ratingCurveGrid.getSelectionModel().on("select",function(){
            Ext.getCmp('vpbtnaddbelowrc').enable();
            Ext.getCmp('vpbtnaddaboverc').enable();
            Ext.getCmp('vpbtnremoverc').enable();
        });
        
        // Enable buttons when grid rows deselected
        ratingCurveGrid.getSelectionModel().on("deselect",function(){
            Ext.getCmp('vpbtnaddbelowrc').disable();
            Ext.getCmp('vpbtnaddaboverc').disable();
            Ext.getCmp('vpbtnremoverc').disable();
        });
        
        // Refresh combo store of virtual procedures every time it is expanded
        Ext.getCmp('vpcmbplist').on("expand",function(combo){
            this.removeAll();
            this.load();
        },plist);
        
        // When virtual procedure is selected in combo load rating curve grid
        Ext.getCmp('vpcmbplist').on("select",function(combo, record, index, eOpts){
            //Ext.getCmp('vppanel').mask.show();
            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/ratingcurve', 
                    wa.url, 
                    this.istService, 
                    record[0].get('name')),
                scope: this,
                method: "GET",
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (json.success) {
                        Ext.getCmp('vpgridratingcurve').store.loadData(json.data);
                    }
                }
            });
        },this);
        
        Ext.getCmp('vpbtnsaverc').on('click',function(){
        
            console.log(this);
            
            var recs = Ext.getCmp('vpgridratingcurve').store.getRange();
            var data = [];
            for (var c = 0; c < recs.length; c++){
                var rec = recs[c];
                data.push({
                    "A": ""+rec.get("A"), 
                    "C": ""+rec.get("C"), 
                    "B": ""+rec.get("B"), 
                    "from": Ext.Date.format(rec.data.from,'c'), 
                    "up_val": ""+rec.get("up_val"), 
                    "K": ""+rec.get("K"), 
                    "low_val": ""+rec.get("low_val"), 
                    "to": Ext.Date.format(rec.data.to,'c')
                });
            }
            console.log(data);
            
            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/ratingcurve', 
                    wa.url, 
                    this.istService, 
                    Ext.getCmp('vpcmbplist').getValue()),
                scope: this,
                method: "POST",
                jsonData: data,
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (json.success) {
                        console.log("ciao");
                    }
                }
            });
            
        },this);
    }
    
});
