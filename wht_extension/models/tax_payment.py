# models/inherit_payment_wht_line.py

from odoo import models, fields, api
from datetime import timedelta

class PaymentWHTLine(models.Model):
    _inherit = 'payment.wht.line'

    cheque_no = fields.Char(related='payment_id.cheque_number', store=True, readonly=True)
    total_amount = fields.Monetary(related='payment_id.amount', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='payment_id.currency_id', readonly=True)
    due_date = fields.Date(compute='_compute_due_date', store=True)
    doc_no = fields.Char(string="Doc No.")
    challan_no  = fields.Char(strign="Challan No.")
    bank_name = fields.Char(string='Bank')
    branch = fields.Char(string='Branch')
    cheque_to_be_issued = fields.Char(string='Cheque # Issued')
    tax_date = fields.Date(strign='Tax Date')
    cprm_no = fields.Char(string='CPRM No.')

    account_type = fields.Selection(
        related='account_id.account_type',
        string='Account Type',
        store=True,
        readonly=True
    )

    tax_description = fields.Char(
        related='tax_id.description',
        string='Description',
        store=True,
        readonly=True
    )

    vendor = fields.Many2one(
        related='payment_id.partner_id',
        string='Vendor',
        store=True,
        readonly=True
    )

    tax_group = fields.Many2one(
        related='tax_id.tax_group_id',
        string='Tax Group',
        store=True,
        readonly=True
    )

    @api.depends('payment_id.date')
    def _compute_due_date(self):
        for line in self:
            if line.payment_id.date:
                line.due_date = line.payment_id.date + timedelta(days=7)



