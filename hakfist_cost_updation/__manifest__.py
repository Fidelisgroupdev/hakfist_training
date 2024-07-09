{
    'name': 'Product Cost',
    'author': 'HAKFIST',
    'company': 'HAKFIST',
    'website': 'www.hakfist.com',
    'version': '17.0.1.0.2',
    'support': 'info@hakfist.com',
    'summary': 'Product Cost',
    'description': """Product Cost update restriction """,
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_template.xml',
        'wizard/product_cost_wizard_view.xml'
    ],
    "images": ["static/description/icon.png"],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
