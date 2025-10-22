{
    'name': 'Partner Type Management',
    'version': '1.0',
    'category': 'Contacts',
    'summary': 'Add customer, vendor, both, and contact type selection for partners.',
    'description': """
        This module adds a selection field in res.partner to categorize partners as:
        - Customer
        - Vendor
        - Both (Customer and Vendor)
        - Contact
        The selected type will dynamically adjust the customer and vendor ranks of the partner.
    """,
    'author': 'Zain Ul Abedin',
    'license': 'LGPL-3',
    'depends': ['base','account', 'sale', 'crm'],
    'data': [
        'views/res_partner_views.xml',
        'views/move_payment_inherit.xml',
        'views/view_CRM_customer_menu.xml',# The XML file where the view modifications are defined
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
