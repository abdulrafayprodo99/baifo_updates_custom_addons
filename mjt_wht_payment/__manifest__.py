{
    'name': "Affinity Payment WHT",

    'summary': """
        Extend Payment usage""",

    'description': """
    """,
    'author': "Bilal",
    'license':'AGPL-3',
    'website': "",
    'category': 'Accounting',
    'version': '0.1',

    'depends': ['account','prodo_x_biafo_ext'],
    # 'depends': ['account'],

    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        # 'views/bukti_potong_view.xml',
    ],
}
