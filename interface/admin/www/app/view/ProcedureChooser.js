/**
 * istSOS WebAdmin - Istituto Scienze della Terra
 * Copyright (C) 2013 Massimiliano Cannata, Milan Antonovic
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 */


/*
 * https://github.com/sterlingwes/RandomColor
 */
 /*
(function(root,factory){
    if(typeof exports==='object'){
        module.exports=factory;
    }else if(typeof define==='function'&&define.amd){
        define(factory);
    }else{
        root.RColor=factory();
    }
}(this,function(){
    var RColor=function(){
        this.hue=Math.random(),this.goldenRatio=0.618033988749895;
    };
    RColor.prototype.hsvToRgb=function(h,s,v){
        var h_i=Math.floor(h*6),f=h*6- h_i,p=v*(1-s),q=v*(1-f*s),t=v*(1-(1-f)*s),r=255,g=255,b=255;
        switch(h_i){
            case 0:
                r=v,g=t,b=p;
                break;
            case 1:
                r=q,g=v,b=p;
                break;
            case 2:
                r=p,g=v,b=t;
                break;
            case 3:
                r=p,g=q,b=v;
                break;
            case 4:
                r=t,g=p,b=v;
                break;
            case 5:
                r=v,g=p,b=q;
                break;
        }
        return[Math.floor(r*256),Math.floor(g*256),Math.floor(b*256)];
    };
    RColor.prototype.get=function(hex,saturation,value){
        this.hue+=this.goldenRatio;
        this.hue%=1;
        if(typeof saturation!=="number")saturation=0.5;
        if(typeof value!=="number")value=0.95;
        var rgb=this.hsvToRgb(this.hue,saturation,value);
        if(hex)
            return"#"+rgb[0].toString(16)+rgb[1].toString(16)+rgb[2].toString(16);else
            return rgb;
    };
    return RColor;
}));*/

/*Please JS, Jordan Checkman 2014, Checkman.io, MIT Liscense, Have fun.*/
(function(e){"use strict";function t(){function i(e,t){return Math.floor(Math.random()*(t-e+1))+e}function s(e,t){return Math.random()*(t-e)+e}function o(e,t,n){if(e<t){e=t}else if(e>n){e=n}return e}function u(t,n){switch(t){case"hex":for(var r=0;r<n.length;r++){n[r]=e.HSV_to_HEX(n[r])}break;case"rgb":for(var r=0;r<n.length;r++){n[r]=e.HSV_to_RGB(n[r])}break;case"rgb-string":for(var r=0;r<n.length;r++){var i=e.HSV_to_RGB(n[r]);n[r]="rgb("+i.r+","+i.g+","+i.b+")"}break;case"hsv":break;default:console.log("Format not recognized.");break}return n}function a(e){var t={};for(var n in e){if(e.hasOwnProperty(n)){t[n]=e[n]}}return t}var e={};var t={aliceblue:"F0F8FF",antiquewhite:"FAEBD7",aqua:"00FFFF",aquamarine:"7FFFD4",azure:"F0FFFF",beige:"F5F5DC",bisque:"FFE4C4",black:"000000",blanchedalmond:"FFEBCD",blue:"0000FF",blueviolet:"8A2BE2",brown:"A52A2A",burlywood:"DEB887",cadetblue:"5F9EA0",chartreuse:"7FFF00",chocolate:"D2691E",coral:"FF7F50",cornflowerblue:"6495ED",cornsilk:"FFF8DC",crimson:"DC143C",cyan:"00FFFF",darkblue:"00008B",darkcyan:"008B8B",darkgoldenrod:"B8860B",darkgray:"A9A9A9",darkgrey:"A9A9A9",darkgreen:"006400",darkkhaki:"BDB76B",darkmagenta:"8B008B",darkolivegreen:"556B2F",darkorange:"FF8C00",darkorchid:"9932CC",darkred:"8B0000",darksalmon:"E9967A",darkseagreen:"8FBC8F",darkslateblue:"483D8B",darkslategray:"2F4F4F",darkslategrey:"2F4F4F",darkturquoise:"00CED1",darkviolet:"9400D3",deeppink:"FF1493",deepskyblue:"00BFFF",dimgray:"696969",dimgrey:"696969",dodgerblue:"1E90FF",firebrick:"B22222",floralwhite:"FFFAF0",forestgreen:"228B22",fuchsia:"FF00FF",gainsboro:"DCDCDC",ghostwhite:"F8F8FF",gold:"FFD700",goldenrod:"DAA520",gray:"808080",grey:"808080",green:"008000",greenyellow:"ADFF2F",honeydew:"F0FFF0",hotpink:"FF69B4",indianred:"CD5C5C",indigo:"4B0082",ivory:"FFFFF0",khaki:"F0E68C",lavender:"E6E6FA",lavenderblush:"FFF0F5",lawngreen:"7CFC00",lemonchiffon:"FFFACD",lightblue:"ADD8E6",lightcoral:"F08080",lightcyan:"E0FFFF",lightgoldenrodyellow:"FAFAD2",lightgray:"D3D3D3",lightgrey:"D3D3D3",lightgreen:"90EE90",lightpink:"FFB6C1",lightsalmon:"FFA07A",lightseagreen:"20B2AA",lightskyblue:"87CEFA",lightslategray:"778899",lightslategrey:"778899",lightsteelblue:"B0C4DE",lightyellow:"FFFFE0",lime:"00FF00",limegreen:"32CD32",linen:"FAF0E6",magenta:"FF00FF",maroon:"800000",mediumaquamarine:"66CDAA",mediumblue:"0000CD",mediumorchid:"BA55D3",mediumpurple:"9370D8",mediumseagreen:"3CB371",mediumslateblue:"7B68EE",mediumspringgreen:"00FA9A",mediumturquoise:"48D1CC",mediumvioletred:"C71585",midnightblue:"191970",mintcream:"F5FFFA",mistyrose:"FFE4E1",moccasin:"FFE4B5",navajowhite:"FFDEAD",navy:"000080",oldlace:"FDF5E6",olive:"808000",olivedrab:"6B8E23",orange:"FFA500",orangered:"FF4500",orchid:"DA70D6",palegoldenrod:"EEE8AA",palegreen:"98FB98",paleturquoise:"AFEEEE",palevioletred:"D87093",papayawhip:"FFEFD5",peachpuff:"FFDAB9",peru:"CD853F",pink:"FFC0CB",plum:"DDA0DD",powderblue:"B0E0E6",purple:"800080",rebeccapurple:"663399",red:"FF0000",rosybrown:"BC8F8F",royalblue:"4169E1",saddlebrown:"8B4513",salmon:"FA8072",sandybrown:"F4A460",seagreen:"2E8B57",seashell:"FFF5EE",sienna:"A0522D",silver:"C0C0C0",skyblue:"87CEEB",slateblue:"6A5ACD",slategray:"708090",slategrey:"708090",snow:"FFFAFA",springgreen:"00FF7F",steelblue:"4682B4",tan:"D2B48C",teal:"008080",thistle:"D8BFD8",tomato:"FF6347",turquoise:"40E0D0",violet:"EE82EE",wheat:"F5DEB3",white:"FFFFFF",whitesmoke:"F5F5F5",yellow:"FFFF00",yellowgreen:"9ACD32"};var n={hue:null,saturation:null,value:null,base_color:"",greyscale:false,grayscale:false,golden:true,full_random:false,colors_returned:1,format:"hex"};var r={scheme_type:"analogous",format:"hex"};e.NAME_to_HEX=function(e){if(e in t){return t[e]}else{console.log("Color name not recognized.")}};e.NAME_to_HSV=function(t){return e.HEX_to_RGB(e.NAME_to_HEX(t))};e.NAME_to_HSV=function(t){return e.HEX_to_HSV(e.NAME_to_HEX(t))};e.HEX_to_RGB=function(e){var t=/^#?([a-f\d])([a-f\d])([a-f\d])$/i;e=e.replace(t,function(e,t,n,r){return t+t+n+n+r+r});var n=/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(e);return n?{r:parseInt(n[1],16),g:parseInt(n[2],16),b:parseInt(n[3],16)}:null};e.RGB_to_HEX=function(e){return"#"+((1<<24)+(e.r<<16)+(e.g<<8)+e.b).toString(16).slice(1)};e.HSV_to_RGB=function(e){var t,n,r;var i=e.h/360;var s=e.s;var o=e.v;var u=Math.floor(i*6);var a=i*6-u;var f=o*(1-s);var l=o*(1-a*s);var c=o*(1-(1-a)*s);switch(u%6){case 0:t=o,n=c,r=f;break;case 1:t=l,n=o,r=f;break;case 2:t=f,n=o,r=c;break;case 3:t=f,n=l,r=o;break;case 4:t=c,n=f,r=o;break;case 5:t=o,n=f,r=l;break}return{r:Math.floor(t*255),g:Math.floor(n*255),b:Math.floor(r*255)}};e.RGB_to_HSV=function(e){var t,n,r;var i=0;var s=0;var o=0;t=e.r/255;n=e.g/255;r=e.b/255;var u=Math.min(t,Math.min(n,r));var a=Math.max(t,Math.max(n,r));if(u==a){o=u;return{h:0,s:0,v:o}}var f=t==u?n-r:r==u?t-n:r-t;var l=t==u?3:r==u?1:5;i=60*(l-f/(a-u));s=(a-u)/a;o=a;return{h:i,s:s,v:o}};e.HSV_to_HEX=function(t){return e.RGB_to_HEX(e.HSV_to_RGB(t))};e.HEX_to_HSV=function(t){return e.RGB_to_HSV(e.HEX_to_RGB(t))};e.make_scheme=function(e,t){function f(e){return{h:e.h,s:e.s,v:e.v}}var n=a(r);if(t!=null){for(var i in t){if(t.hasOwnProperty(i)){n[i]=t[i]}}}var s=[e];switch(n.scheme_type.toLowerCase()){case"monochromatic":case"mono":for(var l=1;l<=2;l++){var c=f(e);var h=c.s+.1*l;h=o(h,0,1);var p=c.v+.1*l;p=o(p,0,1);c.s=h;c.v=p;s.push(c)}for(var l=1;l<2;l++){var c=f(e);var h=c.s-.1*l;h=o(h,0,1);var p=c.v-.1*l;p=o(p,0,1);c.s=h;c.v=p;s.push(c)}break;case"complementary":case"complement":var c=f(e);c.h+=180;if(c.h>360){c.h-=360}s.push(c);break;case"split-complementary":case"split-complement":case"split":var c=f(e);c.h+=165;if(c.h>360){c.h-=360}s.push(c);var c=f(e);c.h-=165;if(c.h<0){c.h+=360}s.push(c);break;case"double-complementary":case"double-complement":case"double":var c=f(e);c.h+=180;if(c.h>360){c.h-=360}s.push(c);var c=f(e);c.h+=30;if(c.h>360){c.h-=360}var d=f(c);s.push(c);d.h+=180;if(d.h>360){d.h-=360}s.push(d);break;case"analogous":case"ana":for(var l=1;l<=5;l++){var c=f(e);c.h+=20*l;if(c.h>360){c.h-=360}s.push(c)}break;case"triadic":case"triad":case"tri":for(var l=1;l<3;l++){var c=f(e);c.h+=120*l;if(c.h>360){c.h-=360}s.push(c)}break;default:console.log("Color scheme not recognized.");break}u(n.format.toLowerCase(),s);return s};e.make_color=function(r){var a=[];var f={};for(var l in n){if(n.hasOwnProperty(l)){f[l]=n[l]}}if(r!=null){for(var l in r){if(r.hasOwnProperty(l)){f[l]=r[l]}}}var c;if(f.base_color.length>0){c=t[f.base_color.toLowerCase()];c=e.HEX_to_HSV(c)}for(var h=0;h<f.colors_returned;h++){var p=i(0,360);var d,v,m;if(c!=null){d=i(c.h-5,c.h+5);v=s(.4,.85);m=s(.4,.85);a.push({h:d,s:v,v:m})}else{if(f.greyscale==true||f.grayscale==true){d=0}else if(f.golden==true){d=p+p/.618033988749895}else if(f.hue==null||f.full_random==true){d=p}else{d=o(f.hue,0,360)}if(f.greyscale==true||f.grayscale==true){v=0}else if(f.full_random==true){v=s(0,1)}else if(f.saturation==null){v=.4}else{v=o(f.saturation,0,1)}if(f.full_random==true){m=s(0,1)}else if(f.greyscale==true||f.grayscale==true){m=s(.15,.75)}else if(f.value==null){m=.75}else{m=o(f.value,0,1)}a.push({h:d,s:v,v:m})}}u(f.format.toLowerCase(),a);if(a.length===1){return a[0]}else{return a}};return e}if(typeof Please=="undefined"){e.Please=t()}})(window)

Ext.define('istsos.view.ProcedureChooser', {
    extend: 'istsos.view.ui.ProcedureChooser',
    alias: 'widget.procedurechooser',

    initComponent: function() {

        var me = this;
        //this.color = new RColor;

        this.addEvents({
            "procedureAdded" : true,
            "procedureRemoved" : true,
            "serviceSelected" : true,
            "offeringSelected" : true,
            "procedureSelected" : true
        });

        Ext.create('istsos.store.Offerings');
        Ext.create('istsos.store.gridProceduresList');
        var ssrv = Ext.create('istsos.store.Services');
        ssrv.getProxy().url = Ext.String.format('{0}/istsos/services',wa.url);

        this.procedures = {};
        this.configsections = {};

        me.callParent(arguments);

        Ext.getCmp("wResetObservedProperties").on("click", function(){
          this._offeringSelected(Ext.getCmp('oeCbOffering'));
        },this);

        Ext.getCmp("cmbServices").on("select",this._serviceSelected,this);

        Ext.getCmp("oeCbOffering").on("select",this._offeringSelected,this);

        Ext.getCmp("oeCbProcedure").on("select",function(combo, records, eOpts){
          this.fireEvent("procedureSelected", combo.getValue());
        },this);

        Ext.getCmp("btnAdd").on("click",function(btn, e, eOpts){
            this._addProcedure(
              Ext.getCmp("cmbServices").getValue(),
              Ext.getCmp("oeCbOffering").getValue(),
              Ext.getCmp("oeCbProcedure").getValue()
            );
        },this);
    },
    _addProcedure: function(service, offering, procedure){
      // Add an istsos.Procedure in the this.procedures array
      // every row contains some describeSensor data
      this.procedures[procedure] = Ext.create('istsos.Sensor',
        service, offering, procedure, {
            listeners: {
                metadataLoaded: this._getProcedureDetails,
                scope: this
            }
        });
    },
    _getProcedureDetails: function(proc){
        var obsprop = [];
        for (var i = 0; i < proc.meta.outputs.length; i++) {
            if (proc.meta.outputs[i]['definition']!=proc.isodef) {
                obsprop.push(proc.meta.outputs[i]['name'] + " (" + proc.meta.outputs[i]['uom']+ ")");
            }
        }
        var anaColor = Please.make_scheme(
            Please.make_color({format: "hsv"}),
            {
                scheme_type: "ana",
                format: "rgb-string"
            }
        );
        proc.color = anaColor[0]; //this.color.get(true);
        proc.color2 = anaColor[3]; //this.color.get(true);
        var idVisible = Ext.id(), idColor = Ext.id(), idColor2 = Ext.id(), idRemove = Ext.id(),
                        idBtnAggregation = Ext.id(), idAggregation = Ext.id(), idToggleAggregation = Ext.id(),
                        idDetailsAggregation = Ext.id(), idBtnAggregationReset = Ext.id(), idDownload = Ext.id(),
                        idBtnAggregationAll = Ext.id();

        var cmp = Ext.getCmp('proceduresTree').add({
            xtype: 'panel',
            //id: 'fs-'+proc.getName(),
            border: false,
            istsos: {
                procedure: proc,
                idVisible: idVisible,
                idColor: idColor,
                idColor2: idColor2,
                idRemove: idRemove,
                chooser: this,
                idToggleAggregation: idToggleAggregation,
                toggleAggregation: false,
                idAggregation: idAggregation,
                idBtnAggregation: idBtnAggregation,
                idBtnAggregationAll: idBtnAggregationAll,
                idBtnAggregationReset: idBtnAggregationReset,
                idDetailsAggregation: idDetailsAggregation,
                idDownload: idDownload
            },
            listeners: {
                "added": {
                    fn: function(panel, container, pos, eOpts){
                        this.fireEvent("procedureAdded", proc);
                    },
                    scope: this,
                    options: {
                        single: true
                    }
                },
                "afterrender": {
                    fn: function(procedureDetailsPanel, layout, eOpts ){

                        //console.log("Afterrender: " + procedureDetailsPanel.istsos.procedure.getName());

                        var v = Ext.get(procedureDetailsPanel.istsos.idVisible);
                        v.on("click",function(){
                            if (this.istsos.procedure.getVisibility()) {
                                Ext.get(this.istsos.idVisible).addCls("pchooserBtnNotVisible");
                            }else{
                                Ext.get(this.istsos.idVisible).removeCls("pchooserBtnNotVisible");
                            }
                            this.istsos.procedure.setVisibility(!this.istsos.procedure.getVisibility());
                        },procedureDetailsPanel);

                        var c = Ext.get(procedureDetailsPanel.istsos.idDownload);
                        c.on("click",function(){
                            var from = Ext.getCmp('oeBegin').getValue();
                            var bt = Ext.getCmp('oeBeginTime').getValue();
                            from.setHours(bt.getHours());
                            from.setMinutes(bt.getMinutes());

                            var to = Ext.getCmp('oeEnd').getValue();
                            var et = Ext.getCmp('oeEndTime').getValue();
                            to.setHours(et.getHours());
                            to.setMinutes(et.getMinutes());

                            var attachment = this.istsos.procedure.getName()+ "_" + Ext.Date.format(to, 'YmdHi') + "00000.csv";

                            var ob = this.istsos.procedure.getObservedProperties();

                            var tz = Ext.getCmp('oeTZ').getValue();
                            var format = Ext.isEmpty(tz) ? "c": "Y-m-d\\TH:i:s";

                            from = Ext.Date.format(from,format);
                            if(!Ext.isEmpty(tz)){
                                from = from + (Ext.isString(tz) ? tz: istsos.utils.minutesToTz(tz));
                            }

                            to = Ext.Date.format(to,format);
                            if(!Ext.isEmpty(tz)){
                                to = to + (Ext.isString(tz) ? tz: istsos.utils.minutesToTz(tz));
                            }

                            var params = {
                                "request": "GetObservation",
                                "attachment": attachment,
                                "offering": this.istsos.procedure.offering,
                                "procedure": this.istsos.procedure.getName(),
                                "eventTime": from+"/"+to,
                                "observedProperty": ob.join(','),
                                "qualityIndex": "True",
                                "responseFormat": "text/plain",
                                "service": "SOS",
                                "version": "1.0.0"
                            };

                            if (Ext.isObject(this.istsos.procedure.aggregation)){
                                params = Ext.apply(params, {
                                    aggregatefunction: this.istsos.procedure.aggregation.f,
                                    aggregateinterval: this.istsos.procedure.aggregation.i,
                                    aggregatenodata: this.istsos.procedure.aggregation.nd,
                                    aggregatenodataqi: this.istsos.procedure.aggregation.ndqi
                                });
                            }
                            params = Ext.Object.toQueryString(params);

                            window.open(Ext.String.format('{0}{1}?{2}', wa.basepath, this.istsos.procedure.service, params));

                            //console.log(params);


                        },procedureDetailsPanel);

                        c = Ext.get(procedureDetailsPanel.istsos.idColor);
                        c.on("click",function(){
                            Ext.create('Ext.window.Window', {
                                title: this.istsos.procedure.getName() + ': primary color',
                                height: 110,
                                width: 200,
                                closeAction: 'destroy',
                                modal: true,
                                layout: 'fit',
                                items: Ext.create('Ext.picker.Color', {
                                    listeners: {
                                        select: function(picker, selColor) {
                                            this.istsos.procedure.setColor("#"+selColor);
                                            Ext.get(this.istsos.idColor).setStyle("background-color", "#"+selColor);
                                            picker.ownerCt.close();
                                        },
                                        scope: this
                                    }
                                })
                            }).show();
                        },procedureDetailsPanel);

                        c = Ext.get(procedureDetailsPanel.istsos.idColor2);
                        c.on("click",function(){
                            Ext.create('Ext.window.Window', {
                                title: this.istsos.procedure.getName() + ': secondary color',
                                height: 110,
                                width: 200,
                                closeAction: 'destroy',
                                modal: true,
                                layout: 'fit',
                                items: Ext.create('Ext.picker.Color', {
                                    listeners: {
                                        select: function(picker, selColor) {
                                            this.istsos.procedure.setColor2("#"+selColor);
                                            Ext.get(this.istsos.idColor2).setStyle("background-color", "#"+selColor);
                                            picker.ownerCt.close();
                                        },
                                        scope: this
                                    }
                                })
                            }).show();
                        },procedureDetailsPanel);


                        c = Ext.get(procedureDetailsPanel.istsos.idRemove);
                        c.on("click",function(){
                            var pchoose = this.ownerCt.ownerCt;
                            this.ownerCt.remove(this);
                            pchoose.fireEvent("procedureRemoved", proc);
                        },procedureDetailsPanel,{
                            single: true
                        });


                        // AGGREGATION FUNCTIONALITIES <<<<<<<<<<<<<<<<<<<<<<<<<

                        procedureDetailsPanel.istsos.procedure.on('aggregationchanged',function(procedure, aggregation){
                            var det = Ext.get(this.istsos.idDetailsAggregation);
                            if (Ext.isObject(aggregation)){
                                det.update(aggregation.f + ", " + aggregation.i + ", " + aggregation.nd + ", " + aggregation.ndqi );
                            }else{
                                det.update("no");
                            }
                            this.istsos.toggleAggregation = false;
                            Ext.getCmp(this.istsos.idAggregation).setVisible( this.istsos.toggleAggregation);
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            form.form.setValues(aggregation);
                        },procedureDetailsPanel);

                        c = Ext.get(procedureDetailsPanel.istsos.idToggleAggregation);
                        c.on("click",function(){
                            this.istsos.toggleAggregation = !this.istsos.toggleAggregation;
                            Ext.getCmp(this.istsos.idAggregation).setVisible( this.istsos.toggleAggregation );
                        },procedureDetailsPanel);

                        c = Ext.getCmp(procedureDetailsPanel.istsos.idBtnAggregation);
                        c.on('click',function(btn){
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            var values = form.getValues();
                            this.istsos.procedure.setAggregation(values);
                        },procedureDetailsPanel);

                        c = Ext.getCmp(procedureDetailsPanel.istsos.idBtnAggregationAll); // APPLY TO ALL
                        c.on('click',function(btn){
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            var values = form.getValues();
                            for ( var k in this.istsos.chooser.procedures) {
                              this.istsos.chooser.procedures[k].setAggregation(values);
                            }
                        },procedureDetailsPanel);

                        c = Ext.getCmp(procedureDetailsPanel.istsos.idBtnAggregationReset);
                        c.on('click',function(btn){
                            var form = Ext.getCmp(this.istsos.idAggregation);
                            form.getForm().reset();
                            this.istsos.procedure.setAggregation(null);
                        },procedureDetailsPanel);
                    },
                    scope: this,
                    options: {
                        single: true
                    }
                }
            },
            cls: 'pchooser',
            items: [
                {
                    xtype: 'panel',
                    border: false,
                    html:
                        "<div>" +
                        "   <div style='border-bottom: thin solid white; padding: 2px; background-color: green; color: white; text-align: center;'>" +
                        "       <span style='font-weight: bold; font-size: 14px;'>" + proc.getName() + "</span>" +
                        "       <div id='"+idVisible+"' class='pchooserBtnVisible' title='Hide this procedure'></div>" +
                        "       <div id='"+idDownload+"' class='pchooserBtnDownload' title='Download CSV data of selected interval'>&nbsp;</div>" +
                        "       <div id='"+idColor+"' class='pchooserBtnColor' style='background-color: "+proc.color+";' title='Choose color primary observed property'></div>" +
                        "       <div id='"+idColor2+"' class='pchooserBtnColor2' style='background-color: "+proc.color2+";' title='Choose color secondary observed property'></div>" +
                        "       <div id='"+idRemove+"' class='pchooserBtnRemove' title='Remove this procedure'>&nbsp;</div>" +
                        "   </div>" +
                        "   <div style='font-size: 12px; border-bottom: thin solid green; padding: 2px; background-color: white; color: black; text-align: center;'>" +
                        "       <span style='font-style: italic;'>" + proc.service + ":" + proc.offering + "</span><br/>" +
                        "       <span>Fr:" + proc.getBeginPosition() + "</span><br/>" +
                        "       <span>To:" + proc.getEndPosition() + "</span><br/>" +
                        "       <span style='font-weight: bold;'>" + obsprop.join("<br>") + "</span>" +
                        "   </div>" +
                        "   <div style='font-size: 12px; border-bottom: thin solid green; padding: 2px; background-color: white; color: black; text-align: center;'>" +
                        "       <span id='"+idToggleAggregation+"' style='color: green; cursor: pointer;'>Aggregation: </span>" +
                        "       <span id='"+idDetailsAggregation+"'>no</span>" +
                        "   </div>" +
                        "</div>"
                },
                {
                    xtype: 'form',
                    border: false,
                    hidden: true,
                    id: idAggregation,
                    /*collapsible: true,
                    collapsed: true,
                    hideCollapseTool: true,
                    titleCollapse: true,*/
                    padding: 8,
                    items: [
                        {
                            xtype: 'combobox',
                            //id: 'oeFunction',
                            name: 'f',
                            fieldLabel: 'Function',
                            displayField: 'name',
                            forceSelection: true,
                            queryMode: 'local',
                            store: 'aggregatefunctionstore',
                            valueField: 'name',
                            anchor: '100%'
                        },
                        {
                            xtype: 'textfield',
                            fieldLabel: 'Interval',
                            name: 'i',
                            emptyText: 'PT10M, P1DT',
                            anchor: '100%'
                        },
                        {
                            xtype: 'textfield',
                            value: this.configsections.getobservation.aggregatenodata,
                            name: 'nd',
                            fieldLabel: 'No Data Value',
                            anchor: '100%'
                        },
                        {
                            xtype: 'textfield',
                            value: this.configsections.getobservation.aggregatenodataqi,
                            name: 'ndqi',
                            fieldLabel: 'No Data QI',
                            anchor: '100%'
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: 'toolbar',
                            dock: 'bottom',
                            layout: {
                                align: 'middle',
                                pack: 'center',
                                type: 'hbox'
                            },
                            items: [
                                {
                                    id: idBtnAggregationAll,
                                    xtype: 'button',
                                    text: 'Apply to all'
                                },
                                {
                                    id: idBtnAggregation,
                                    xtype: 'button',
                                    text: 'Apply'
                                },
                                {
                                    id: idBtnAggregationReset,
                                    xtype: 'button',
                                    text: 'Reset'
                                }
                            ]
                        }
                    ]
                }
            ]

        });


    },
    _serviceSelected: function(combo, records, eOpts){
        var pr = Ext.getCmp('oeCbProcedure');
        pr.reset();
        pr.disable();

        var o = Ext.getCmp('oeCbOffering');
        o.reset();
        o.getStore().removeAll();
        o.disable();

        this.fireEvent("serviceSelected", combo.getValue());

        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/offerings/operations/getlist',
                wa.url,combo.getValue()),
            scope: this,
            method: "GET",
            success: function(response){
                var o = Ext.getCmp('oeCbOffering');
                var json = Ext.decode(response.responseText);
                if (json.data.length>0) {
                    o.getStore().loadData(json.data);
                    o.enable();
                    if(json.data.length==1){
                      o.select(o.getStore().getAt(0));
                      this._offeringSelected(Ext.getCmp('oeCbOffering'));
                    }
                }else{
                    o.disable();
                    Ext.Msg.alert("Server message", "\"" + json['message'] + "\"<br/><br/>" +
                            "<small>Status response: " + response.statusText + "</small>");
                }
            }
        });

        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/configsections',wa.url, combo.getValue()),
            scope: this,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.success) {
                    this.configsections = json.data;
                }
            }
        });

    },
    _offeringSelected: function(combo, records, eOpts){
        var pr = Ext.getCmp('oeCbProcedure');
        pr.reset();
        pr.getStore().removeAll();
        pr.disable();

        this.fireEvent("offeringSelected", combo.getValue());

        Ext.Ajax.request({
            url: Ext.String.format('{0}/istsos/services/{1}/offerings/{2}/procedures/operations/memberslist',
                wa.url,Ext.getCmp('cmbServices').getValue(),combo.getValue()),
            scope: pr,
            method: "GET",
            success: function(response){
                var json = Ext.decode(response.responseText);
                if (json.data.length>0) {
                    this.getStore().loadData(json.data);
                    this.enable();
                    if(json.data.length==1){
                      this.select(this.getStore().getAt(0));
                    }
                }else{
                    this.disable();
                    Ext.Msg.alert("Server message", "\"" + json['message'] + "\"<br/><br/>" +
                            "<small>Status response: " + response.statusText + "</small>");
                }
            }
        });
    }
});
