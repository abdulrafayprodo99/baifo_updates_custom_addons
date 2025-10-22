{
    'name': "Landed Cost Approval",
    'author':"Hamza Khattak",
    'summary': """
       """,
    'version': '1',
    'depends': ['purchase','sale','stock','base','product',
                'stock_landed_costs','account'],
                # 'record_expense',
    'data': [
        'security/ir.model.access.csv',
        'views/landed_cost_apporoval.xml',
    ],
    'installable': True,
    'application': True,
}
