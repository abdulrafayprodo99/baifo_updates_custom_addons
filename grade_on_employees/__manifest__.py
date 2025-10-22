# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Employee Grades',
    'version': "1.0.0",
    'author':'Odolution | Uzair',
    'summary': '',
    'description': """""",
    'sequence': '-100',
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/view_grade_employee.xml',
        'views/view_employment_category.xml',
        'views/view_hr_employee.xml'
    ],
     'installable': True,
    'application': True,
    'auto_install': False,
    'License': 'LGPL-3'
}
