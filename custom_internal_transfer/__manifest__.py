{
    'name': 'Internal Transfer',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Hide the vendor field in stock.picking for internal transfers',
    'author': 'Aneeq Akhtar',
    'depends': ['stock','gate_module'],
    'data': [
        'views/gate_out_view.xml',
        # 'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
