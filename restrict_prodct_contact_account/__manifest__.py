{
    'name': 'Restriction on Prepared Product/Contact/Account',
    'version': '1.0',
    'category': 'Access Control',
    'summary': 'Something...',
    'description': """
        This module integrates Some functionalities with inventory transfers, delivery management, and invoicing.
    """,
    'author': 'Zain Ul Abedin',
    'depends': [
        'base',              # Core Odoo base module
        'product',           # Product management
        'stock',             # Inventory management
        'mrp',               # Manufacturing resource planning
        'sale',              # Sales and invoicing
        'account',
        'prodo_x_biafo_ext',  # Accounting module for invoices
    ],
    'data': [
        # 'security/ir.model.access.csv',  # Access rights definitions
        # 'views/mrp_production_views.xml', # MRP production views
        # 'views/stock_transfer_views.xml', # Stock transfer views
        # 'views/account_invoice_views.xml', # Invoice views
        # 'views/views.xml',
        'views/filter.xml',
    ],
    'installable': True,
    'application': True,
}
