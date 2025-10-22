{
    'name':'Custom Inventory Report',
    'author':"Odolution | Uzair",    
    "version": "16.0.1.0.9",
    "license": "LGPL-3",
    "installable": True,
    "depends": ['stock'],
    "data": [
        'security/ir.model.access.csv',
        'report_templates/template_inventory_closing.xml',
        'report_templates/template_inventory_all.xml',
        'report_templates/paperformat_for_inventory_reports.xml',
        'report_wizard/custom_inventory_report.xml',
        'report_wizard/stock_status_inventory_report.xml',
        'report_btns/inventory_report_btns.xml',
    ],
    "application":True
}
