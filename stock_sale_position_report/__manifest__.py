{
    'name': 'Stock Sale Position',
    'version': '1.0',
    'summary': '',
    'depends': [
        'manufacturing_reports'
    ],
    'data': [
      'security/ir.model.access.csv',
      'views/stock_sale_view.xml',
      'views/stock_sale_wizard.xml',
      'views/menu.xml',
     
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'company': 'Biafo',

}
