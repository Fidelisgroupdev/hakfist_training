# -*- coding: utf-8 -*-
{
    'name': 'Landed Cost Extended Functionality',
    'author': 'HAK FIST',
    'company': 'HAKFIST',
    'website': 'www.hakfist.com',
    'version': '17.0.1.0.4',
    'maintainer': 'nbl',
    'support': 'info@hakfist.com',
    'summary': 'Landed Cost Extended',
    'description': """Landed Cost Extended""",
    'depends': ['purchase_stock', 'stock_landed_costs', 'stock_account'],
    'data': [
        'views/stock_views.xml',
        'views/stock_landed_cost_views.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
