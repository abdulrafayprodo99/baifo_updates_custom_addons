# __manifest__.py
{
    'name': 'Quality Management',
    'version': '1.0',
    'category': 'Quality',
    'summary': 'Add button to Quality Overview',
    'description': 'This module adds a custom button to the quality overview screen.',
    'author': 'Aneeq Akhtar',
    'depends': ['base', 'quality','quality_control', 'prodo_x_biafo_ext'],
    'data': [
        'views/quality_button_view.xml',
        'views/qir_button_view.xml',
    ],
    'assets': {

        'web.assets_backend': [

            'ol_quality_management/static/src/js/button_tree_extend.js',
            'ol_quality_management/static/src/xml/button_list_button.xml',

        ],

    },
    'installable': True,
}
