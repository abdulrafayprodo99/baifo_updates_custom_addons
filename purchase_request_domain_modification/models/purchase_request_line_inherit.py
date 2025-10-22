
from odoo import models, fields

class PurchaseRequestLineInherit(models.Model):
    _inherit = 'purchase.request.line'
     

    account_id = fields.Many2one('account.account', string="Account" , domain=[('account_type', 'in',['expense','asset_current','asset_non_current','expense_direct_cost', 'asset_fixed'])] )
