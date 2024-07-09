# -*- coding: utf-8 -*-

{
    'name': "Hak Purchase Return",
    'company': '',
    'website': '',
    'version': '17.0.1.0.0',
    'support': '',
    'category': 'Stock',
    'summary': "Hak Purchase Return",
    'description': """
    """,
    'depends': ['stock'],
    'data': [
        'views/purchase_return_reason.xml',
        'views/stock_picking.xml',
        'views/picking_return.xml',
        'security/ir.model.access.csv',
           ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
