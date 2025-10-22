{
    'name': 'Journal Entry Origin Field',
    'version': '1.0',
    'summary': 'Adds an Origin field to Journal Entries displaying related Invoice/Payment names',
    'description': """
        This module adds a computed field "Origin" on Journal Entries, 
        showing the related Invoice and Payment names in the format <invoice name> / <payment name>.
    """,
    'category': 'Accounting',
    'author': 'Zain Ul Abedin',
    'depends': ['account', 'dropdown_contact'],
    'data': [
        'views/account_move_views.xml',  # Your XML file to modify the form view
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
