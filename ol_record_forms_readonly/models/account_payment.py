from odoo import models, fields
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    vendor_payment_readonly_check = fields.Boolean(string="Vendor Payment Readonly Check")

    def action_post(self):
        # super
        # raise UserError('hit Aliii')
        if self.payment_type in ['outbound', 'inbound'] and self.state != 'posted':
            for rec in self:
                rec.vendor_payment_readonly_check = True
        super(AccountPayment, self).action_post()

    def action_draft(self):
        # super
        if self.payment_type in ['outbound', 'inbound'] and self.state == 'posted':
            for rec in self:
                rec.vendor_payment_readonly_check = False
        super(AccountPayment, self).action_draft()