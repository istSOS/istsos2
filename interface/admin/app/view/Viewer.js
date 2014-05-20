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

Ext.define('istsos.view.Viewer', {
    extend: 'istsos.view.ui.Viewer',

    initComponent: function() {
        
        var me = this;
        me.callParent(arguments);
        
        Ext.getCmp('pchoose').on("procedureAdded",function(procedure) {
            this.addProcedure(procedure);
        },Ext.getCmp('chartpanel'));
        
        Ext.getCmp('pchoose').on("procedureRemoved",function(procedure) {
            this.removeProcedure(procedure);
        },Ext.getCmp('chartpanel'));
        
        Ext.getCmp('pchoose').on("procedureRemoved",function(procedure) {
            this.removeProcedure(procedure);
        },Ext.getCmp('gridpanel'));
        
        Ext.getCmp('chartpanel').on("queueLoaded",function(chartpanel) {
            this.initReadOnlyGrid(
                chartpanel.procedures,
                Ext.getCmp("oeCbObservedProperty").getValue());
        },Ext.getCmp("gridpanel"));
        
        Ext.getCmp('chartpanel').on("clickCallback",function(panel, e, x, pts) {
            this.updateGridSelection([x]);
            panel.highlightRegion(x);
        },Ext.getCmp('gridpanel'));
        
        /*Ext.getCmp('gridpanel').on("select",function(panel, grid, record, index, eOpts) {
            console.log("select:");
            console.dir(arguments);
        },Ext.getCmp('chartpanel'));*/
        
        Ext.getCmp('gridpanel').on("selectionchange",function(panel, grid, selected, eOpts) {
            
            if (selected.length==1) {
                //this.addAnnotation(selected[0].get('micro'));
                this.highlightRegion(selected[0].get('micro'));
            }else if (selected.length>1) {
                var rec, begin, end;
                rec = selected[0];
                begin = rec.get('micro');
                rec = selected[selected.length-1];
                end = rec.get('micro');
                this.highlightRegion(begin,end);
            }else if (selected.length==0) {
                this.highlightRegion();
                this.removeAnnotations();
            }
        },Ext.getCmp('chartpanel'));
        
        /*Ext.getCmp('chartpanel').on("underlayCallback",function(panel, e, x, pts) {
            console.log("underlayCallback:");
            console.dir(arguments);
        });*/
        
    }
});