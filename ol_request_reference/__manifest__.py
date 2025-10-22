# __manifest__.py
{
    'name': 'Request Reference',
    'version': '1.0',
    'summary': 'request reference',
    'description': 'This module adds the pr no fields in request reference',
    'author': 'Abdul Wahab ',
    'depends': ['base','prodo_x_biafo_ext'],
    'data': [
        'views/rfq_view_inherit.xml',
    ],

    'installable': True,
    'application': True,
    'sequence': -999,
    'license': 'LGPL-3',
}

