{
    'name': 'Cost Field',
    'version': '16.0.1.0.2',
    'summary': 'Move History',
    'sequence': -100,
    'author': 'Osama Nadeem ',
    'license': 'OPL-1',
    'description':"""
      
        """,
    "price": "29.00",
    "currency": "USD",
    'depends': ['stock', 'purchase_request'],
    'data':[
        # 'security/ir.model.access.csv',
        "view/_cost_field.xml",
        # "view/_contact_field_in_purchase.xml",
        "view/purchase_order_view_form.xml",
        ],
    # 'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
