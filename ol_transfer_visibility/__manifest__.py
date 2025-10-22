{
    'name': 'Transfer Visibility',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Transfer Visibility module',
    'description': """  This is the module of Transfer Visibility  """,
    'sequenece':-200,
    'depends': ['stock','prodo_x_biafo_ext'],
    'data': [
        "views/transfer_view.xml",
        "views/affinityInherit_view.xml"
        ],

    'demo': [],
    'application':True,
    'installable': True,
    'auto_install':False,
    'assets': {},
    'license': 'LGPL-3',
}
