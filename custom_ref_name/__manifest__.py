{
    'name': 'Custom Account Move Asset Fields',
    'version': '1.0',
    'summary': 'Adds sr_no and asset_tag fields to ref and name fields in account move and move lines',
    'description': """
        This module customizes the ref field in account.move and the name field in account.move.line
        by adding the sr_no and asset_tag fields from the account.asset model.
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Accounting',
    'depends': ['account', 'account_asset'],
    'data': [
        'views/account_move.xml',
    ],
    'installable': True,
    'application': False,
}
