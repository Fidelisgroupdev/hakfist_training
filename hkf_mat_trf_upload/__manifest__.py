# -*- coding: utf-8 -*-
{
    'name': "hkf_mat_trf_upload",

    'summary': """
        import inventory transfer""",

    'description': """
        import inventory transfer
    """,

    'author': "jsa",
    'website': "http://www.hakfist.com",

    'category': 'stock',
    'version': '17.0.1.0.4',

    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/picking_view.xml',
    ],

    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
