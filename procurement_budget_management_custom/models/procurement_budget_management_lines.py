from odoo import models,api,fields,_
from odoo.exceptions import UserError

class BudgmentManagementLines(models.Model):
    _name = 'procurement.budget.management.lines'
    _description = 'Budget Management Lines'


    budgetary_position_id = fields.Many2one('account.budget.post',string="Budgetary Position")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    analytic_plan_id = fields.Many2one('account.analytic.plan',string="Analytic Plan")
    budget_approved = fields.Float(string='Budget Approved')
    reference = fields.Char(string='Reference')
    old_reference = fields.Char(string='Old Reference')
    budget_consumed = fields.Float(string='Budget Consumed')
    pr_budget = fields.Float(string='PR Budget', compute='_compute_pr_budget')
    po_budget = fields.Float(string='PO Budget')
    invoice_budget =  fields.Float(string='Invoice Budget')
    cumulative_budget = fields.Float(string='Cumulative Budget')
    budget_remaining = fields.Float(string='Budget Remaining')

    budget_id = fields.Many2one('procurement.budget.management', string='Budget ID')

    budget_line_ids = fields.One2many('budget.move.lines', 'budget_line_id', string='Budget Lines')


    def action_open_budget_move_lines(self):
        self.ensure_one()
        return {
            'name': _('Budget Move Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'budget.move.lines',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [
                ('budget_id', '=', self.budget_id.id),
                ('budgetary_position_id', '=', self.budgetary_position_id.id),
            ],
            'views': [(self.env.ref('procurement_budget_management_custom.view_budget_move_lines_tree').id, 'tree')],
            'context': dict(self._context),
        }



    @api.depends('budgetary_position_id')
    def _compute_pr_budget(self):
        for record in self:
            pr_total = 0.0
            po_total = 0.0
            budget_consumed_total = 0.0

            if record.budgetary_position_id:
                matched_lines = self.env['budget.move.lines'].search([
                    ('budget_id', '=', record.budget_id.id),
                    ('budgetary_position_id', '=', record.budgetary_position_id.id),
                ])

                for line in matched_lines:
                    pr_total += line.pr_budget
                    po_total += line.po_budget
                    budget_consumed_total += line.budget_consumed_gl

                # Get only the latest line for cumulative_budget
                latest_line = record.env['budget.move.lines'].search([
                    ('budget_id', '=', record.budget_id.id),
                    ('budgetary_position_id', '=', record.budgetary_position_id.id),
                ], order="id desc", limit=1)

                if latest_line:
                    record.cumulative_budget = latest_line.cumulative_budget
                else:
                    record.cumulative_budget = 0.0
            else:
                record.cumulative_budget = 0.0

            # Assigning other individual budgets
            record.pr_budget = pr_total
            record.po_budget = po_total
            record.budget_consumed = budget_consumed_total

            # Remaining budget based on cumulative
            record.budget_remaining = record.budget_approved - record.cumulative_budget







