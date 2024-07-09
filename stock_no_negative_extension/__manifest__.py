# -*- coding: utf-8 -*-
{
    'name': 'Stock Disallow Negative Extension',
    'author': 'asn',
    'company': 'HAK FIST',
    'website': 'www.hakfist.com',
    'version': '17.0.1.0.0',
    'support': 'info@hakfist.com',
    'summary': 'Disallow negative stock levels by default',
    'description': """ """,
    'depends': ['stock_no_negative'],
    'data': [
        'views/user_group.xml',
        'views/product_product_view.xml',
        'views/product_category_view.xml',
        'views/stock_location_view.xml'
    ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
