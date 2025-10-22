{
    "name" : "Currency Exhange Modifications",
    "version" : "16.0.0.2",
    "depends" : ['base','account','purchase','sale_management','stock'],
    "author": "Odolution | Stock",
    'category': 'Accounting',
    "website" : "https://www.odolution.com",
    "depends":["base","account","purchase","sale",'prodo_x_biafo_ext','Record_Expense','production_demand_plan'],
    # "depends":["base","account","purchase","sale",'Record_Expense','production_demand_plan'],
    "data" :[
        'views/account_payment_form_view_inherited.xml',
        'views/sale_order_form_view_inherited.xml',
        'views/purchase_order_form_view_inherited.xml',
        ],
    'qweb':[],
    "auto_install": False,
    "installable": True,
    "license": "OPL-1",
}