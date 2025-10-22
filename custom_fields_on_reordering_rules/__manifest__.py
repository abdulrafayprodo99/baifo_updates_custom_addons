{
    'name': 'Custom Fields on Reordering Rules',
    'version': '1.0.0',
    'category': 'Inventory',
    'summary': 'Add custom fields to Reordering Rules in Odoo',
    'description': 'This module adds additional float fields to the stock.warehouse.orderpoint model.',
    'author': 'Zain Ul Abedin - Odolution',
    'depends': ['stock','purchase_stock'],
    'data': [
    'views/stock_orderpoint_fields_view.xml',
],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}