# __manifest__.py
{
    'name': 'Manufacturing Reports',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Wizards for manufacturing reports',
    'author': 'Zain Ul Abedin',
    'depends': ['base', 'stock', 'mrp', 'affinity_production_plan', 'planning_manufacturing_modifications', 'production_demand_plan', 'product'],
    'data': [
        'wizards/wizards_views/daily_production_views.xml',
        'wizards/wizards_views/material_requiement_views.xml',
        'wizards/wizards_views/stock_sale_position_views.xml',
        'wizards/wizards_views/bill_of_material_views.xml',
        'security/ir.model.access.csv',
        'wizards/wizards_views/menus.xml',
        'views/daily_production_template.xml',
        'views/material_requirment_template.xml',
        'views/bill_of_material_template.xml',
        'views/stock_sale_position_template.xml'
    ],
    'installable': True,
    'application': False,
}
