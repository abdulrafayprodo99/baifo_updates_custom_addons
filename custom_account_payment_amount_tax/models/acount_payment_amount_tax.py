from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tax_amount_custom = fields.Float(
        string="Tax Amount",
        compute="_compute_tax_amount_custom",
    )

    @api.depends('amount', 'amount_company_currency_signed')
    def _compute_tax_amount_custom(self):
        for record in self:
            record.tax_amount_custom = record.amount - abs(record.amount_company_currency_signed) if record.amount and record.amount_company_currency_signed else 0.0
