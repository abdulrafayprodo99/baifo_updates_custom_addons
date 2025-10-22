{
    'name': 'Custom Approval Request',
    'version': '1.0',
    'summary': 'Customizations for Approval Request Form',
    'description': """
        This module customizes the Approval Request form by adding custom fields and adjusting the visibility of buttons.
        It also changes the "Submitted" status label to "Prepare".
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Approvals',
    'depends': ['base','approvals','affinity_x_payroll_ext'],
    'data': [
        'views/view_approval.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
