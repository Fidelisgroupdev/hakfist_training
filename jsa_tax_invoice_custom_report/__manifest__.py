{
    'name': "Tax Invoice Custom Report",
    'version': '17.0.0.3',
    'depends': ['account'],
    'author': "Team JSA",
    'category': 'Sales',
    'description': """
    Tax Invoice Custom Report
    """,
    'data': [
        'report/tax_invoice_report.xml',
        'report/tax_invoice_report_template.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}