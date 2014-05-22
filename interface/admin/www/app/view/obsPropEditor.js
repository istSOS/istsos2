Ext.define('istsos.view.obsPropEditor', {
    extend: 'istsos.view.ui.obsPropEditor',

    initComponent: function() {
        var me = this;
        
        var gs = Ext.create('Ext.data.Store', {
             storeId: 'gridobservedproperties',
             proxy: {
                type: 'ajax',
                url: '',
                reader: {
                    type: 'json',
                    idProperty: 'definition',
                    messageProperty: 'message',
                    root: 'data'
                }
            },
            fields: [
                {
                    name: 'name',
                    type: 'string'
                },
                {
                    name: 'definition',
                    type: 'string'
                },
                {
                    name: 'description',
                    type: 'string'
                },
                {
                    name: 'procedures',
                    type: 'string'
                },
                {
                    name: 'constraint'
                },
                {
                    name: 'constraint2str',
                    type: 'string',
                    convert: function(value, record) {
                        if (record.data.constraint){
                            if (record.data.constraint.min) { // Greater then
                                return "From: " + record.data.constraint.min;
                            } else if (record.data.constraint.max) { // Less then
                                return "To: " + record.data.constraint.max;
                            } else if (record.data.constraint.interval) { // Between
                                return "From: " + record.data.constraint.interval[0] 
                                + " / To: "  + record.data.constraint.interval[1];
                            } else if (record.data.constraint.valueList) { // List
                                return "List: " + record.data.constraint.valueList.join(', ');
                            }
                        }
                        return "-";
                    }
                }
            ]
         });
        
        //var gs = Ext.create('istsos.store.gridObservedProperties');
        
        Ext.create('istsos.store.Constraint');
        
        me.callParent(arguments);
        
        Ext.getCmp("btnNew").on("click",function(){
            this.resetForm();
            Ext.getCmp('opDefinition').setValue(
                Ext.String.format(
                    'urn:ogc:def:parameter:{0}:{1}:',
                    this.istSections.identification.authority ? this.istSections.identification.authority: 'x-istsos',
                    this.istSections.identification.urnversion ? this.istSections.identification.urnversion: '1.0'
                )
            );
            Ext.getCmp('frmObservedProperties').show();
        },this);
                
        Ext.getCmp("btnForm").on("click",function(){
            var f = Ext.getCmp('frmObservedProperties');
            var btn = Ext.getCmp("btnForm");
            
            if (f.getForm().isValid()) {
                var jsonData = f.getValues();
                
                var role = "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0";
                
                switch (jsonData.ctype) {
                    case 1: // Greater then
                        jsonData.constraint = {
                            "role" : role,
                            "min" : jsonData.from
                        };
                        break;
                    case 2: // Less then
                        jsonData.constraint = {
                            "role" : role,
                            "max" : jsonData.to
                        };
                        break;
                    case 3: // Between
                        jsonData.constraint = {
                            "role" : role,
                            "interval" : [jsonData.from, jsonData.to]
                        };
                        break;
                    case 4: // List
                        jsonData.constraint = {
                            "role" : role,
                            "valueList" : jsonData.list.split(",")
                        };
                        break;
                    default:
                        jsonData.constraint = {};
                }
                delete jsonData.list;
                delete jsonData.from;
                delete jsonData.to;
                delete jsonData.ctype;
                
                if (btn.getText()=='Insert') {
                    Ext.Ajax.request({
                        url: Ext.String.format('{0}/istsos/services/{1}/observedproperties',wa.url, this.istService),
                        scope: this,
                        method: "POST",
                        jsonData: jsonData,
                        success: function(response){
                            this.resetForm();
                            Ext.getStore("gridobservedproperties").load();
                            Ext.getCmp('frmObservedProperties').hide();
                        }
                    });
                } else {
                    Ext.Ajax.request({
                        url: Ext.String.format('{0}/istsos/services/{1}/observedproperties/{2}',wa.url, this.istService,Ext.getCmp('opDefinition').originalValue),
                        scope: this,
                        method: "PUT",
                        jsonData: jsonData,
                        success: function(response){
                            this.resetForm();
                            Ext.getStore("gridobservedproperties").load();
                            Ext.getCmp('frmObservedProperties').hide();
                        }
                    });
                }
            }else{
                Ext.MessageBox.show({
                    title: 'Validation error',
                    msg: "Filled data is invalid",
                    buttons: Ext.MessageBox.OK,
                    animateTarget: f
                });
                return;
            }
        },this);
                
        Ext.getCmp("gridop").on("select",function(rowmodel, record, index, eOpts ){
            
            this.resetForm();
            
            Ext.getCmp('frmObservedProperties').loadRecord(record);
            
            var constraint = record.get("constraint");
            var ctypeRec, ctypeCmb = Ext.getCmp('sqiChoose');
            
            /*if (constraint == null || Ext.Object.getKeys(constraint)==0) {
                console.log("ciao");
            } else */
            
            if (constraint){
                if (constraint.min) { // Greater then
                    ctypeCmb.select(1);
                    ctypeRec = ctypeCmb.getStore().findRecord("value", 1);
                    Ext.getCmp('sqiFrom').setValue(constraint.min);
                } else if (constraint.max) { // Less then
                    ctypeCmb.select(2);
                    ctypeRec = ctypeCmb.getStore().findRecord("value", 2);
                    Ext.getCmp('sqiTo').setValue(constraint.max);
                } else if (constraint.interval) { // Between
                    ctypeCmb.select(3);
                    ctypeRec = ctypeCmb.getStore().findRecord("value", 3);
                    Ext.getCmp('sqiFrom').setValue(constraint.interval[0]);
                    Ext.getCmp('sqiTo').setValue(constraint.interval[1]);
                } else if (constraint.valueList) { // List
                    ctypeCmb.select(4);
                    ctypeRec = ctypeCmb.getStore().findRecord("value", 4);
                    Ext.getCmp('sqiList').setValue(constraint.valueList);
                }
            }
            ctypeCmb.fireEvent("select",ctypeCmb,ctypeRec);
            
            Ext.getCmp('btnForm').setText('Update');
            Ext.getCmp('btnRemove').enable();
            Ext.getCmp('frmObservedProperties').show();
            
        },this);
        
        Ext.getCmp("btnRemove").on("click",function(){
            //var sm = Ext.getCmp("gridop").getSelectionModel();
            //var rec = sm.getSelection();
            //if (rec.length>0) {
            Ext.Msg.show({
                    title:'Erasing observed property',
                    msg: 'Are you sure you want to erase the observed property?',
                    buttons: Ext.Msg.YESNO,
                    icon: Ext.Msg.QUESTION,
                    scope: this,
                    fn: function(btn){
                        if (btn == 'yes'){
                            Ext.Ajax.request({
                                url: Ext.String.format('{0}/istsos/services/{1}/observedproperties/{2}',wa.url, this.istService,Ext.getCmp('opDefinition').originalValue),
                                scope: this,
                                method: "DELETE",
                                /*jsonData: {
                                    'name': rec[0].get('name'),
                                    'description': rec[0].get('description')
                                },*/
                                success: function(response){
                                    this.resetForm();
                                    Ext.getStore("gridobservedproperties").load();
                                    Ext.getCmp('frmObservedProperties').hide();
                                }
                            });      
                        }
                    }
            });
                          
            //}
        },this);
        
        
        Ext.getCmp("sqiChoose").on("select",function(combo, records, eOpts){
        
            var value = combo.getValue();
            console.log(value);
            
            var from = Ext.getCmp('sqiFrom');
            var to = Ext.getCmp('sqiTo');
            var list = Ext.getCmp('sqiList');
            
            switch (value) {
                case 0:
                  from.setVisible(false);
                  to.setVisible(false);
                  list.setVisible(false);
                  break;
                case 1:
                  from.setVisible(true);
                  to.setVisible(false);
                  list.setVisible(false);
                  break;
                case 2:
                  from.setVisible(false);
                  to.setVisible(true);
                  list.setVisible(false);
                  break;
                case 3:
                  from.setVisible(true);
                  to.setVisible(true);
                  list.setVisible(false);
                  break;
                case 4:
                  from.setVisible(false);
                  to.setVisible(false);
                  list.setVisible(true);
                  break;
            }
            
        });
        
        //this.istService="sosmilan";
        gs.getProxy().url=Ext.String.format('{0}/istsos/services/{1}/observedproperties',wa.url, this.istService);
    },
    operationLoad: function(){
        Ext.getStore("gridobservedproperties").load();
    },
    resetForm: function(){
        
        Ext.getCmp('frmObservedProperties').loadRecord({
            'data': { 
                'name': '',
                'definition': '',
                'description': '',
                'from': '',
                'to': '',
                'list': ''
            }
        });
        
        Ext.getCmp("sqiChoose").select(0);
        Ext.getCmp('sqiFrom').setVisible(false);
        Ext.getCmp('sqiTo').setVisible(false);
        Ext.getCmp('sqiList').setVisible(false);
        
        Ext.getCmp('opName').clearInvalid();
        Ext.getCmp('opDefinition').clearInvalid();
        Ext.getCmp('btnForm').setText('Insert');
        Ext.getCmp('btnRemove').disable();
        Ext.getCmp("gridop").getSelectionModel().deselectAll();
        
    }
});


function openObsPropEditorWin(istService) {
    var editor = Ext.create("istsos.view.obsPropEditor",{
        istService: istService
    });
    var win = Ext.create('Ext.window.Window', {
        title: 'Observed properties - EDITOR',
        height: 400,
        width: 800,
        layout: 'fit',
        items: editor,
        modal: true
    });
    win.show();
    editor.operationLoad();
    return win;
}
