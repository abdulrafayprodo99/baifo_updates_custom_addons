from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    age_bucket = fields.Char(
        string='Aging Bucket',
        compute='_compute_age_bucket',
        store=True
    )

    @api.depends('invoice_date_due', 'invoice_date')
    def _compute_age_bucket(self):
        """
        Compute the age bucket based on the difference between the due date
        and the current date. If the due date crosses the current date, 
        categorize the record in an aging bucket.
        """
        today = fields.Date.today()
        for move in self:
            # Ensure the due date is available
            if move.invoice_date_due:
                # Calculate days overdue (if negative, it hasn't crossed the due date yet)
                due_days = (today - move.invoice_date_due).days
                move.age_bucket = self._get_aging_bucket(due_days)
            else:
                # If no due date, treat as "Not Due"
                move.age_bucket = "Not Due"

    def _get_aging_bucket(self, due_days):
        """
        Map the number of days overdue to an aging bucket.
        """
        if due_days <= 0:
            return 'Not Due'
        elif 1 <= due_days <= 15:
            return '1-15 Days'
        elif 16 <= due_days <= 30:
            return '16-30 Days'
        elif 31 <= due_days <= 45:
            return '31-45 Days'
        elif 46 <= due_days <= 60:
            return '46-60 Days'
        elif 61 <= due_days <= 75:
            return '61-75 Days'
        elif 75 < due_days:
            return '75+ Days'
