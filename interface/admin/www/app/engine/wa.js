wa = {};
wa.isodef = "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601";
wa.basepath = "../";
wa.url = wa.basepath+"wa";

wa.createPath = function(){
    var waUrl = wa.url;
    for (var i = 0; i < arguments.length; i++) {
        if (Ext.isObject(arguments[i])){
            if (!Ext.isEmpty(arguments[i].istService)) {
                waUrl += "/"+arguments[i].istService;
            }
        }else{
            waUrl += "/"+arguments[i];
        }
    }
    return waUrl;
}

/**
 * arguments: FormPanel object, service name [optional], operation name
 */
wa.initConfigForm = function () {

    var waUrl = wa.url;
    for (var i = 0; i < arguments.length; i++) {
        if (Ext.isObject(arguments[i])){
            if (!Ext.isEmpty(arguments[i].istService)) {
                waUrl += "/"+arguments[i].istService;
            }
        }else{
            waUrl += "/"+arguments[i];
        }
    }

    arguments[0].waurl = waUrl;

    arguments[0].on("afterlayout",function(cmp, eOpts){
        if (Ext.isEmpty(cmp.mask)) {
            cmp.mask = new Ext.LoadMask(this.body, {
                msg:"Please wait..."
            });
        }
        cmp.mask.show();
    });

    arguments[0].on("afterrender",function(cmp, eOpts){
        Ext.Ajax.request({
            url: cmp.waurl,
            scope: cmp,
            method: 'GET',
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json['message']) {
                    Ext.getCmp('messageField').setVisible(true);
                    json['data']['message']=json['message']
                }
                this.loadRecord(json);
                this.mask.hide();
            }
        });
    //wa.initConfigSubmit(cmp);

    });
}

wa.initConfigSubmit = function (panel){
    Ext.getCmp('configsubmit').on("click",function(){
        if (Ext.isEmpty(this.mask)) {
            this.mask = new Ext.LoadMask(this.body, {
                msg:"Please wait..."
            });
        }
        this.mask.show();
        var json = this.getValues();
        Ext.Ajax.request({
            url: this.waurl,
            scope: this,
            method: 'POST',
            jsonData: json,
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (!json.success && !Ext.isEmpty(json.message)) {
                    Ext.Msg.alert('Warning', json['message']);
                }else if (json.success && !Ext.isEmpty(json.message)) {
                    Ext.getCmp('messageField').setVisible(true);
                    json['data']['message']=json['message']
                }else{
                    Ext.getCmp('messageField').setVisible(false);
                }
                this.loadRecord(json);
                this.mask.hide();
            }
        });
    },panel);
}

/*var head = document.getElementsByTagName("head")[0];
var script = document.createElement("script");
script.type = "text/javascript";
script.src = wa.url+"/user";
head.appendChild(script);*/
