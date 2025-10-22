{
    'name': 'Payment Term Extension',
    'version': '1.0',
    'depends': ['account', 'sale', 'purchase'],
    'author': 'Zain Ul Abedin - Odolution',
    'category': 'Accounting',
    'description': 'Adds order_type field to payment terms',
    'data': [
        'views/account_payment_term_views.xml',
    ],
    'installable': True,
    'application': False,
}
