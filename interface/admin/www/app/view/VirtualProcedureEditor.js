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
        var plist = Ext.create('istsos.store.vplist');
        plist.getProxy().url = Ext.String.format(
            '{0}/istsos/services/{1}/virtualprocedures/operations/getlist',
            wa.url, this.istService
        );

        me.callParent(arguments);

        Ext.getCmp('vppanel').mask = new Ext.LoadMask(Ext.getCmp('vppanel'), {msg:"Please wait..."});


        // Refresh combo store of virtual procedures every time it is expanded
        /*Ext.getCmp('vpcmbplist').on("expand",function(combo){
            this.removeAll();
            this.load();
        },plist);*/

        // When virtual procedure is selected in combo load rating curve grid
        Ext.getCmp('vpcmbplist').on("select",function(combo, record, index, eOpts){
            this.loadRatingCurve(record[0].get('name'));
            this.loadCode(record[0].get('name'));
        },this);


        // *****************************************
        //              CODE EDITOR
        // *****************************************

        this.codeExist = false;

        Ext.getCmp('vpcodingform').add(
            Ext.create('Ext.ux.form.field.CodeMirror', {
                anchor: '100%',
                name: 'code',
                flex: 1,
                mode: {
                    name: "python",
                    version: 2,
                    singleLineStringErrors: false
                },
                hideLabel:  true,
                enableLineNumbers: true,
                lineNumbers: true,
                enableIndentWithTabs: false,
                indentUnit: 4,
                tabMode: "shift",
                matchBrackets: true
            })
        );


        Ext.getCmp('vpbtnsavecode').on('click',function(){

            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/code',
                    wa.url,
                    this.istService,
                    Ext.getCmp('vpcmbplist').getValue()),
                scope: this,
                method: this.codeExist? "PUT": "POST",
                jsonData: Ext.getCmp('vpcodingform').getValues(),
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (!json.success && !Ext.isEmpty(json.message)) {
                        Ext.Msg.alert('Warning', json['message']);
                    }else{
                        this.loadCode(Ext.getCmp('vpcmbplist').getValue());
                    }
                }
            });

        },this);

        Ext.getCmp('vpbtndeletecode').on('click',function(){
            Ext.Msg.show({
                title:'Erasing rating curve',
                msg: 'Are you sure you want to erase the rating curve data?',
                buttons: Ext.Msg.YESNO,
                icon: Ext.Msg.QUESTION,
                scope: this,
                fn: function(btn){
                    if (btn == 'yes'){
                        Ext.Ajax.request({
                            url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/code',
                                wa.url,
                                this.istService,
                                Ext.getCmp('vpcmbplist').getValue()),
                            scope: this,
                            method: "DELETE",
                            success: function(response){
                                var json = Ext.decode(response.responseText);
                                if (!json.success && !Ext.isEmpty(json.message)) {
                                    Ext.Msg.alert('Warning', json['message']);
                                }else{
                                    this.loadCode(Ext.getCmp('vpcmbplist').getValue());
                                }
                            }
                        });
                    }
                }
            });

        },this);


        // *****************************************
        //           RATING CURVE EDITOR
        // *****************************************

        var ratingCurveGrid = Ext.getCmp('vpgridratingcurve');

        // Add row on rating curve grid @ end
        Ext.getCmp('vpbtnaddrc').on('click',function(){
            var row = this.store.getCount();
            var r = Ext.create('ratingCurveModel');
            if (row>0){
                var previous = this.store.getAt(row-1);
                r.set("from",previous.get("to"));
            }
            this.store.insert(row, r);
            if (row>0){
                this.editingPlugin.startEditByPosition({row: row, column: 1});
            }
        },ratingCurveGrid);

        // Add row on rating curve grid above selection
        Ext.getCmp('vpbtnaddbelowrc').on('click',function(){
            var r = Ext.create('ratingCurveModel');
            var sm = this.getSelectionModel();
            var previous = sm.selected.items[0];
            r.set("from",previous.get("to"));
            var row = this.store.indexOf(previous)+1;
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

        Ext.getCmp('vpbtnsaverc').on('click',function(){

            try{
                this.validateRatingCurve();
            }catch (e){
                Ext.Msg.alert('Validation error', e);
                return;
            }

            var recs = Ext.getCmp('vpgridratingcurve').store.getRange();
            var data = [];

            for (var c = 0; c < recs.length; c++){
                var rec = recs[c];
                data.push({
                    "from": Ext.Date.format(rec.data.from,'c'),
                    "to": Ext.Date.format(rec.data.to,'c'),
                    "up_val": ""+rec.get("up_val"),
                    "low_val": ""+rec.get("low_val"),
                    "A": ""+rec.get("A"),
                    "B": ""+rec.get("B"),
                    "C": ""+rec.get("C"),
                    "K": ""+rec.get("K")
                });
            }

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
                    if (!json.success && !Ext.isEmpty(json.message)) {
                        Ext.Msg.alert('Warning', json['message']);
                    }else{
                        this.loadRatingCurve(Ext.getCmp('vpcmbplist').getValue());
                    }
                }
            });

        },this);

        Ext.getCmp('vpbtndeleterc').on('click',function(){

            Ext.Msg.show({
                title:'Erasing rating curve',
                msg: 'Are you sure you want to erase the rating curve data?',
                buttons: Ext.Msg.YESNO,
                icon: Ext.Msg.QUESTION,
                scope: this,
                fn: function(btn){
                    if (btn == 'yes'){
                        Ext.Ajax.request({
                            url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/ratingcurve',
                                wa.url, this.istService, Ext.getCmp('vpcmbplist').getValue()),
                            scope: this,
                            method: "DELETE",
                            success: function(response){
                                var json = Ext.decode(response.responseText);
                                if (!json.success && !Ext.isEmpty(json.message)) {
                                    Ext.Msg.alert('Warning', json['message']);
                                }else{
                                    this.loadRatingCurve(Ext.getCmp('vpcmbplist').getValue());
                                }
                            }
                        });
                    }
                }
            });
        },this);

    },
    loadRatingCurve: function(procedure){
        Ext.getCmp('vppanel').mask.show();
        Ext.getCmp('vpgridratingcurve').store.removeAll();
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/ratingcurve',
                wa.url, this.istService, procedure),
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    Ext.getCmp('vpgridratingcurve').store.loadData(json.data);
                }else{
                    console.log(json.message);
                }
                Ext.getCmp('vppanel').mask.hide();
            }
        });
    },
    // Validate single row of the rating curve grid
    validateRatingCurveRecord: function(rec){
        Ext.Array.each(['from','to'], function(key) {
            if (!Ext.isDate(rec.get(key))){
                throw "\""+key+"\" field must be a valid date";
            }
        });
        Ext.Array.each(['A','B','C','K','up_val','low_val'], function(key) {
            if (!Ext.isNumeric(rec.get(key))){
                throw "\""+key+"\" field must be numeric";
            }
        });
    },
    // Validate all rows of the rating curve grid
    validateRatingCurve: function(){
        var recs = Ext.getCmp('vpgridratingcurve').store.getRange();
        if (recs.length==0){
            throw "The rating curve data grid is empty";
        }
        var from, to;
        for (var c = 0; c < recs.length; c++){

            var rec = recs[c];

            try{
                this.validateRatingCurveRecord(rec);
            }catch (e){
                throw 'Line ' + (c+1) + ': ' + e;
            }

            // Check dates
            if (c===0){
                from = rec.get('from');
                to = rec.get('to');
                low = rec.get('low_val');
                up = rec.get('up_val');
            }else{
                if (rec.get('from').getTime() == from.getTime() && rec.get('to').getTime() == to.getTime()){
                    if (rec.get('low_val') != up){
                        throw 'Line ' + (c+1) + ' [Low/Up error]: \"Low\" must be equal to \"Up\" in previous line';
                    }
                }else if (rec.get('from').getTime()  != to.getTime() ){
                    throw 'Line ' + (c+1) + ' [Date error]: \"From\" must be equal to \"To\" in previous line';
                }
                from = rec.get('from');
                to = rec.get('to');
                low = rec.get('low_val');
                up = rec.get('up_val');
            }
            if (from>=to){
                throw 'Line ' + (c+1) + ' [Date error]: \"From\" must be prior to \"To\"';
            }
        }
    },
    loadCode: function(procedure){
        Ext.getCmp('vppanel').mask.show();
        Ext.getCmp('vpcodingform').loadRecord( { data:{code:''} });
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/virtualprocedures/{2}/code',
                wa.url, this.istService, procedure),
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    //Ext.getCmp('vpgridratingcurve').store.loadData(json.data);
                    Ext.getCmp('vpcodingform').loadRecord(json);
                    this.codeExist = true;
                }else{
                    console.log(json.message);
                    this.codeExist = false;
                }
                Ext.getCmp('vppanel').mask.hide();
            }
        });
    }
});
