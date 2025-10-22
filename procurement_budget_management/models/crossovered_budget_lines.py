from odoo import models,api,fields,_
from odoo.exceptions import UserError

class CrossOveredBudgetLines(models.Model):
    _inherit="crossovered.budget.lines"

    remaining_budget = fields.Float(string='Remaining Budget', compute='_compute_remaining_budget', store=True)

    

    @api.depends('planned_amount', 'practical_amount')
    def _compute_remaining_budget(self):
        for line in self:
            remaining_budget = line.planned_amount - line.practical_amount
            # if remaining_budget < 0:
            #     raise UserError(_("Consumed budget cannot be greater than planned amount."))
            
            line.remaining_budget = remaining_budget