Ext.define('istsos.view.uomsEditor', {
    extend: 'istsos.view.ui.uomsEditor',

    initComponent: function() {
        var me = this;
        var gs = Ext.create('istsos.store.gridUoms');
        
        me.callParent(arguments);
        
        
        Ext.getCmp("btnNew").on("click",function(){
            this.resetForm();
            Ext.getCmp('frmUoms').show();
        },this);
                
        Ext.getCmp("btnForm").on("click",function(){
            var f = Ext.getCmp('frmUoms');
            var btn = Ext.getCmp("btnForm");
            if (f.getForm().isValid()) {
                var jsonData = f.getValues();
                if (btn.getText()=='New') {
                    Ext.Ajax.request({
                        url: Ext.String.format('{0}/istsos/services/{1}/uoms', wa.url,this.istService),
                        scope: this,
                        method: "POST",
                        jsonData: jsonData,
                        success: function(response){
                            this.resetForm();
                            Ext.getStore("griduoms").load();
            Ext.getCmp('frmUoms').hide();
                        }
                    });
                }else{
                    Ext.Ajax.request({
                        url: Ext.String.format('{0}/istsos/services/{1}/uoms/{2}', wa.url,this.istService,escape(Ext.getCmp('opName').originalValue)),
                        scope: this,
                        method: "PUT",
                        jsonData: jsonData,
                        success: function(response){
                            this.resetForm();
                            Ext.getStore("griduoms").load();
            Ext.getCmp('frmUoms').hide();
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
        
        Ext.getCmp("gridop").columns[2].renderer = function (value, p, record) {
            var ret = [];
            for (var i = 0; i < value.length; i++) {
                var s = Ext.String.format('<span class="softLink" onclick="alert(\'load editor for: '+value[i]+'\')">{0}</span>',value[i]);
                ret.push(s);
            }
            return ret.join(",&nbsp;")
        };
        
        Ext.getCmp("gridop").on("select",function(rowmodel, record, index, eOpts ){
            Ext.getCmp('frmUoms').loadRecord(record);
            Ext.getCmp('btnForm').setText('Update');
            Ext.getCmp('btnRemove').enable();
            Ext.getCmp('frmUoms').show();
        });
        
        
        Ext.getCmp("btnRemove").on("click",function(){
            var sm = Ext.getCmp("gridop").getSelectionModel();
            var rec = sm.getSelection();
            if (rec.length>0) {
                Ext.Ajax.request({
                    url: Ext.String.format('{0}/istsos/services/{1}/uoms/{2}', wa.url,this.istService,Ext.getCmp('opName').originalValue),
                    scope: this,
                    method: "DELETE",
                    jsonData: {
                        'name': rec[0].get('name'),
                        'description': rec[0].get('description')
                    },
                    success: function(response){
                        this.resetForm();
                        Ext.getStore("griduoms").load();
            Ext.getCmp('frmUoms').hide();
                    }
                });                
            }
        },this);
        
        //this.istService="sosmilan";
        gs.getProxy().url=Ext.String.format('{0}/istsos/services/{1}/uoms',wa.url,this.istService);
    },
    operationLoad: function(){
        Ext.getStore("griduoms").load();
    },
    resetForm: function(){
        Ext.getCmp('frmUoms').loadRecord({
            'data': { 
                'name': '',
                'description': ''
            }
        });
        Ext.getCmp('opName').clearInvalid();
        Ext.getCmp('btnForm').setText('New');
        Ext.getCmp('btnRemove').disable();
        Ext.getCmp("gridop").getSelectionModel().deselectAll();
    }
});


function openUomsEditorWin(istService) {
    var editor = Ext.create("istsos.view.uomsEditor",{
        istService: istService
    });
    var win = Ext.create('Ext.window.Window', {
        title: 'Units of measures - EDITOR',
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
