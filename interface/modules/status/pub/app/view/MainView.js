/*
 * File: app/view/MainView.js
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

Ext.define('istsosStatus.view.MainView', {
    extend: 'Ext.container.Viewport',

    requires: [
        'Ext.panel.Panel',
        'Ext.form.field.ComboBox',
        'Ext.form.field.Number',
        'Ext.button.Button',
        'Ext.form.Label',
        'Ext.form.RadioGroup',
        'Ext.form.field.Radio'
    ],

    id: 'mainView',
    itemId: 'mainView',
    layout: 'border',

    initComponent: function() {
        var me = this;

        Ext.applyIf(me, {
            items: [
                {
                    xtype: 'panel',
                    region: 'north',
                    split: false,
                    height: 150,
                    id: 'header',
                    itemId: 'headerPanel',
                    bodyBorder: false,
                    header: {
                        xtype: 'container',
                        html: '<div class=\'mainHeaderTitle\'><a  href=\'http://istgeo.ist.supsi.ch/software/istsos/\' target=\'_BLANK\'><img height=28 src=\'images/istsos-logo.png\'/></a></div>'
                    },
                    overlapHeader: false,
                    title: ' ',
                    titleAlign: 'right',
                    items: [
                        {
                            xtype: 'container',
                            listeners: {
                                render: function(c){
                                    c.getEl().on('click',function(){this.fireEvent('click',c);},c);
                                }
                            },
                            disabledCls: 'submenu',
                            id: 'submenu',
                            overCls: 'submenuOver',
                            style: {
                                position: 'absolute',
                                width: '150px',
                                left: 0,
                                top: 0,
                                'border-color': 'green',
                                'background-color': 'rgba(0,0,0,0)',
                                height: '100px'
                            },
                            width: 207,
                            items: [
                                {
                                    xtype: 'container',
                                    cls: 'submenuIcon',
                                    html: '<img src="images/status_1.svg" width="46"> <div style="padding-top:4px;"> request status</div>',
                                    style: {
                                        height: '93px',
                                        'padding-left': '8px',
                                        'padding-top': '8px'
                                    }
                                }
                            ]
                        },
                        {
                            xtype: 'container',
                            style: {
                                position: 'absolute',
                                left: '208px',
                                'background-color': 'rgba(0,0,0,0)',
                                width: '350px',
                                height: '100px',
                                top: '0',
                                'padding-top': '10px'
                            },
                            items: [
                                {
                                    xtype: 'combobox',
                                    id: 'serviceSelector',
                                    itemId: 'service',
                                    style: {
                                        'padding-left': '10px'
                                    },
                                    fieldLabel: 'Service',
                                    displayField: 'service',
                                    queryCaching: false,
                                    store: 'storeServices',
                                    valueField: 'service'
                                }
                            ]
                        },
                        {
                            xtype: 'container',
                            style: {
                                position: 'absolute',
                                top: 0,
                                width: '300px',
                                left: '558px',
                                height: '100px',
                                'padding-top': '10px'
                            },
                            items: [
                                {
                                    xtype: 'numberfield',
                                    id: 'refreshRate',
                                    style: {
                                        'padding-left': '10px'
                                    },
                                    fieldLabel: 'Refresh rate',
                                    minValue: 0
                                },
                                {
                                    xtype: 'combobox',
                                    id: 'uomSelector',
                                    fieldLabel: 'Uom',
                                    autoSelect: false,
                                    displayField: 'uom',
                                    queryCaching: false,
                                    queryMode: 'local',
                                    store: 'uomStore',
                                    valueField: 'uom'
                                },
                                {
                                    xtype: 'button',
                                    id: 'refRate',
                                    text: 'refresh'
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: 'panel',
                    region: 'center',
                    id: 'content',
                    itemId: 'contentPanel',
                    style: {
                        position: 'relative',
                        width: '100%',
                        height: '100%'
                    },
                    defaultDockWeights: {
                        top: {
                            render: 1,
                            visual: 1
                        },
                        left: {
                            render: 3,
                            visual: 5
                        },
                        right: {
                            render: 5,
                            visual: 7
                        },
                        bottom: {
                            render: 7,
                            visual: 3
                        }
                    },
                    bodyPadding: 10,
                    shrinkWrapDock: 2,
                    title: 'Status',
                    titleAlign: 'left',
                    items: [
                        {
                            xtype: 'container',
                            id: 'grid',
                            style: {
                                position: 'absolute',
                                left: 0,
                                top: 0,
                                width: 'calc(100% - 220px)',
                                height: '100%',
                                'padding-left': '1%',
                                'padding-bottom': '1%',
                                'padding-top': '3px'
                            }
                        },
                        {
                            xtype: 'container',
                            id: 'legend',
                            maxWidth: 220,
                            minWidth: 220,
                            style: {
                                position: 'absolute',
                                stroke: '#000000',
                                'stroke-width': 5,
                                width: '15%',
                                height: '100%',
                                right: 0,
                                top: 0,
                                'padding-left': '1%',
                                'padding-top': '10px'
                            },
                            width: 220,
                            items: [
                                {
                                    xtype: 'label',
                                    id: 'legendTitle',
                                    text: 'Error code'
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'exc1',
                                    maxWidth: 185,
                                    minWidth: 185,
                                    width: 185,
                                    fieldLabel: '1',
                                    labelWidth: 20,
                                    name: '',
                                    readOnly: true,
                                    blankText: 'ParsiongError',
                                    emptyText: 'ParsingError'
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'exc2',
                                    maxWidth: 185,
                                    minWidth: 185,
                                    width: 185,
                                    fieldLabel: '2',
                                    labelWidth: 20,
                                    name: '',
                                    readOnly: true,
                                    blankText: 'ParsongError',
                                    emptyText: 'TypeError'
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'exc3',
                                    maxWidth: 185,
                                    minWidth: 185,
                                    width: 185,
                                    fieldLabel: '13',
                                    labelWidth: 20,
                                    name: '',
                                    readOnly: true,
                                    blankText: '',
                                    emptyText: 'EOFError'
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'exc4',
                                    maxWidth: 185,
                                    minWidth: 185,
                                    width: 185,
                                    fieldLabel: '42',
                                    labelWidth: 20,
                                    name: '',
                                    readOnly: true,
                                    blankText: 'ParsiongError',
                                    emptyText: 'IndexError'
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'exc5',
                                    maxWidth: 185,
                                    minWidth: 185,
                                    width: 185,
                                    fieldLabel: '8',
                                    labelWidth: 20,
                                    name: '',
                                    readOnly: true,
                                    blankText: 'ParsiongError',
                                    emptyText: 'BufferError'
                                },
                                {
                                    xtype: 'radiogroup',
                                    id: 'radioGroup',
                                    itemId: 'radioGroup',
                                    width: 170,
                                    fieldLabel: 'Type',
                                    labelWidth: 30,
                                    items: [
                                        {
                                            xtype: 'radiofield',
                                            labelWidth: 40,
                                            name: 'rb',
                                            boxLabel: 'Delay',
                                            inputValue: 'delay'
                                        },
                                        {
                                            xtype: 'radiofield',
                                            name: 'rb',
                                            boxLabel: 'Cycle',
                                            checked: true,
                                            inputValue: 'cycle'
                                        }
                                    ]
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'minValue',
                                    minWidth: 185,
                                    width: 185,
                                    fieldLabel: 'Min value',
                                    labelWidth: 65,
                                    readOnly: true
                                },
                                {
                                    xtype: 'textfield',
                                    id: 'maxValue',
                                    width: 185,
                                    fieldLabel: 'Max value',
                                    labelWidth: 65,
                                    readOnly: true
                                }
                            ]
                        },
                        {
                            xtype: 'container',
                            id: 'popup',
                            style: {
                                position: 'absolute',
                                display: 'block',
                                'z-index': 100,
                                visibility: 'hidden',
                                'line-height': 1,
                                'font-weight': 'bold',
                                padding: '12px',
                                background: 'rgba(0,0,0,0.6)',
                                color: '#fff',
                                'border-radius': '2px'
                            }
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: 'panel',
                            dock: 'bottom',
                            baseCls: 'mainFooter',
                            height: 25,
                            html: '<a style="color: white; text-decoration: none;" href="http://www.supsi.ch/ist" target="_BLANK">Open Source Software by Institute of Earth Science - SUPSI</a>',
                            id: 'bottomPanel',
                            maxHeight: 25,
                            minHeight: 25,
                            layout: 'absolute',
                            title: '     ',
                            titleAlign: 'center'
                        }
                    ]
                }
            ]
        });

        me.callParent(arguments);
    }

});