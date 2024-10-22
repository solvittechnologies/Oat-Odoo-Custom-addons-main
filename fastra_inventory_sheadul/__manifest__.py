# -*- coding: utf-8 -*-
{
    'name': 'Fastra Inventory - sheadul',
    'summary': 'Fastra Inventory - sheadul',
    'category': 'Warehouse',
    'version': '12.0',
    'author': 'sheadul',
    'depends': [
        'stock', 'od_material_consumption', 'posh_multilocation','fastra_inventory_simbeez'
    ],
    'data': [
        'views/asset_schedule_view.xml',
        'views/assets.xml',
    ],'qweb': [
        'static/src/xml/view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
