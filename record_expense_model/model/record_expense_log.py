from odoo import api, models, fields
from odoo.exceptions import UserError

class ExpenseInherit(models.Model):
    _inherit = "expense.module"

    prepared_by = fields.Many2one("res.users", string="Prepared by", copy=False)
    prepared_timestamp = fields.Datetime(string="Prepare Timestamp", readonly=True, copy=False)
    verify_by = fields.Many2one("res.users", string="Verify by", copy=False)
    verify_timestamp = fields.Datetime(string="Verify Timestamp", readonly=True, copy=False)
    Approve_by = fields.Many2one("res.users", string="Approved by", copy=False)
    approve_timestamp = fields.Datetime(string="Approve Timestamp", readonly=True, copy=False)

    def action_prepared_expense(self):
        # super
        for rec in self:
            # if rec.payment_type == 'Bank Payment':
            rec.prepared_by = self.env.user
            rec.prepared_timestamp = fields.Datetime.now()
        super(ExpenseInherit, self).action_prepared_expense()

    def action_verify_expense(self):
        for rec in self:
            rec.verify_by = self.env.user
            rec.verify_timestamp = fields.Datetime.now()
        super(ExpenseInherit, self).action_verify_expense()

    def action_approve_expense(self):
        for rec in self:
            rec.Approve_by = self.env.user
            rec.approve_timestamp = fields.Datetime.now()
        super(ExpenseInherit, self).action_approve_expense()
