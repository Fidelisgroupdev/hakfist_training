# -*- coding: utf-8 -*-
{
    'name': 'Inter Company Payments',
    "author": "",
    'website': '',
    'version': '17.0.1.0.1',
    'category': 'Accounting',
    'summary': 'Auto Payment Generation',
    'description': """ """,
    'depends': ['account'],
    'data': [
        "security/ir.model.access.csv",
        "data/inter_company_seq.xml",
        "views/account_payment_views.xml",
        "views/inter_company_payment_views.xml",
        # "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/account_journal_views.xml",
        "wizard/inter_company_payment_wiz_views.xml",
    ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    "images": [],

}

