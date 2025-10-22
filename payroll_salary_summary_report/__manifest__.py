{
    'name': 'Salary Summary Report',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Generate Salary Summary Report in PDF format',
    'description': """
        This module allows users to generate payroll reports in XLSX format.
    """,
    'author': 'Aneeq Akhtar - Odolution',
    'depends': ['hr', 'hr_payroll', 'payroll_report_xlsx'],
    'data': [
        'views/salary_payslip_report.xml',
        'views/salary_payslip_wizard.xml',
        'views/salary_summary_wizard.xml',
        'views/salary_summary_report.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
