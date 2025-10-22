{
    'name': "Account Changes",
    'version': '1.0',
    'author': "Karimdad | Odolution",
    'sequence':-1000,
    'description': """
    This module holds all the changes to the app Account.
    """,
    "depends": ['base','account','prodo_x_biafo_ext'],
    # "depends": ['base','account'],
    'data': [
        'views/account_payment_extension.xml',
        'views/account_account_extension.xml',
    ],            
    'demo': [],
    'assets': {},
    'auto_install' : False,
    'application': True,
    'installable':True,
    'license': 'LGPL-3',
}