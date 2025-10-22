from odoo import models, api, fields

class AccountAssetClass(models.Model):
    _name = 'account.asset.class' # M Azeem started Task 43483

    name = fields.Char(string="Name")