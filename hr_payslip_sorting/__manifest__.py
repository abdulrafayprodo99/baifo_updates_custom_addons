{
    'name': 'HR Payslip sorting',
    'version': '1.0',
    'category': 'Customizations',
    'author': 'Aneeq Akhtar',
    'depends': ['hr', 'hr_payroll', 'base','account','hr_contract'],
    'summary': '',
    'description': '',
    'data': [
        'views/hr_payslip_view.xml',
        'views/journal_vouchar_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
