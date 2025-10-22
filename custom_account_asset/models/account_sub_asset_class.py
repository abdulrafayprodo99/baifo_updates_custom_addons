from odoo import models, api, fields

class AccountSubAssetClass(models.Model):
    _name = 'account.sub.asset.class' # M Azeem started Task 43483

    name = fields.Char(string="Name")