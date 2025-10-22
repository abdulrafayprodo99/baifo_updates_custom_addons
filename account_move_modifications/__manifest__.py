# -*- coding: utf-8 -*-

{
    'name': 'Account Move Modifications',
    'sequence': '-100',
    'author': 'Odolution | Uzair',
    'depends': ['account','prodo_x_biafo_ext', 'mrp', 'Record_Expense'],
    # 'depends': ['account','stock','mrp','Record_Expense','stock_landed_costs'],
    'demo': [],
    'data': [
        'views/landed_cost_views.xml',
        'views/record_expense_form_view.xml',
        'views/manufacutiring_order_view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
}
