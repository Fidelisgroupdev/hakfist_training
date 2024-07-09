{
    'name': "Delivery Note Custom Report",
    'version': '17.0.0.2',
    'depends': ['stock','stock_delivery'],
    'author': "Team JSA",
    'category': 'Stock',
    'description': """
    Delivery Note and Picking List Custom Report
    """,
    'data': [
        'report/delivery_note_report.xml',
        'report/picking_slip_report.xml',
        'report/delivery_note_report_template.xml',
        'report/picking_slip_report_template.xml',
    ],
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}