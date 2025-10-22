# -*- coding: utf-8 -*-
#################################################################################
#################################################################################

{
    'name': 'Approval Access Groups',
    'version': '16.0.1',
    'sequence': 5,
    'author': 'Muhammad Bilal',
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'website': '',
    'summary': """""",
    
    'description':"""""",
    "images": [],
    "price": "270.99",
    "currency": "USD",
    'data':[
        'security/ir.model.access.csv',
        'views/approval_access.xml',   
        'views/approval_store_node.xml'   
    ],
    'depends':['web','advanced_web_domain_widget'],    
    'application': True,
    'installable': True,
    'auto_install': False,

}
