# -*- coding: utf-8 -*-
{
    'name': 'Custom_attendance_report',
    'version': '',
    'summary': """ Custom_attendance_report Summary """,
    'author': 'Odolution | Abdul Wahab',
    'website': '',
    'category': '',
    'depends': ['base', ],
    'data': [
        'security/ir.model.access.csv',
        'report_wizard/attendance_report_wizard.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
