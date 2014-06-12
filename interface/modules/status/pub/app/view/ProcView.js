/*
 * File: app/view/ProcView.js
 *
 * This file was generated by Sencha Architect version 3.0.4.
 * http://www.sencha.com/products/architect/
 *
 * This file requires use of the Ext JS 4.2.x library, under independent license.
 * License of Sencha Architect does not include license for Ext JS 4.2.x. For more
 * details see http://www.sencha.com/license or contact license@sencha.com.
 *
 * This file will be auto-generated each and everytime you save your project.
 *
 * Do NOT hand edit this file.
 */

Ext.define('istsosStatus.view.ProcView', {
    extend: 'Ext.window.Window',

    requires: [
        'Ext.panel.Panel',
        'Ext.form.Label',
        'Ext.form.field.Text'
    ],

    height: 600,
    id: 'ProcView',
    itemId: 'ProcView',
    maxHeight: 600,
    maxWidth: 800,
    minHeight: 600,
    minWidth: 800,
    width: 800,
    modal: true,

    initComponent: function() {
        var me = this;

        Ext.applyIf(me, {
            style: {
                position: 'relative',
                width: '100%',
                height: '100%'
            },
            items: [
                {
                    xtype: 'panel',
                    height: 561,
                    style: {
                        position: 'absolute'
                    },
                    frameHeader: false,
                    header: false,
                    manageHeight: false,
                    title: '',
                    items: [
                        {
                            xtype: 'label',
                            cls: 'labelProc',
                            text: 'Details'
                        },
                        {
                            xtype: 'container',
                            id: 'details',
                            itemId: 'details',
                            items: [
                                {
                                    xtype: 'textfield',
                                    id: 'lastObs',
                                    itemId: 'lastObs',
                                    style: {
                                        width: '100%',
                                        'padding-top': '20px'
                                    },
                                    fieldLabel: 'Last observation',
                                    readOnly: true
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'lastMes',
                                    itemId: 'lastMes',
                                    style: {
                                        width: '100%'
                                    },
                                    fieldLabel: 'Last measure',
                                    readOnly: true
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'op',
                                    itemId: 'op',
                                    style: {
                                        width: '100%'
                                    },
                                    fieldLabel: 'Observed properties',
                                    fieldStyle: 'width:40%',
                                    readOnly: true
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'status',
                                    itemId: 'status',
                                    style: {
                                        width: '100%'
                                    },
                                    fieldLabel: 'Status',
                                    readOnly: true
                                }
                            ]
                        },
                        {
                            xtype: 'label',
                            cls: 'labelProc',
                            id: 'Exception',
                            text: 'Exception'
                        },
                        {
                            xtype: 'container',
                            height: 556,
                            id: 'exception',
                            autoScroll: true
                        },
                        {
                            xtype: 'label',
                            cls: 'labelProc',
                            id: 'labelMap',
                            text: 'Map'
                        },
                        {
                            xtype: 'container',
                            height: 280,
                            id: 'map',
                            itemId: 'map'
                        }
                    ]
                }
            ]
        });

        me.callParent(arguments);
    }

});