{
    'name': "Bank Account",
    'version': '1.0',
    'author': "Sher Ahmed",
    'sequence':-1000,
    'description': """
    This module holds all the changes to the app Account.
    """,
    "depends": ['base','account'],
    'data': [
        'views/res_partner_bank.xml',       
    ],            
    'demo': [],
    'assets': {},
    'auto_install' : False,
    'application': True,
    'installable':True,
    'license': 'LGPL-3',
}