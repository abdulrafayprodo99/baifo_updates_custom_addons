{
    'name': 'Sequence Transfer',
    'version': '1.0.0',
    'author': 'Zain Ul Abedin',
    'depends': [
        'base',  # Odoo base module dependency
        'stock',  # If related to inventory management or stock
        'sale',  # If related to sales management
        'purchase',  # If related to purchase management
        'prodo_x_biafo_ext'
    ],
    'data': [
        'views/picking_form.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
