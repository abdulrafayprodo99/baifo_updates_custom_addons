{
    'name': 'No Create/ Edit line',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Zain Ul Abedin',
    'depends': ['stock', 'sale','purchase_request', 'mjt_wht_payment', 'mrp'],  # 'mail' is required for activity creation
    # 'depends': ['sale', 'purchase' , 'stock', 'account',  'mrp', 'mail'],  # 'mail' is required for activity creation
    'data': [
        'views/lines.xml' # Add any XML data here like views, security if needed.
    ],
    'installable': True,
    'application': False,
}
