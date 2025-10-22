# -*- coding: utf-8 -*-

{
    "name": "Record Expense Rate Conversion",
    "summary": "Record Expense Rate Conversion Module",
    "description": """Record Expense Rate Conversion Module.""",
    "author": "Mahshid Fatima",
    "website": "",
    "license": "",
    "version": "1.0.0",
    "depends": ["sale","base" , 'Record_Expense','account','account_payment','sales_team'],
    "data": [
        "views/record_expense_view_currency.xml",
        'views/account_payment_view_inherit.xml',        
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    
     
}
