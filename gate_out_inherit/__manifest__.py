{
    'name': 'Gate Out Customization',
    'version': '1.0',
    'summary': 'Customizations for the Gate Out model',
    'description': """
        This module customizes the Gate Out model to include additional logic for handling delivery orders.
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Custom',
    'depends': ['gate_module', 'stock'],  # Add other dependencies if required
    'data': [
        'views/gate_out_views.xml',  # Add if you have custom views to include
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
