{
    'name': 'Custom Asset Tree Form View',
    'version': '1.0',
    'summary': 'Customizations for the Asset Form View',
    'description': """
        This module customizes the Account Asset form view by adding new fields and making layout changes.
    """,
    'author': 'Zain Ul Abedin | Odolution',
    'category': 'Accounting',
    'license': 'LGPL-3',
    'depends': ['account_asset', 'account_asset_no_days_issue', 'ol_quality_control'],  # Ensure you depend on 'account_asset'
    'data': [
        'views/account_asset_form_inherit.xml',  # Include your XML view inheritance file
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
