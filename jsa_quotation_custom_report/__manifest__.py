{
    'name': "Quotation Custom Invoice",
    'version': '17.0.0.2',
    'depends': ['sale_management'],
    'author': "Team JSA",
    'category': 'Sales',
    'description': """
    Quotation Custom Invoice
    """,
    'data': [
        'report/quotation_report.xml',
        'report/quotation_report_template.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
    'module_type': 'official',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
