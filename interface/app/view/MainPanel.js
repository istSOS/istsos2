Ext.define('istsos.view.MainPanel', {
    extend: 'istsos.view.ui.MainPanel',
    initComponent: function() {
        this.callParent(arguments);
        this.on("afterrender",function(){
            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/operations/initialization',wa.url),
                scope: this,
                method: 'GET',
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (parseInt(json.data.level)>0) {
                        this.enableStandardView();
                    }else{
                        // Set invisible the menu panel
                        var x = Ext.getCmp("panelMenu");
                        x.setVisible(false);
                        // Initialize the wizard
                        istsos.engine.pageManager.openWizard("initialization");
                    }
                }
            });
        });  
        Ext.getCmp("btnMainMenu").on("click",function(){
            Ext.getCmp('menuCard').getLayout().setActiveItem(0);
        });
        Ext.getCmp("btnServicesMenu").on("click",function(){
            Ext.getCmp('menuCard').getLayout().setActiveItem(1);
        });
    },
    enableStandardView: function(){
        Ext.getCmp("panelMenu").setVisible(true);
        // Load the existing services menu
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services',wa.url),
            scope: this,
            method: 'GET',
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    Ext.getCmp("servicesMenu").removeAll();
                    Ext.getCmp("servicesMenu").add(istsos.engine.pageManager.getServicesMenu(json));
                }else{
                                    
                }
            }
        });          
        // Set the default server configuration menu
        Ext.getCmp("mainMenu").update(istsos.engine.pageManager.getMenuHtml());
    }
});