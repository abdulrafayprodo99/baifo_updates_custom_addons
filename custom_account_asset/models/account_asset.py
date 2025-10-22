from odoo import models, fields, api

class AccountAsset(models.Model):
    _inherit = "account.asset" # M Azeem added this

    asset_history_ids = fields.One2many('asset.history.lines', 'account_asset_id', string="Account History")
    acc_class_id = fields.Many2one('account.asset.class', string="Asset Class ")
    sub_acc_class_id = fields.Many2one('account.sub.asset.class', string="Sub Asset Class")