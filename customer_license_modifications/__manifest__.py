{
    'name': 'Customer License Modification',
    'version': '1.0',
    'author': 'Hayah Ahmed',
    'category': 'Sales',
    'depends': ['base','customer_license_app'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/view_customer_license.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
