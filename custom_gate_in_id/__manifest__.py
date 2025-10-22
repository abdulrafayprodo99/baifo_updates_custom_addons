{
    'name': 'Custom Gate In many 2 many',
    'version': '1.0',
    'author': 'Zain Ul Abedin',
    'category': 'Gate In ID',
    'depends': ['base', 'stock', 'prodo_x_biafo_ext', 'gate_module'],
    # 'depends': ['base', 'stock', 'gate_module'],
    'data': [
        # Add XML files for views, filters, or actions here
        'views/custom_gate_in_id.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
