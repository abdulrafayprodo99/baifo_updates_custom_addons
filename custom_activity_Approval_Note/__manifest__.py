{
    'name': 'Activity Generation On Approval Note',
    'version': '1.0',
    'description': """
        This app generate activity on basis of Different Stage.
    """,
    'author': 'Zain Ul Abedin',
    'category': 'Approvals',
    'depends': ['base','prodo_x_biafo_ext'],
    # 'depends': ['base'],
    'data': [
        'views/view_approval_note_form.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
