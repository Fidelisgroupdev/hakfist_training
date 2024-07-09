# -*- coding: utf-8 -*-

{
    'name': "Product Catalog",
    'company': '',
    'website': '',
    'version': '17.0.1.0.14',
    'support': '',
    'category': 'CRM',
    'summary': " ",
    'description': """Product Catalog
    """,
    'depends': ['sale_management', 'hak_product_configurator', 'hkf_pcat_type'],
    'data': [
        'security/ir.model.access.csv',
        'views/products_view.xml',
        'views/crm_view.xml',

        'wizard/product_catalog_view.xml',
        'report/product_catalog_template.xml',
        'report/report_action.xml',

    ],

    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
