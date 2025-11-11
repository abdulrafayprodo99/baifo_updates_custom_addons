{
    'name': 'Prodo X Biafo Ext App',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'sequence': 1,
    'author': 'Muhammad Bilal , Hamza Khattak',
    'depends': ['base','production_demand_plan','quality','stock','purchase_request'],

    'data': [
        'security/ir.model.access.csv',
        'views/affinity_x_biafo_ext.xml',
        'views/attestation_view.xml',
        'views/currency_rate.xml',
        'views/rfq_comparison_view.xml',
        'data/rfq_data.xml',
        'data/pr_email_template.xml',
        'views/qir_view.xml',
        'views/asset_location.xml',
        'views/operation_subtype.xml',
        'views/merging.xml',
        'views/contract_management.xml',
        'views/stock_picking_sequence.xml',
        'views/intimation.xml',
        # 'data/ir_rule.xml',
        'wizards/reject_wizard.xml',
        'wizards/cancel_wizard.xml',
        'views/landed_cost_analytic.xml',
        'views/stock_move_mrp.xml',

    ],
    'images': [],
    
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',

    'assets': {
        'web.assets_backend': [
            'prodo_x_biafo_ext/static/src/*'
        ]
    },
}
