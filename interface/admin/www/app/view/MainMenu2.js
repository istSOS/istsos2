Ext.define('istsos.view.MainMenu2', {
    extend: 'istsos.view.ui.MainMenu2',

    initComponent: function() {
        var me = this;
        this.btnTemplate = new Ext.Template([
            '<div class="submenuIcon">',
            '<img src="images/menu/{icon}" width="46"/>',
            '<div style="padding-top: 4px;">',
            '{name}',
            '</div>',
            '</div>',
            ]);
        this.btnTemplate.compile();

        me.callParent(arguments);


        if (Ext.Array.contains(wa.user.groups, 'viewer') && (
            !Ext.Array.contains(wa.user.groups, 'admin') &&
            !Ext.Array.contains(wa.user.groups, 'datamanager') &&
            !Ext.Array.contains(wa.user.groups, 'networkmanager'))){
          Ext.getCmp("btnService").setVisible(false);
          Ext.getCmp("btnStatus").setVisible(false);
        }

        this.on("afterrender",function(){
            //Ext.getCmp('submenu').expand();
            this.loadServiceMenu();
        });


        // Registering click event on Server/Default button
        Ext.getCmp('menuServer').on("click",function(){

            var mainCenter = Ext.getCmp("mainCenter"), items = [];
            mainCenter.removeAll(true);

            for (var h in istsos.engine.defaultConfig){
                for (var l in istsos.engine.defaultConfig[h]){
                    items.push(this.createSubButton({
                        "name": l,
                        "icon": istsos.engine.defaultConfig[h][l]['icon'],
                        "istConfig": istsos.engine.defaultConfig[h][l]
                    }));
                }
            }

            var sub = Ext.getCmp("submenu");
            sub.removeAll();
            var cmps = sub.add(items);

            var time = 250;

            for (var i = 0; i < cmps.length; i++) {

                var el = cmps[i].getEl();

                el.on("click",function(e, t, eOpts){
                    for (var c = 0; c < cmps.length; c++) {
                        cmps[c].removeCls('submenuSelect');
                    }
                    this.addClass('submenuSelect');

                    var conf = Ext.apply({
                        istService: ((wa.user && 'admin' in wa.user.roles) ? "default": null)
                    },this.istConfig);

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
                    istsos.engine.pageManager.openWaPage(conf);

                },cmps[i]);

                time += 250;
            }
        },this);


        Ext.getCmp('btnObservations').on("click",function(){

            var mainCenter = Ext.getCmp("mainCenter");
            mainCenter.removeAll(true);

            var items = []
            for (var h in istsos.engine.observationConfig){
                for (var l in istsos.engine.observationConfig[h]){
                    items.push(this.createSubButton({
                        "name": l,
                        "icon": istsos.engine.observationConfig[h][l]['icon'],
                        "istConfig": istsos.engine.observationConfig[h][l]
                    }));
                }
            }

            var sub = Ext.getCmp("submenu");
            sub.removeAll();
            if (items.length==1) {
                items[0]['flex']=null;
                items.push({
                    xtype: 'container',
                    id: 'imnotabutton',
                    margin: '4 4 0 4',
                    html: "",
                    flex: 1,
                    style: 'opacity: 0;'
                });
            }
            var cmps = sub.add(items);

            var time = 250;

            for (var i = 0; i < cmps.length; i++) {
                //console.dir(cmps[i]);
                if (cmps[i].getId()!='imnotabutton') {
                    var el = cmps[i].getEl();
                    el.fadeIn({
                        duration: time,
                        easing: null

                    });
                    el.on("click",function(e, t, eOpts){
                        for (var c = 0; c < cmps.length; c++) {
                            cmps[c].removeCls('submenuSelect');
                        }
                        this.addClass('submenuSelect');
                        var conf = Ext.apply({
                            istService: "default"
                        },this.istConfig);
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
                        istsos.engine.pageManager.openWaPage(conf);
                    },cmps[i]);
                    time += 250;
                }
            }
        },this);


        Ext.getCmp('btnStatus').on("click",function(){
            if (this.status && !this.status.closed){
                this.status.focus();
            }else{
                this.status = window.open("../modules/status", 'status', "location=no, menubar=no, status=no");
            }
        },this);

    },
    showMask: function(msg){
        if (!Ext.isEmpty(this.mask)) {
            this.mask.hide();
        }
        this.mask = new Ext.LoadMask(Ext.getCmp('mainCenter').body, {
            msg: msg
        });
        this.mask.show();
    },
    hideMask: function(){
        if (!Ext.isEmpty(this.mask)) {
            this.mask.hide();
        }
    },
    createSubButton: function(conf){
        return {
            xtype: 'container',
            margin: '4 4 0 4',
            html: this.btnTemplate.apply(conf),
            istConfig: conf['istConfig'],
            width: 60,
            flex: 1,
            overCls: 'submenuOver',
            componentCls: 'submenu'
        }
    },
    loadServiceMenu: function(){
        if (Ext.Array.contains(wa.user.groups, 'viewer') && (
            !Ext.Array.contains(wa.user.groups, 'admin') &&
            !Ext.Array.contains(wa.user.groups, 'datamanager') &&
            !Ext.Array.contains(wa.user.groups, 'networkmanager'))){
          Ext.getCmp('menuServer').fireEvent("click");
          istsos.engine.pageManager.openWaPage(istsos.engine.defaultConfig.Server.Status);
          return;
        }
        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services', wa.url),
            scope: this,
            method: 'GET',
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    var menu = Ext.getCmp("menuServices");
                    menu.removeAll();
                    var items = [];
                    for (var i = 0; i < json.total; i++) {
                        items.push({
                            text: json.data[i].service,
                            istConfig: json.data[i],
                            iconCls: 'service_menu'
                        });
                    }
                    var cmp = menu.add(items);
                    for (i = 0; i < cmp.length; i++) {
                        cmp[i].on("click",function(btn, e, eOpts){

                            var mainCenter = Ext.getCmp("mainCenter");
                            mainCenter.removeAll(true);
                            this.loadServiceButtons(btn.istConfig);
                            Ext.getCmp('btnService').toggle(true,true);
                        },this)
                    }
                }else{

                }
            }
        });
        Ext.getCmp('menuServer').fireEvent("click");
        istsos.engine.pageManager.openWaPage(istsos.engine.defaultConfig.Server.Status);
    },
    loadServiceButtons: function(istConfig){

        var mainCenter = Ext.getCmp("mainCenter");
        mainCenter.removeAll(true);

        var items = [];

        for (var h in istsos.engine.serviceConfig){
            for (var l in istsos.engine.serviceConfig[h]){
                items.push(this.createSubButton({
                    "name": l,
                    "icon": istsos.engine.serviceConfig[h][l]['icon'],
                    "istConfig": istsos.engine.serviceConfig[h][l]
                }));
            }
        }

        var sub = Ext.getCmp("submenu");
        sub.removeAll();
        var cmps = sub.add(items);

        var time = 250;

        for (var i = 0; i < cmps.length; i++) {

            var el = cmps[i].getEl();
            el.fadeIn({
                duration: time,
                //easing: 'elasticIn'
                //easing: 'ease'
                //easing: 'easeInOut'
                //easing: 'backIn'
                easing: null
            });

            el.on("click",function(e, t, eOpts){
                for (var c = 0; c < cmps.length; c++) {
                    cmps[c].removeCls('submenuSelect');
                }
                this.addClass('submenuSelect');
                var conf = Ext.apply({
                    istService: istConfig.service
                },this.istConfig);
                var url;
                if (Ext.isObject(conf.istOperation)) {
                    url = conf.istOperation.restUrl;
                    if (url.indexOf("@")>0) {
                        conf.istOperation.restUrl = url.replace("@", istConfig.service);
                    }
                }else if (Ext.isString(conf.istOperation)) {
                    url = conf.istOperation;
                    if (url.indexOf("@")>0) {
                        conf.istOperation = url.replace("@", istConfig.service);
                    }
                }
                istsos.engine.pageManager.openPage(conf);
            },cmps[i]);
            time += 250;

        }
    }
});
