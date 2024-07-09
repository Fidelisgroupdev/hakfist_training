{
    'name': "Pro-forma Custom Invoice",
    'version': '17.0.0.4',
    'depends': ['sale'],
    'author': "Team JSA",
    'category': 'Sales',
    'description': """
    Pro-forma Custom Invoice
    """,
    'data': [
        'report/proforma_invoice_report.xml',
        'report/proforma_invoice_report_template.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
