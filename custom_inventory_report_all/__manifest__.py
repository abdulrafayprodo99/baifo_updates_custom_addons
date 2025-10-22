{
    'name':'Custom Inventory Report',
    'author':"Ataib",    
    "version": "1.0",#16.0.1.0.9
    "license": "LGPL-3",
    "installable": True,
    "depends": ['stock', 'report_xlsx'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/custom_inventory_report.xml',
        'reports/inventory_report_all_paper_format.xml',
        'reports/inventory_report_all_template.xml',
        'reports/inventory_report_all.xml',
    ],
    "application":True
}
