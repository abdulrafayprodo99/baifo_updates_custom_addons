{
    "name" : "Planning Manufacturing Modifications",
    "version" : "16.0.0.2",
    "depends" : ['base','account','purchase','sale_management','stock'],
    "author": "Odolution | Uzair Ahmed",
    'category': 'Accounting',
    "website" : "https://www.odolution.com",
    "depends":["production_demand_plan",'prodo_x_biafo_ext', 'affinity_production_plan'],
# ,'mrp','production_demand_plan', 'affinity_production_plan'
    "data" :[
        'views/view_pdo_form.xml',
        ],
        # 'views/mrp_production_view.xml',
    'qweb':[],
    "auto_install": False,
    "installable": True,
    'application': True,
    "license": "OPL-1",
}