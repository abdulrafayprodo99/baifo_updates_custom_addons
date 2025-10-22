{
    'name': 'Sale Quotation Customization',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Customizations for Sale Quotations',
    'description': """
        This module customizes sale quotations in Odoo, 
    """,
    'author': 'Zain Ul Abedin',
    'depends': [
        'sale_management',  
        'sale', 
        'sale_revision_history',
        'account', 
        'prodo_x_biafo_ext',
        'stock', 
    ],
    'data': [
        'views/sale_quotation.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
        'web.assets_qweb': [
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
