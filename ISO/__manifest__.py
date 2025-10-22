# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ISO',
    'version': "1.0.0",

    'summary': '',
    'description': """""",
    'depends': ['account','base','sale'],
    'data': [
          'views/iso.xml',
          'security/ir.model.access.csv',
          
        ],
   
    'installable': True,
    'application': True,
    'auto_install': False,
    'License': 'LGPL-3'
}



