{
    'name': "Production Demand Order",
    'author':"Hamza Khattak",
    'summary': """
       """,
    'version': '1',
    'depends': ['account_budget','purchase_request','purchase','sale','stock','base'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/sequence.xml',
        'views/production_demand_plan_view.xml',
        
    ],
    'installable': True,
    'application': True,
}
