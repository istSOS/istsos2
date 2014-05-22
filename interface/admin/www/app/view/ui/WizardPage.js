Ext.define('istsos.view.ui.WizardPage', {
    extend: 'istsos.view.ui.CenterPage',
    constructor: function(config) {
        if(Ext.isObject(config)){
            Ext.apply(this,config);
            // Get first configured wizard page
            for (var k in config.istConfig){
                Ext.apply(this,config.istConfig[k],{
                    istWizardPage: k
                });
                break;
            }
        }
        this.callParent(arguments);
        this.on('operationSubmit', function(json){
            if (json.success) {
                this.nextPage();
            }
        }, this);
    },
    initFooter: function(){
        if (!Ext.isEmpty(this["istFooter"])){
            if(this["istFooter"] == istsos.WIZARD_JUST_NEXT){
                this.getComponent(1).addDocked({
                    xtype: 'toolbar',
                    id: this.istDocId,
                    //ui: 'footer',
                    //dock: 'bottom',
                    layout: {
                        pack: 'end',
                        padding: 6,
                        type: 'hbox'
                    },
                    items: [
                    {
                        xtype: 'button',
                        id: 'wizardnext',
                        //scale: 'medium',
                        scope: this,
                        handler: this.nextPage,
                        text: 'Next'
                    }
                    ]
                });
            } else if(this["istFooter"] == istsos.WIZARD){
                this.getComponent(1).addDocked({
                    xtype: 'toolbar',
                    id: this.istDocId,
                    //ui: 'footer',
                    //dock: 'bottom',
                    layout: {
                        pack: 'end',
                        padding: 6,
                        type: 'hbox'
                    },
                    items: [
                    {
                        xtype: 'button',
                        id: 'wizardback',
                        //scale: 'medium',
                        handler: this.backPage,
                        scope: this,
                        text: 'Back'
                    },
                    {
                        xtype: 'button',
                        id: 'wizardnext',
                        scope: this,
                        handler: this.operationSubmit,
                        //scale: 'medium',
                        text: 'Next'
                    }
                    ]
                });
            } else if(this["istFooter"] == istsos.WIZARD_NEXT_FINISH){
                this.getComponent(1).addDocked({
                    xtype: 'toolbar',
                    id: this.istDocId,
                    //ui: 'footer',
                    //dock: 'bottom',
                    layout: {
                        pack: 'end',
                        padding: 6,
                        type: 'hbox'
                    },
                    items: [
                    {
                        xtype: 'button',
                        id: 'wizardfinish',
                        scope: this,
                        handler: this.finishPage,
                        //scale: 'medium',
                        text: 'Finish'
                    },
                    {
                        xtype: 'tbspacer',
                        width: 20
                    },
                    {
                        xtype: 'button',
                        id: 'wizardback',
                        //scale: 'medium',
                        handler: this.backPage,
                        scope: this,
                        text: 'Back'
                    },
                    {
                        xtype: 'button',
                        id: 'wizardnext',
                        scope: this,
                        handler: this.operationSubmit,
                        //scale: 'medium',
                        text: 'Next'
                    }
                    ]
                });
            } else if(this["istFooter"] == istsos.WIZARD_FINISH){
                this.getComponent(1).addDocked({
                    xtype: 'toolbar',
                    id: this.istDocId,
                    //ui: 'footer',
                    //dock: 'bottom',
                    layout: {
                        pack: 'end',
                        padding: 6,
                        type: 'hbox'
                    },
                    items: [
                    {
                        xtype: 'button',
                        id: 'wizardfinish',
                        scope: this,
                        handler: this.finishPage,
                        //scale: 'medium',
                        text: 'Finish'
                    }
                    ]
                });
            }
            this.callParent();
        }        
    },
    /*operationSubmit: function(){
        this.callParent(arguments);
    },*/
    nextPage: function(){
        var onemore = false;
        for (var k in this.istConfig){
            if (onemore) {
                this.resetIstConfig();
                Ext.apply(this,this.istConfig[k],{
                    istWizardPage: k
                });
                break;
            }
            if (k == this.istWizardPage) {
                onemore = true;
            }
        }
        this.setTitle(this.istTitle);
        this.setBody();
    },
    backPage: function(){
        var page = "";
        for (var k in this.istConfig){
            if (k == this.istWizardPage) {
                Ext.apply(this,this.istConfig[page],{
                    istWizardPage: page
                });
                break;
            }
            page = k;
        }
        this.setTitle(this.istTitle);
        this.setBody();
    },
    finishPage: function(){
        var mainCenter = Ext.getCmp("mainCenter");
        mainCenter.removeAll(true);
        Ext.getCmp('submenu').expand();
        this.loadServiceMenu();
    }
});