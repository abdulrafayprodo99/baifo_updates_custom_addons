{
    "name": "Custom Account Asset",
    "author" : "Muhammad Azeem",
    "license" : "LGPL-3",
    "version" : "16",
    "depends" : ['base', 'account','account_asset', 'account_asset_no_days_issue','hr', ],
    # hr, 
    "data" : [
        # M Azeem Task: 43480
        'security/ir.model.access.csv',
        'views/account_asset_view.xml',
        'views/account_asset_class_view.xml',
        'views/account_sub_asset_class_view.xml',
        'views/menu.xml',
    ],
    "installable" : True,
    "application" : True,
    "auto_install" : False

}
