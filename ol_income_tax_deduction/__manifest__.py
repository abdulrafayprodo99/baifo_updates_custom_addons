{
    'name': "Income Tax Deduction",
    'version': '16.0',
    'depends': ['base','hr','hr_payroll'],
    'author': "ahzam.sheikh@odoloution.com",
    'sequence':-1000,
    'description': "Income Tax Deduction with respect to Fiscal Year, Salary Raises and Tax Slabs",
    'data': [
        'views/employee_view_extension.xml'
    ],
    'application': True,
    'license': 'LGPL-3',
}