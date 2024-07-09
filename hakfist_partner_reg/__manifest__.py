# -*- coding: utf-8 -*-
{
    'name': 'Customer Registration Management',
    'version': '17.0.1.0.6',
    'summary': '',
    'sequence': 10,
    'description': """
    Customer Registration Management
    """,
    'category': 'contact',
    'website': '',
    'images': [],
    'depends': ['contacts', 'crm', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/reject_reason_view.xml',
        'views/temp_partner_view.xml',
        'views/res_partner_views.xml',
        'wizard/reject.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # "/hakfist_partner_reg/static/css/style.css",
        ],
    },

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
