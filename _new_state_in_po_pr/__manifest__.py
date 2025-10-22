{
    'name': 'New State On PR And PO',
    'version': '16.0.1.0.2',
    'summary': 'Close State On PR And PO',
    'sequence': -100,
    'author': 'Osama Nadeem ',
    'license': 'OPL-1',
    'description':"""
      
        """,
    "price": "29.00",
    "currency": "USD",
    'depends': ['purchase','prodo_x_biafo_ext'],
    "data": [
        'security/ir.model.access.csv',
        "view/purchase_request_inherit.xml",
        "view/purchase_order_inherit.xml",
        "view/close_po_wizard_view.xml",
        "view/cancel_po_wizard_view.xml",
        'groups/groups.xml'
    ],
    # 'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
