# -*- coding: utf-8 -*-
{
    'name': 'Fastra Inventory - Simbeez',
    'summary': 'Fastra Inventory - Simbeez',
    'category': 'Warehouse',
    'version': '12.0',
    'author': 'Simbeez',
    'depends': [
        'stock', 'od_material_consumption', 'posh_multilocation', 'fastra_purchase_custom'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/request_inventory.xml',
        'views/stock_location.xml',
        'views/stock_move_line_inherit_view.xml',
        'views/asset_schedule_view.xml',
        'views/stock_move_line_excel_report.xml',
        'views/stock_quant.xml',
        'wizard/inventory_request_confirm_wizard.xml',
        'reports/product_inventory_valuation.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
