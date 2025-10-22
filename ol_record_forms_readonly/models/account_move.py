from odoo import models, fields
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    vendor_bills_readonly_check = fields.Boolean(string="Vendor Bills Readonly Check")
    journal_type = fields.Char(string="Journal Type")

    def action_post(self):
        for rec in self:
            if rec.move_type in ['in_invoice', 'out_invoice', 'entry'] and rec.state != 'posted':
                rec.vendor_bills_readonly_check = True
            super(AccountMove, rec).action_post()
            # rec.asset_id.depreciation_field_population()


    def button_draft(self):
        for rec in self:
            if rec.move_type in ['in_invoice', 'out_invoice', 'entry'] and rec.state == 'posted':
                rec.vendor_bills_readonly_check = False
        super(AccountMove, self).button_draft()