# __manifest__.py

{
    'name': 'WHT Extension',
    'version': '1.0',
    'summary': 'Extended functionality for Withholding Tax (WHT)',
    'description': """
This module extends the existing WHT (Withholding Tax) functionality in Odoo, 
adding custom rules, reports, and improved handling for specific country tax regulations.
""",
    'category': 'Accounting',
    'author': 'Zain Ul Abedin - Odolution',
    'depends': ['base', 'account', 'contacts', 'mjt_wht_payment'],
    'data': [
        # 'views/res_partner_aop.xml'
        # 'security/ir.model.access.csv',

        'views/tax_payment.xml',
        'security/ir.model.access.csv',
        'wizard/wht_receipt_wizard.xml',
        'wizard/cprm_updated.xml',
        'reports/excel_wizard.xml',
        'reports/payment_wht_line_report_wizard_views.xml',
        'reports/payment_report_template.xml',

     

    ],
    'assets': {

        'web.assets_backend': [

            'wht_extension/static/src/js/button_tree_extend.js',

            'wht_extension/static/src/xml/button_list_button.xml',

        ],

    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
