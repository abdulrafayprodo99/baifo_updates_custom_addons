{
    'name': 'Activity Generation On Delivery Order',
    'version': '1.0',
    'description': """
        This app generate activity on basis of Different Stage.
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Approvals',
    'depends': ['base', 'sale',  'approvals' ,'prodo_x_biafo_ext'],
    'data': [
        'views/view_stock_backorder_confirmation.xml',
        # 'views/view_stock_picking.xml',
        'views/do_ref.xml',
        'views/stock_move_line_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
