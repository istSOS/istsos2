Ext.define('istsos.view.serviceEditor', {
    extend: 'istsos.view.ui.serviceEditor',

    initComponent: function() {
        var me = this;
        var strsrv = Ext.create('istsos.store.Services');
        strsrv.getProxy().url = Ext.String.format('{0}/istsos/services', wa.url);
            
        me.callParent(arguments);
        
        Ext.getCmp("btnNew").on("click",function(){
            this.resetForm();
        },this);
        
        Ext.getCmp("btnForm").on("click",function(){
            var f = Ext.getCmp('frmServices');
            var btn = Ext.getCmp("btnForm");
            if (f.getForm().isValid()) {
                var jsonData = f.getValues();
                if (btn.getText()=='New') {
                    Ext.Ajax.request({
                        url: Ext.String.format('{0}/istsos/services', wa.url,Ext.getCmp('opService').originalValue),
                        scope: this,
                        method: "POST",
                        jsonData: jsonData,
                        success: function(response){
                            this.resetForm();
                            Ext.getStore("storeServices").load();
                            Ext.getCmp('webadmincmp').loadServiceMenu();
                        }
                    });
                }else{
                    Ext.Ajax.request({
                        url: Ext.String.format('{0}/istsos/services/{1}', wa.url,Ext.getCmp('opService').originalValue),
                        scope: this,
                        method: "PUT",
                        jsonData: jsonData,
                        success: function(response){
                            this.resetForm();
                            Ext.getStore("storeServices").load();
                            Ext.getCmp('webadmincmp').loadServiceMenu();
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
            Ext.getCmp('frmServices').loadRecord(record);
            Ext.getCmp('btnForm').setText('Update');
            Ext.getCmp('btnRemove').enable();
        });
        
        
        Ext.getCmp("btnRemove").on("click",function(){
        
            Ext.Msg.show({
                    title:'Erasing service',
                    styleHtmlContent: true,
                    msg: '<strong>This operation cannot be undone!</strong><br/><br/>are you sure you want to erase the selected service and all of its procedures/observations?',
                    buttons: Ext.Msg.YESNO,
                    icon: Ext.Msg.QUESTION,
                    fn: function(btn){
                        if (btn == 'yes'){
                            var sm = Ext.getCmp("gridop").getSelectionModel();
                            var rec = sm.getSelection();
                            if (rec.length>0) {
                                Ext.Ajax.request({
                                    url: Ext.String.format('{0}/istsos/services/{1}', wa.url,Ext.getCmp('opService').originalValue),
                                    scope: this,
                                    method: "DELETE",
                                    jsonData: {
                                        'service': rec[0].get('service')
                                    },
                                    success: function(response){
                                        this.resetForm();
                                        Ext.getStore("storeServices").load();
                                        Ext.getCmp('webadmincmp').loadServiceMenu();
                                    }
                                });                
                            } 
                        }
                    },
                    scope: this
                });     
        
            
        },this);
        
    },
    operationLoad: function(){
        Ext.getStore("storeServices").load();
    },
    resetForm: function(){
        Ext.getCmp('frmServices').loadRecord({
            'data': { 
                'service': ''
            }
        });
        Ext.getCmp('opService').clearInvalid();
        Ext.getCmp('btnForm').setText('New');
        Ext.getCmp('btnRemove').disable();
        Ext.getCmp("gridop").getSelectionModel().deselectAll();
    }
});
