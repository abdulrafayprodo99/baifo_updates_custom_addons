{
    'name': 'MRP Production Quantity Done',
    'version': '1.0',
    'summary': 'Adds a field to MRP Production to calculate total quantity_done excluding specific products.',
    'description': 'This module adds a computed field to MRP Production that calculates the total quantity_done from related stock moves, excluding products whose internal reference starts with "9".',
    'author': 'Zain Ul Abedin',
    'category': 'Manufacturing',
    'depends': ['mrp', 'stock'],
    'data': [
        'views/mrp_production_view.xml',
    ],
    'installable': True,
    'application': False,
}
