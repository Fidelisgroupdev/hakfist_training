# -*- coding: utf-8 -*-
# Copyright 2023-TODAY Juan Formoso Vasco <jfv@anubia.es>
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'bulk import in zip',
    'summary': """bulk import in zip.
""",
    'description': """bulk import in zip
""",
    'category': 'Extra Tools',
    'version': '17.0.1.0.0',
    'author': 'JSA',
    'mantainer': 'Chlpn',
    'website': 'hakfist.com',
    'license': 'OPL-1',
    'depends': [
        'base',
    ],
    'external_dependencies': {},
    'data': [
        'security/ir.model.access.csv',
        'wizard/image_zip_importation_views.xml',
    ],
    'demo': [],
    'test': [],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
