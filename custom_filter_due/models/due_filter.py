# models/account_move.py
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_not_overdue = fields.Boolean(
        string="Not Overdue",
        compute="_compute_is_not_overdue",
        store=True,
        index=True
    )

    @api.depends('age_bucket')
    def _compute_is_not_overdue(self):
        for record in self:
            record.is_not_overdue = record.age_bucket == 'Not Due'
