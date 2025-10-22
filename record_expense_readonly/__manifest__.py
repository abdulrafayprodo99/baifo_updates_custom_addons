# -*- coding: utf-8 -*-

{
    "name": "Record Expense Readonly",
    "summary": "Record Expense Readonly",
    "description": """Record Expense Readonly Module.""",
    "author": "",
    "website": "",
    "license": "",
    "version": "1.0.0",
    "depends": ['record_expense_rate_conversion','Record_Expense'],
    "data": [
        "views/record_expense_view.xml",
        # 'views/account_payment_view_inherit.xml',        
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    
     'assets': {
        'web.assets_backend': [
            'record_expense_readonly/static/src/*'
        ]
    },
}
