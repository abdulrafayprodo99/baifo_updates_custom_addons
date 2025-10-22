# -*- coding: utf-8 -*-
{
    'name': "Affinity Production Plan",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Asir Amin",
    'website': "https://www.affinitysuite.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
}
