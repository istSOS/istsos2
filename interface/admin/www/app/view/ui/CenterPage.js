Ext.define('istsos.view.ui.CenterPage', {
    extend: 'istsos.view.ui.BasePage',
    constructor: function(config) {
        if(Ext.isObject(config)){
            Ext.apply(this,config);
        }
        this.istDocId = Ext.id();
        this.addEvents('operationSubmit', 'operationPost', 'operationPut',
            'operationDelete', 'operationGet');
        this.callParent(arguments);
    },
    initComponent: function() {
        this.callParent(arguments);

        if(this.istService){
            Ext.Ajax.request({
                url: Ext.String.format('{0}/istsos/services/{1}/configsections',wa.url, this.istService),
                scope: this,
                method: "GET",
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    if (json.success) {
                        this.configsections = json.data;
                    }
                    if(this.istTitle){
                        this.setTitle(this.istTitle);
                    }
                    if(this.istBody) {
                        if (this.istService) {
                            this.setBody(this.istBody,this.istService);
                        }else{
                            this.setBody(this.istBody);
                        }
                    }
                }
            });
        }else{
            if(this.istTitle){
                this.setTitle(this.istTitle);
            }
            if(this.istBody) {
                if (this.istService) {
                    this.setBody(this.istBody,this.istService);
                }else{
                    this.setBody(this.istBody);
                }
            }
        }
    },
    resetIstConfig: function(){
        Ext.apply(this,{
            istTitle: null,
            istService: null,
            istProcedure: null,
            istDescription: null,
            istBody: null,
            istFunction: null,
            istOperation: null,
            istFooter: null
        });
    },
    getIstConfig: function(){
        return {
            istTitle: this.istTitle,
            istService: this.istService,
            istProcedure: this.istProcedure,
            istDescription: this.istDescription,
            istBody: this.istBody,
            istFunction: this.istFunction,
            istOperation: this.istOperation,
            istFooter: this.istFooter,
            istSections: this.configsections
        };
    },
    initWaurl: function(){
        this.waurl = this.istOperation.restUrl.replace("","");
    },
    setTitle: function(title){
        this.getComponent(1).setTitle( (!Ext.isEmpty(this.istService) ? this.istService: '') + " > " + title);
    },
    setBody: function(){
        this.getComponent(1).removeAll(true);
        // Removing docked button toolbar
        var doc = Ext.getCmp(this.istDocId);
        if (!Ext.isEmpty(doc)) {
            this.getComponent(1).removeDocked(doc,true);
        }
        this.istForm = null;
        // Creating Description panel just over body panel
        if(this.istDescription){
            this.getComponent(1).add({
                xtype: 'panel',
                title: null,
                bodyStyle: 'color: BLACK; font-size: 14px;',
                html: this.istDescription,
                flex: 0.5,
                border: 0,
                bodyPadding: "5px 0px 5px 0px"
            });
        }
        // If istBody is a String that that means that is an html page
        if(Ext.isString(this.istBody)){
            this.getComponent(1).add({
                xtype: 'panel',
                title: null,
                html: this.istBody,
                flex: 0.5,
                border: 0,
                bodyPadding: "5px 0px 5px 0px"
            });
        }else{
            // If istBody is an array then a container is initialized
            if(Ext.isArray(this.istBody)){
                if(this.istBody.length==1){
                    this.istForm = Ext.create(this.istBody[0],Ext.apply({
                        flex: 1
                    },this.getIstConfig()));
                    this.initListeners();
                    this.getComponent(1).add({
                        xtype: 'panel',
                        title: null,
                        items: this.istForm,
                        layout: 'fit',
                        flex: 1,
                        border: 0
                    });
                }else{
                    throw "CenterPage can't handle the given body configuration array.";
                }
            }
        }
        // Construct and initialize actions on button toolbar
        this.initFooter();
    },
    initListeners: function () {
        // Initialize the function to call when the page is displayed.
        // in the config the paramenters to are:
        // istOperation: the url where the standard REST call must be done
        // istBodyOnLoad: the function name of the panel (this.istForm)
        //                  that is loaded inside.

        if (!Ext.isEmpty(this.istOperation) || !Ext.isEmpty(this.istFunction)) {
            this.istForm.on("afterrender",function(cmp, eOpts){

                if (!Ext.isEmpty(this.istFunction) && !Ext.isEmpty(this.istFunction.onLoad)){
                    Ext.callback(this.istForm[this.istFunction.onLoad], this);
                }

                if (!Ext.isEmpty(this.istOperation)){
                    this.operationGet();
                }

            },this, {
                single: true
            });
        }
    },
    initFooter: function(){
        if (!Ext.isEmpty(this["istFooter"])){
            if (this["istFooter"] == istsos.SUBMIT) {
                this.getComponent(1).addDocked({
                    id: this.istDocId,
                    xtype: 'toolbar',
                    //ui: 'footer',
                    //dock: 'bottom',
                    layout: {
                        pack: 'start',
                        //padding: 6,
                        type: 'hbox'
                    },
                    items: [
                    /*{
                        xtype: 'button',
                        id: 'configcancel',
                        //scale: 'medium',
                        text: 'Cancel'
                    },*/
                    {
                        xtype: 'panel',
                        id: "messagesbox",
                        border: 0,
                        html: " ",
                        bodyStyle: 'background-color: transparent; color: white; text-align: right; opacity: 1;',
                        flex: 1
                    },
                    {
                        xtype: 'button',
                        id: 'configsubmit',
                        scope: this,
                        handler: this.operationSubmit,
                        //scale: 'medium',
                        text: 'Submit',
                        //width: 180,
                        flex: 0
                    }
                    ]
                });
            }
        }
    },
    operationSubmit: function(){
        if (!Ext.isEmpty(this.istFunction)) {
            Ext.callback(this.istForm[this.istFunction.onSubmit], this);
        }
        if (!Ext.isEmpty(this.istForm) && !Ext.isEmpty(this.istOperation)){

            if (Ext.isEmpty(this.mask)) {
                this.mask = new Ext.LoadMask(this.body, {
                    msg:"Inserting data..."
                });
            }
            this.mask.show();
            var json = this.istForm.getValues();
            var url = null;
            var method = "PUT";
            if (Ext.isObject(this.istOperation)) {
                url = this.istOperation.restUrl;
                method = this.istOperation.onSubmitMethod?this.istOperation.onSubmitMethod:"POST";
            }else if (Ext.isString(this.istOperation)) {
                url = this.istOperation;
            }else{
                throw "Misconfiguration in pageConfig";
            }

            Ext.Ajax.request({
                url: url,
                scope: this,
                method: method,
                jsonData: json,
                success: function(response){
                    var json = Ext.decode(response.responseText);
                    this.istForm.loadRecord(json);
                    this.mask.hide();
                    this.fireEvent("operationSubmit",json);
                }
            });
        }

    },
    operationGet: function(){
        if (!Ext.isEmpty(this.istOperation)) {
            Ext.getCmp('webadmincmp').showMask("Please wait...");

            var url = null;
            if (Ext.isObject(this.istOperation)) {
                url = this.istOperation.restUrl;
            }else if (Ext.isString(this.istOperation)) {
                url = this.istOperation;
            }else{
                throw "Misconfiguration in pageConfig";
            }
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
                    Ext.getCmp('webadmincmp').hideMask();
                    this.fireEvent("operationGet",json);
                }
            });
        }
    },
    operationPost: function(){
        Ext.getCmp('webadmincmp').showMask("Inserting data...");

        var json = this.istForm.getValues();

        Ext.Ajax.request({
            url: this.waurl,
            scope: this,
            method: 'POST',
            jsonData: json,
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (Ext.getCmp('messageField') != undefined) {
                    if (json.success && !Ext.isEmpty(json.message)) {
                        Ext.getCmp('messageField').setVisible(true);
                        json['data']['message']=json['message']
                    }else{
                        Ext.getCmp('messageField').setVisible(false);
                    }
                }
                this.istForm.loadRecord(json);
                Ext.getCmp('webadmincmp').hideMask();
                this.fireEvent("operationPost",json);
            }
        });
    },
    operationPut: function(){
        Ext.getCmp('webadmincmp').showMask("Updating data...");
        var json = this.istForm.getValues();

        Ext.Ajax.request({
            url: this.waurl,
            scope: this,
            method: 'PUT',
            jsonData: json,
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (Ext.getCmp('messageField') != undefined) {
                    if (json.success && !Ext.isEmpty(json.message)) {
                        Ext.getCmp('messageField').setVisible(true);
                        json['data']['message']=json['message']
                    }else{
                        Ext.getCmp('messageField').setVisible(false);
                    }
                }
                this.istForm.loadRecord(json);
                Ext.getCmp('webadmincmp').hideMask();
                this.fireEvent("operationPut",json);
            }
        });
    }
});
