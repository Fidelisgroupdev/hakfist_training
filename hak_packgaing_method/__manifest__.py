# -*- coding: utf-8 -*-
{
    'name': "Packaging Methods",
    'company': '',
    'website': '',
    'version': '17.0.1.0.0',
    'support': '',
    'category': 'Sale',
    'summary': "Packaging Methods",
    'description': """
    """,
    'depends': ['sale_management', 'stock'],
    'data': [
        # 'data/foc_data.xml',
        'security/ir.model.access.csv',
        'views/packaging_method_views.xml',
        'views/sale_order_views.xml',
        'wizard/choose_packaging_method.xml',
    ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
