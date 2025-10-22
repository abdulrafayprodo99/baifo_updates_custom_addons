{
    'name': 'Purchase Order Return Sequence',
    'version': '1.0',
    'category': 'extra-tools',
    'summary': 'Purchase Order Return Sequence',
    'description': """
        Purchase Order Return Sequence
    """,
    'author': 'Odolution | Okasha Bin Ghaffar ',
    'website': 'https://www.odolution.com',
    'depends': ['stock','account'],
    'data': [
        'data/data.xml',
        'reports/credit_note.xml',
        'reports/delivery_return.xml',
        'reports/goods_return.xml',
        'reports/debit_note.xml',
        'reports/vendor_bills.xml',
    ],
    "auto_install": False,
    "installable": True,
    'application': True,
    "license": "OPL-1",

}