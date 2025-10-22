from odoo import models,api,fields,_
from odoo.exceptions import UserError

class PurchaseBudgetEstimationLines(models.Model):
    _name = 'purchase.budget.estimation.lines'
    _description = 'Purchase Budget Estimation Lines'

    budgetary_position_id = fields.Many2one('account.budget.post',string="Budgetary Position")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    budget_approved = fields.Float(string='Budget Approved')
    budget_consumed = fields.Float(string='Budget Consumed')
    budget_remaining = fields.Float(string='Budget Remaining')
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request ID')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order ID')