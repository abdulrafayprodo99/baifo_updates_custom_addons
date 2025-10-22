{
    'name': 'Brand field on product',
    'version': '16.0.1.0.2',
    'summary': 'Field On Product',
    'sequence': -100,
    'author': 'Osama Nadeem | Odolution',
    'license': 'OPL-1',
    'description':"""
      
        """,
    "price": "29.00",
    "currency": "USD",
    'depends': ['base', 'sale', 'product', 'mail', 'stock'],
    'data':[
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/custome_field.xml',
        'views/sale_segment_target_view.xml',
        'views/collection_summary_target_view.xml',
        'views/product_category.xml',
        ],
    # 'images': ['static/description/banner.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
