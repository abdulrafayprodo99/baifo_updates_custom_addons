{
    'name': 'Purchase Request Modification',
    'version': '1.0.0',
    'sequenece':-200,
    'depends': ['purchase','purchase_request','prodo_x_biafo_ext','gate_module','mrp', 'stock'],
    'data': [
        # 'views/view_po_modification.xml',
        # 'views/view_stock_picking.xml',
        'views/view_gate_in_modification.xml',
        'views/purchase_request_from.xml',
        'views/mrp_bom_form_view.xml'
        ],

    'demo': [],
    'application':True,
    'installable': True,
    'auto_install':False,
    'assets': {},
    'license': 'LGPL-3',
}
