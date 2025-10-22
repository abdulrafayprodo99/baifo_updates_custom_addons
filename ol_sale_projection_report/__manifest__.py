{
    'name': "Sale Projection Report",
    'author':'Maaz Ali - Odolution',
    "license": "AGPL-3",
    'category': 'Reporting',
    'version': '1.0.0',
    "depends": ['base','sale','Brand_field_on_product'],
    "application": True,
    "data": [
        "wizard/sale_projection.xml",
        "reports/sale_projection_report.xml",
        "security/ir.model.access.csv",
            ],
    'demo': [],
    'installable': True,
    'assets': {},
    'application':True,
    'license': 'LGPL-3',
}
