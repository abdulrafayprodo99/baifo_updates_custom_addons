{
    'name': 'inventory overview',
    "author": "Abdul Wahab | Odolution",
    'version': '16.0',
    'description': "Inventory Overview",
    'depends': ['base','prodo_x_biafo_ext' , 'stock' , 'mrp'],
    'data': [
        'views/inherit_stock_picking.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': -999,
    'license': 'LGPL-3',
}
