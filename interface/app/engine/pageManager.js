Ext.ns("istsos","istsos.engine","istsos.engine.pageManager");

// Create the default configuration menu in html
istsos.engine.pageManager.getMenuHtml = function(){
    var htmlMenu = "";
    for (var h in istsos.engine.defaultConfig){
        htmlMenu += "<div class='menuHead'>"+h+"</div>";
        for (var l in istsos.engine.defaultConfig[h]){
            htmlMenu += "<div class='menuLink' id='menuLink_"+ l + 
            "' onClick='istsos.engine.pageManager.menuClick(\"menuLink_"+l+"\",\"default\");'>"+l+"</div>";
        }
        htmlMenu += "<br>";
    }
    return htmlMenu;
}

// Create the items representing the services menu
istsos.engine.pageManager.getServicesMenu = function(serviceJson){
    var ret = [];
    for (var i = 0; i < serviceJson.total; i++) {
        var data = serviceJson.data[i];
        var htmlMenu = "";
        for (var h in istsos.engine.serviceConfig){
            htmlMenu += "<div class='menuHead'>"+h+"</div>";
            for (var l in istsos.engine.serviceConfig[h]){
                htmlMenu += "<div class='menuLink' id='menuLink_"+l+"' onClick='istsos.engine.pageManager.menuClick(\"menuLink_"+l+"\",\""+data.service+"\");'>"+l+"</div>";
            }
            htmlMenu += "<br>";
        }
        ret.push(Ext.create('Ext.Panel', {
            title: data.service,
            html: htmlMenu,
            bodyPadding: "6px"
        }));
    }
    return ret;
}

// Menu styling
istsos.engine.pageManager.resetMenuHtml = function(){
    // Reset style on other menu links
    for (var h in istsos.engine.defaultConfig){
        for (var l in istsos.engine.defaultConfig[h]){
            var el = Ext.get("menuLink_"+l);
            el.setStyle("color", "green");
        }
    }
}

istsos.engine.pageManager.getMenuConfig = function(menuLink, config) {
    for (var h in config){
        for (var l in config[h]){
            if ("menuLink_"+l == menuLink) {
                return config[h][l];
            }
        }
    }
    throw "Menu configuration object not found: " + menuLink;
}

istsos.engine.pageManager.getWizardConfig = function(wizardName) {
    if (!Ext.isEmpty(istsos.engine.pageWizard[wizardName])) {
        return istsos.engine.pageWizard[wizardName];
    }
    throw "Wizard configuration object not found: " + wizardName;
}

istsos.engine.pageManager.menuClick = function (menuLinkId, istService){
    var conf = null;
    if (istService != undefined) {
        if (istService=="default") {
            conf = Ext.apply({},istsos.engine.pageManager.getMenuConfig(
                menuLinkId, istsos.engine.defaultConfig));
        } else {
            conf = Ext.apply({},istsos.engine.pageManager.getMenuConfig(
                menuLinkId, istsos.engine.serviceConfig));
        }
        var url;
        if (Ext.isObject(conf.istOperation)) {
            url = conf.istOperation.restUrl;
            if (url.indexOf("@")>0) {
                conf.istOperation.restUrl = url.replace("@", istService);
            }
        }else if (Ext.isString(conf.istOperation)) {
            url = conf.istOperation;
            if (url.indexOf("@")>0) {
                conf.istOperation = url.replace("@", istService);
            }
        }
        Ext.apply(conf,{
            istService: istService
        });
    }
    istsos.engine.pageManager.openPage(conf);
}

istsos.engine.pageManager.openPage = function (conf){
    // Loading page content
    var mainCenter = Ext.getCmp("mainCenter");
    mainCenter.removeAll(true);
    try{
        var page;
        if (!Ext.isEmpty(conf['wapage']) && conf['wapage'] == 'MainCenter') {
            page = Ext.create(conf.istBody[0],Ext.apply({
                flex: 1 //,padding: 16
            },conf)); 
        }else{
            page = Ext.create('istsos.view.ui.CenterPage',Ext.apply({},conf));
        }
        //var page = Ext.create('istsos.view.ui.CenterPage',Ext.apply({},conf));
        mainCenter.add(page);
    }catch(e){
        console.error(e);
        alert("Page does not exist ["+e+"]");
        return;
    }
};
istsos.engine.pageManager.openWaPage = function (conf){
    var mainCenter = Ext.getCmp("mainCenter");
    mainCenter.removeAll(true);
    try{
        var page = null;
        if (Ext.isEmpty(conf['wapage']) || conf['wapage'] == "CenterPage" ) {
            page = Ext.create('istsos.view.ui.CenterPage',Ext.apply({},conf));
        } else if (conf['wapage'] == 'WizardPage') {
            page = Ext.create('istsos.view.ui.WizardPage',{
                istConfig: istsos.engine.pageManager.getWizardConfig(conf['wizardName']) 
            },{
                istWizard: conf['wizardName'],
                istService: conf['istService']
            });
        } else if (conf['wapage'] == 'MainCenter') {
            if(Ext.isArray(conf.istBody)){
                if(conf.istBody.length==1){
                    page = Ext.create(conf.istBody[0],{
                        flex: 1 //,padding: 16
                    });  
                }
            }
        } else{
            return;
        }
        mainCenter.add(page);
    }catch(e){
        console.error(e);
        alert("Page does not exist ["+e+"]");
        return;
    }
};

istsos.engine.pageManager.openWizard = function(wizardName, istService){
    var mainCenter = Ext.getCmp("mainCenter");
    mainCenter.removeAll(true);
    try{
        var conf = null;
        var page = null;
        if (istService != undefined) {
            page = Ext.create('istsos.view.ui.WizardPage',{
                istConfig: istsos.engine.pageManager.getWizardConfig(wizardName) 
            },{
                istWizard: wizardName,
                istService: istService
            });
        } else {
            page = Ext.create('istsos.view.ui.WizardPage',{
                istWizard: wizardName,
                istConfig: istsos.engine.pageManager.getWizardConfig(wizardName) 
            });
        }
        mainCenter.add(page);
    }catch(e){
        console.error(e);
        alert("Page does not exist ["+e+"]");
        return;
    }
};


istsos.engine.pageManager.initConfigForm = function (panel) {
    
    var waUrl = wa.url;
    if (!Ext.isEmpty(panel.istService)) {
        waUrl += "/"+panel.istService;
    }
    waUrl += "/"+panel.istOperation;
    panel.waurl = waUrl;
    
    panel.on("afterrender",function(cmp, eOpts){
        
        if (Ext.isEmpty(cmp.mask)) {
            cmp.mask = new Ext.LoadMask(this.body, {
                msg:"Please wait..."
            });
        }
        cmp.mask.show();
        
        Ext.Ajax.request({
            url: cmp.waurl,
            scope: cmp,
            method: 'GET',
            success: function(response){
                try {
                    var json = Ext.decode(response.responseText);
                    if (json['message']) {
                        Ext.getCmp('messageField').setVisible(true);
                        json['data']['message']=json['message']
                    }
                    this.loadRecord(json);
                } catch (exception) {
                    console.error(exception);
                }
                this.mask.hide();
            }
        });
        
    });
};
