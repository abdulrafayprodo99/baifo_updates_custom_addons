# -*- coding: utf-8 -*-

{
    "name": "Record Forms Readonly",
    "summary": "Record Forms Readonly",
    "description": """Module to make the forms of the models Readonly if Posted.""",
    "author": "Rao Abdul Rehman",
    "license": "LGPL-3",
    "version": "1.0.0",
    "depends": ['account', 'Record_Expense'],
    "data": [
        "views/account_payment.xml",
        "views/account_move.xml",
        "views/expense_module.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    
     'assets': {
        'web.assets_backend': [
            'ol_record_forms_readonly/static/src/*'
        ]
    },
}
