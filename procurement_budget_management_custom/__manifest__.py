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
    'depends': ['base','custom_activity_pr','purchase','prodo_x_biafo_ext','account_budget', '_new_state_in_po_pr'],
    'data': [
        'security/ir.model.access.csv',
        'views/procurement_budget_management.xml',
        'views/purchase_request_view.xml',
        'views/purchase_order_view.xml',
        'views/crossovered_budget_lines_view.xml',
        'views/budget_moe_lines.xml',
        'wizard/budget_wizard_view.xml',
        'wizard/budget_report_template.xml',
        'wizard/budget_capex_report.xml',
    ],
    "auto_install": False,
    "installable": True,
    'application': True,
    "license": "OPL-1",

}