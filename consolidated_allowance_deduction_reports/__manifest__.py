{
    'name': 'Allowance Reports',
    'version': '16.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Generate Allowance Reports',
    'description': """This module allows to generate allowance reports in PDF and Excel format.""",
    'author': 'Your Company',
    'depends': ['base', 'hr', 'allowances_deduction_employee_form', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/allowance_report_wizard_view.xml',
        'wizards/allowance_details_report_wizard_view.xml',
        'reports/allowance_report.xml',
        'reports/allowance_details.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}