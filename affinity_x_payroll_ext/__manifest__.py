# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Affinity X Payroll Ext',
    'version': "1.0.0",
    'category': '',
    'summary': '',
    'description': """""",
    'author': "Bilal",
    'sequence': '-100',
    'depends': ['hr_contract','hr_payroll','hr','base','approvals'],
    'images' : [],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_request.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'License': 'LGPL-3'
}
