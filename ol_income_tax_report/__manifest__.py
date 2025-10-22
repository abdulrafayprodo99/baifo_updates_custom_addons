{
    'name': 'Income Tax Report',
    "author": "Huzaifa Shaikh | Odolution",
    'version': '16.0',
    'description': "Income Tax Report",
    'depends': ['base','hr_payroll'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/custom_wizard.xml",
        # "views/stock_valuation_layer.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': -999,
    'license': 'LGPL-3',
}
