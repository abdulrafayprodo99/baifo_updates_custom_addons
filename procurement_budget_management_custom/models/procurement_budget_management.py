from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProcurementBudgetManagement(models.Model):
    _name = 'procurement.budget.management'
    _description = 'Budget Management'

    name = fields.Char(string='Budget Name')
    budget_type= fields.Selection([
        ('capex', 'Capex'),
        ('opex', 'Opex'),
    ], string='Type')
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    budget_move_lines = fields.One2many('budget.move.lines', 'budget_id', string='Budget Move Lines')
    procurement_lines_ids = fields.One2many('procurement.budget.management.lines', 'budget_id', string='Procurement Lines')

