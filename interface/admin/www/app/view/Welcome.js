Ext.define('istsos.view.Welcome', {
    extend: 'istsos.view.ui.Welcome',
    initComponent: function() {
        var me = this;
        me.callParent(arguments);

        Ext.getCmp('btnLogin').on('click', function(){

          Ext.getCmp('loginCard').setLoading(true);

          Ext.Ajax.request({
            method: 'GET',
            url: "../wa/istsos/services/default/configsections/provider",
            success: function(response){

              var json = Ext.decode(response.responseText);
              var provider = json.data;

              Ext.Ajax.request({
                method: 'GET',
                url: "../wa/user",
                params: {
                  json: true
                },
                success: function(response){

                  json = Ext.decode(response.responseText);
                  wa.user = json.data;

                  // Loading external libs
                  var head = document.getElementsByTagName("head")[0];

                  script = document.createElement("script");
                  script.type = "text/javascript";
                  script.src = "ol/ol-debug.js";
                  head.appendChild(script);

                  var link = document.createElement("link");
                  link.rel = "stylesheet";
                  link.type = "text/css";
                  link.src = "ol/ol.css";
                  head.appendChild(link);

                  if (!Ext.Array.contains(wa.user.groups, 'admin')){

                    istsos.engine.defaultConfig = {
                        "Server": {
                            "About istSOS": {
                                istTitle: "About istSOS",
                                icon: 'about_grey.svg',
                                istBody: ["istsos.view.about"],
                                istFunction: {
                                    onLoad: "operationLoad"
                                },
                                istOperation: wa.url + "/istsos/operations/about",
                                istFooter: istsos.EMPTY
                            },
                            "Status": {
                                istTitle: "Server Status",
                                istDefault: "defaultPage",
                                icon: 'status_1.svg',
                                istDescription: "Summary of istSOS instances and run-time status",
                                istBody: ["istsos.view.status"],
                                istFunction: {
                                    onLoad: "operationLoad"
                                },
                                istFooter: istsos.EMPTY
                            }
                        }
                    };


                    if(!Ext.Array.contains(wa.user.groups, 'networkmanager')){

                      istsos.engine.serviceConfig["Service Settings"] = {};

                      if(Ext.Array.contains(wa.user.groups, 'datamanager')){
                        istsos.engine.serviceConfig["Wizards"]={
                          "Water Discharge": {
                            istTitle: "Water Discharge parameters editor",
                            icon: 'virtual.svg',
                            istBody: ["istsos.view.VirtualDischargeEditor"],
                            wapage: 'MainCenter',
                            istFooter: istsos.EMPTY
                          }
                        };
                        /*delete istsos.engine.serviceConfig["Wizards"]["Offerings"];
                        delete istsos.engine.serviceConfig["Wizards"]["Procedures"];
                        delete istsos.engine.serviceConfig["Wizards"]["Virtual Procedures"];
                        delete istsos.engine.serviceConfig["Wizards"]["New procedure"];
                        delete istsos.engine.serviceConfig["Wizards"]["Observed properties"];
                        delete istsos.engine.serviceConfig["Wizards"]["Units of measures"];
                        delete istsos.engine.serviceConfig["Wizards"]["Data quality"];
                        istsos.engine.serviceConfig["Wizards"]["Water Discharge"] = {
                            istTitle: "Water Discharge parameters editor",
                            icon: 'virtual.svg',
                            istBody: ["istsos.view.VirtualDischargeEditor"],
                            wapage: 'MainCenter',
                            istFooter: istsos.EMPTY
                        };*/

                      }else if(Ext.Array.contains(wa.user.groups, 'viewer')){
                        istsos.engine.serviceConfig["Wizards"] = {};
                        delete istsos.engine.observationConfig["Services"]["Data Editor"];
                      }
                    }

                  }

                  Ext.getCmp('loginCard').setLoading(false);

                  var cc = Ext.getCmp('contentcards')
                  cc.add(new istsos.view.MainMenu2());
                  cc.getLayout().setActiveItem(1);

                }
              });

            },
            failure: function(response, opts) {
                Ext.getCmp('loginCard').setLoading(false);
                Ext.getCmp('loginFailed').show();
                console.log('server-side failure with status code ' + response.status);
            }
          });
        });
    }
});
