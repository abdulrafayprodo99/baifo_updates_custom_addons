{
    'name': 'Procurement Budget Management',
    'version': '1.0',
    'category': 'Procurement',
    'summary': 'Manage procurement budgets efficiently',
    'description': """
        This module helps in managing procurement budgets, allowing users to create, confirm, and track budgets.
    """,
    'author': 'Odolution | Uzair Ahmed',
    'website': 'https://www.odolution.com',
    'depends': ['base','custom_activity_pr','purchase','prodo_x_biafo_ext','account_budget'],
    'data': [
        'security/ir.model.access.csv',
        'views/procurement_budget_management.xml',
        'views/purchase_request_view.xml',
        'views/purchase_order_view.xml',
        'views/crossovered_budget_lines_view.xml'
    ],
    "auto_install": False,
    "installable": True,
    'application': True,
    "license": "OPL-1",

}