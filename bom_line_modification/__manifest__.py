{
    'name': 'BOM Line Modification',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Module to add custom purchase rate fields on product templates.',
    'description': 'This module adds a custom purchase rate field on product templates and products.',
    'depends': ['base', 'product', 'affinity_x_payroll_ext' , 'mrp'],
    'data': [
        'views/product_template_view.xml',  # Link to the XML view
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}