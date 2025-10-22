from odoo import models,fields,api,_
from odoo.exceptions import UserError

class BudgetMoveLines(models.Model):
    _name = 'budget.move.lines'
    _description = 'Budget Move Lines'

    budget_approved = fields.Float(string='Budget Approved')
    reference = fields.Char(string='Reference')
    old_reference = fields.Char(string='Old Reference')
    budget_consumed_gl = fields.Float(string='Budget Consumed')
    pr_budget = fields.Float(string='PR Budget')
    po_budget = fields.Float(string='PO Budget')
    invoice_budget =  fields.Float(string='Invoice Budget')
    cumulative_budget = fields.Float(string='Cumulative Budget')
    budget_remaining = fields.Float(string='Budget Remaining')
    
    budget_id = fields.Many2one('procurement.budget.management', string='Budget ID')
    crossovered_budget_line_id = fields.Many2one('crossovered.budget.lines', string='Crossovered Budget Line ID')
    budgetary_position_id = fields.Many2one('account.budget.post', string='Budgetary Position ID')

    @api.constrains('budget_approved','cumulative_budget')
    def _check_budget_approved(self):
        for record in self:
            if record.budget_approved < 0:
                raise UserError(_("Budget Approved cannot be negative."))
            if record.cumulative_budget > record.budget_approved:
                raise UserError(_("Cumulative Budget cannot exceed Budget Approved."))