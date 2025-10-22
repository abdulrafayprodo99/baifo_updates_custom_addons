{
    'name': 'Bank Letter',
    'version': '1.0',
    'category': 'Customizations',
    'author': 'Ataib Saboor',
    'depends': ['hr', 'hr_payroll', 'report_xlsx', 'base'],
    'summary': '',
    'description': '',
    'data': [
        'security/ir.model.access.csv',
        'wizards/bank_letter_wizard.xml',
        'reports/bank_letter_report_template.xml',
        'reports/bank_letter_report.xml',
        'views/hr_payslip.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
