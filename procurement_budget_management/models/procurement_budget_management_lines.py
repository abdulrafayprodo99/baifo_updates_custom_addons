from odoo import models,api,fields,_
from odoo.exceptions import UserError

class BudgmentManagementLines(models.Model):
    _name = 'procurement.budget.management.lines'
    _description = 'Procurement Budget Management Lines'


    budgetary_position_id = fields.Many2one('account.budget.post',string="Budgetary Position")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    analytic_plan_id = fields.Many2one('account.analytic.plan',string="Analytic Plan")
    budget_approved = fields.Float(string='Budget Approved')
    reference = fields.Char(string='Reference')
    old_reference = fields.Char(string='Old Reference')
    budget_consumed = fields.Float(string='Budget Consumed')
    pr_budget = fields.Float(string='PR Budget')
    po_budget = fields.Float(string='PO Budget')
    invoice_budget =  fields.Float(string='Invoice Budget')
    cumulative_budget = fields.Float(string='Cumulative Budget')
    budget_remaining = fields.Float(string='Budget Remaining')

    budget_id = fields.Many2one('procurement.budget.management', string='Budget ID')