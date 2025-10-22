{
    'name':'Product Ledger Report',
    "version": "16.0.0.0.0",
    "license": "LGPL-3",
    "installable": True,
    "depends": ['stock','stock_account'],
    "data": [
        'security/ir.model.access.csv',
        'view/product_ledger.xml',
        'view/stock_valuation_layer.xml',
        'report/product_ledger.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend':[
    #         'product_ledger_report/static/src/css/styles.css',
    #     ]
    # },
    "application":True
}
