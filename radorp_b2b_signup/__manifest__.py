# -*- coding: utf-8 -*-

{
    'name': 'B2B Signup',
    'description': """ B2B Signup """,
    'summary': """ B2B Signup """,
    'category': 'Website',
    'version': '17.0.0.0',
    'author': 'RADORP Pvt. Ltd.',
    'website': 'https://radorp.com/',
    'depends': [
        'portal'    
    ],
    'data': [
        'views/auth_signup_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'radorp_b2b_signup/static/src/js/auth_signup.js',
            'radorp_b2b_signup/static/src/scss/auth_signup.scss',
        ],
    },
    'images': [
        'static/description/banner.png'
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
