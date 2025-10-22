# -*- coding: utf-8 -*-
{
    'name': 'Tax Certificate Report',
    'version': '16.0.1.0',
    'summary': """ Employee Tax Certificate Report Summary """,
    'author': 'Saif',
    'website': '',
    'category': '',
    'depends': ['base','hr', ],
    'data': [
        'data/tax_certificate_report_seq.xml',
        'report/tax_certificate_report.xml',
        
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
