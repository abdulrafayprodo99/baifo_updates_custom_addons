{
    'name': 'Payroll Report XLSX',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Generate payroll reports in XLSX format',
    'description': """
        This module allows users to generate payroll reports in XLSX format.
    """,
    'author': 'Zain Ul Abedin - Odolution',
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'views/payroll_report.xml',
        'views/payroll_pdf_report.xml',
        'secuirity/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
