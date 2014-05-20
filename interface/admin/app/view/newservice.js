Ext.define('istsos.view.newservice', {
    extend: 'istsos.view.ui.newservice',
    initComponent: function() {
        var me = this;
        me.callParent(arguments);
        Ext.getCmp('btnTestConnection').on("click",function(){
            
            if (Ext.isEmpty(this.mask)) {
                this.mask = new Ext.LoadMask(this.body, {
                    msg:"Please wait..."
                });
            }
            this.mask.show();
            
            console.dir(this.getForm().getValues())
            
            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/operations/validatedb', wa.url),
                scope: this,
                method: 'POST',
                jsonData: this.getForm().getValues(),
                success: function(response){
                    this.mask.hide();
                    var json = Ext.decode(response.responseText);
                    if (json['success']) {
                        Ext.MessageBox.show({
                            title: 'Test success',
                            msg: "Database: " + json['data']['database'] + "<br/><br/>" + 
                                "<small>"+json['message']+"</small>",
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.Msg.INFO,
                            animateTarget: 'btnTestConnection'
                        });
                    }else{
                        Ext.MessageBox.show({
                            title: 'Test failure',
                            msg: json['message'],
                            buttons: Ext.MessageBox.OK,
                            icon: Ext.Msg.WARNING,
                            animateTarget: 'btnTestConnection'
                        });
                    }
                }
            });
        },this);
    },
    operationLoad: function(){
        if (Ext.isEmpty(this.mask)) {
            this.mask = new Ext.LoadMask(this.body, {
                msg:"Please wait..."
            });
        }
        this.mask.show();
        var url = Ext.String.format('{0}/istsos/services/default/configsections/connection', wa.url);
        Ext.Ajax.request({
            url: url,
            scope: this,
            method: "GET",
            success: function(response){
                try {
                    var json = Ext.decode(response.responseText);
                    this.istForm.loadRecord(json);
                } catch (exception) {
                    console.error(exception);
                }
                this.mask.hide();
                this.fireEvent("operationGet",json);
            }
        });
    },
    operationPost: function(){
        
        var json = this.istForm.getValues();
            
        if (Ext.isEmpty(json['customdb'])) {
            if (!Ext.getCmp('nsservice').isValid()){
                Ext.Msg.alert('Validation error', 'Service name is invalid, it must be a single lower case word.');
                return;
            }
            json = {
                "service": json['service']
            };
        }else{
            if (!this.istForm.getForm().isValid()){
                Ext.Msg.alert('Validation error', 'Please correct the invalid values');
                return;
            }
        }
        
        if (Ext.isEmpty(this.mask)) {
            this.mask = new Ext.LoadMask(this.body, {
                msg:"Please wait..."
            });
        }
        this.mask.show();
        
        if (Ext.isEmpty(json.epsg)){
            delete json.epsg;
        }
        
        this.servicename = json['service'];
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services', wa.url),
            scope: this,
            method: "POST",
            jsonData: json,
            success: function(response){
                var json = Ext.decode(response.responseText);
                this.mask.hide();
                Ext.getCmp('webadmincmp').loadServiceMenu();
                this.fireEvent("operationSubmit",json);
            }
        });
    }
});
