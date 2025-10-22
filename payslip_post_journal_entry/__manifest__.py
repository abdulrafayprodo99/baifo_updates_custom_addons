{
    'name': "HR Payslip Journal Entry Enhancement",
    'summary': """
        Adds button to post journal entries for payslip batches""",
    'description': """
        This module adds a 'Post Journal Entry' button to the HR Payslip Run form
        to easily post accounting entries for all payslips in a batch.
    """,
    'author': "Aneeq Akhtar",
    'category': 'Human Resources/Payroll',
    'version': '1.0',
    'depends': ['hr_payroll', 'account'],
    
    'data': [
        'views/payslip_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}