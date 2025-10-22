{
    'name': 'Product Group Wise Sales Summary Report',
    'version': '16.0.1.0.0',

    'depends': ['base', 'account'],
    
    'data': ['wizard/wizard.xml',
             'report/report.xml',
             'report/report_template.xml',
             'security/ir.model.access.csv'
             ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
}
