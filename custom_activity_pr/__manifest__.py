{
    'name': 'Activity Generation On Purchase Request',
    'version': '1.0',
    'description': """
        This app generate activity on basis of Different Stage.
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Approvals',
    'depends': ['base','purchase_request',  'prodo_x_biafo_ext','purchase'],
    # 'depends': ['base','purchase_request','purchase'],
    'data': [
        'views/purchase_request_line.xml',
        'views/purchase_order_action.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
