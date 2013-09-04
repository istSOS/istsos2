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

Ext.define('istsos.view.ProcedurePlotter', {
    extend: 'istsos.view.ui.ProcedurePlotter',
    alias: 'widget.procedureplotter',

    initComponent: function() {
        var me = this;
        
        Ext.create('istsos.store.ObservedProperties');
        
        me.callParent(arguments);
        
        var offset = (new Date()).getTimezoneOffset()/-60;
        var tz = ((offset > 0) ? "+"+pad(offset) : pad(offset));
        Ext.getCmp('oeBeginTime').format = 'H:i ['+tz+']';
        Ext.getCmp('oeBeginTime').setValue(Ext.Date.parse("00:00", 'H:i'));
        Ext.getCmp('oeEndTime').format = 'H:i ['+tz+']';
        Ext.getCmp('oeEndTime').setValue(Ext.Date.parse("00:00", 'H:i'));
        
    }
});
