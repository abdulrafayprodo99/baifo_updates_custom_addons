{
    'name': 'Custom Due Filter',
    'version': '1.0',
    'summary': 'Adds a custom due filter to the account.move model.',
    'description': """
        This module adds a custom filter to the account.move model to easily filter invoices that are due.
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        # Add XML files for views, filters, or actions here
        'views/account_move_filter.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
