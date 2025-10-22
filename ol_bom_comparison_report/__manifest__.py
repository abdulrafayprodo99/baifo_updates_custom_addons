{
    'name': 'BOM Comparison Report',
    'version': '1.0',
    'summary': '''
                Custom module for BOM Comparison Report in Excel and PDF.
                Task ID: 38,780,
                ''',
    'author': ['Mahshid Fatima', 'abdul wahab'],
    'depends': ['product', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard.xml',
        'views/bom_comparison_report.xml',
    ],
    'application':True,
}