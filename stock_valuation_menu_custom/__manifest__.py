{
    'name': 'Stock Valuation Menu Custom',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Customizations for Stock Valuation Menu',
    'description': """
        This module provides customizations for the stock valuation menu in Odoo.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'depends': ['stock', 'account', 'stock_account'],
    'data': [
        'views/stock_valuation_view.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
