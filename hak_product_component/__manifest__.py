# -*- coding: utf-8 -*-
{
    'name': "Product Component",
    'company': '',
    'website': '',
    'version': '17.0.1.0.4',
    'support': '',
    'category': 'Inventory',
    'summary': " ",
    'description': """Product Component
    """,
    'depends': ['sale_management', 'hak_product_configurator'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_category_view.xml',
        'views/product_component_view.xml',
        'views/product_template_view.xml',
    ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
