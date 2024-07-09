{
    'name': "Employee Purchase Requisition",
    'version': '17.0.0.7',
    'depends': ['base', 'hr', 'stock', 'purchase', 'purchase_requisition'],
    'author': "Team JSA",
    'category': 'Purchases',
    'description': """
    Employee Purchase Requisition,
    """,
    # data files always loaded at installation
    'data': [
        'security/security_access.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/product_data.xml',
        'views/purchase_requisition.xml',
        'views/menu.xml',
        'views/hr_employee_view.xml',
        'views/hr_department_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'views/action_print_requisition.xml',
        'views/stock_location_view.xml',
        'wizard/mr_rejection_wizard.xml',
        'report/purchase_requisition_template.xml',
        'report/purchase_requisition_report.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
# {
#     'name': 'Employee Purchase Requisition',
#     'version': '16.0.1.0.1',
#     'category': 'Purchases',
#     'summary': 'Employee Purchase Requisition',
#     'description': 'Employee Purchase Requisition',
#     'author': 'Cybrosys Techno Solutions',
#     'company': 'Cybrosys Techno Solutions',
#     'maintainer': 'Cybrosys Techno Solutions',
#     'images': ['static/description/banner.png'],
#     'website': 'https://www.cybrosys.com',
#     'depends': ['base', 'hr', 'stock', 'purchase'],
#     'data': [
#         # 'security/custom_security_access.xml',
#         'security/security_access.xml',
#         'security/ir.model.access.csv',
#         'data/ir_sequence_data.xml',
#         'views/purchase_requisition.xml',
#         'views/menu.xml',
#         'views/hr_employee_view.xml',
#         'views/hr_department_view.xml',
#         'views/purchase_order_view.xml',
#         'views/stock_picking_view.xml',
#         'views/action_print_requisition.xml',
#         'views/stock_location_view.xml',
#         'report/purchase_requisition_template.xml',
#         'report/purchase_requisition_report.xml',
#     ],
#     'license': 'AGPL-3',
#     'installable': True,
#     'auto_install': False,
#     'application': True,
# }