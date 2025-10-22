from odoo import api,models,fields
from odoo.exceptions import UserError
import datetime
import base64

class InheritAccountAccount(models.Model):
    _inherit = 'account.account'
    
    is_tax = fields.Boolean(string='Ïs Tax?', default=True, store=True, compute='_compute_is_tax')
    
    account_tag_id = fields.Many2one(
        comodel_name="account.account.tag",
        string="Account Tag",
    )
   
    @api.depends('name')
    def _compute_is_tax(self):
        for rec in self:
            rec.is_tax = 'tax' in rec.name.lower() if rec.name else False



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_tag_id = fields.Many2one(
        comodel_name="account.account.tag",
        string="Account Tag",
        related="account_id.account_tag_id",
        store=True,
        readonly=True,
    )
