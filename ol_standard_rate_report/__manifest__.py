{
    'name': 'Standard Rate Report',
    'version': '1.0',
    'summary': '''
                Custom module for Standard Rate Report in Excel and PDF.
                Task ID: 38,779,
                ''',
    'author': 'Rao Abdul Rehman',
    'depends': ['product', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard.xml',
        'views/standard_rate_report.xml',
    ],
}