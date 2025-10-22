# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer License',
    'version': "1.0.0",

    'summary': '',
    'description': """""",
    'depends': ['account','base','sale','mail'],
    'data': [
          'views/model.xml',
          'views/customer_license.xml',
          'security/ir.model.access.csv',
          
        ],
   
    'installable': True,
    'application': True,
    'auto_install': False,
    'License': 'LGPL-3'
}



