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




    practical_amount = fields.Monetary(
        string='Practical Amount',
        compute='_compute_practical_amount',
    )

    @api.depends(
        'general_budget_id.account_ids',
        'crossovered_budget_id.date_from',
        'crossovered_budget_id.date_to',
    )
    def _compute_practical_amount(self):
        AccountMoveLine = self.env['account.move.line']
        for line in self:
            accounts = line.general_budget_id.account_ids
            date_from = line.crossovered_budget_id.date_from
            date_to = line.crossovered_budget_id.date_to

            if not accounts or not date_from or not date_to:
                line.practical_amount = 0.0
                continue

            domain = [
                ('account_id', 'in', accounts.ids),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('move_id.state', '=', 'posted'),
            ]

            move_lines = AccountMoveLine.search(domain)

            total_debit = sum(move.debit for move in move_lines)
            total_credit = sum(move.credit for move in move_lines)

            line.practical_amount = total_debit - total_credit





class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    hide_update_budget_button = fields.Boolean(string='Hide Update Budget Button') # Rao Abdul Rehman

    def get_crossovered_budget_line(self, line):
        crossovered_budget_line = self.env['crossovered.budget.lines'].search([
            ('crossovered_budget_id', '=', self.id),
            ('general_budget_id.account_ids', 'in', line.account_id.id)
        ], limit=1)

        if not crossovered_budget_line:
            raise UserError("No matching crossovered budget line found.")

        return crossovered_budget_line

    def get_budget_management(self):
        self.ensure_one()

        BudgetManagement = self.env['procurement.budget.management']
        budget = BudgetManagement.search([
            ('name', '=', self.name),
            ('budget_type', '=', self.type)
        ], limit=1)

        if not budget:
            budget = BudgetManagement.create({
                'name': self.name,
                'budget_type': self.type,
                'date_from': self.date_from,
                'date_to': self.date_to,
            })

        existing_positions = budget.procurement_lines_ids.mapped('budgetary_position_id.id')

        procurement_lines = []
        for line in self.crossovered_budget_line:
            if line.general_budget_id.id not in existing_positions:
                procurement_lines.append((0, 0, {
                    'analytic_account_id': line.analytic_account_id.id,
                    'budgetary_position_id': line.general_budget_id.id,
                    'budget_approved': line.planned_amount,
                    'budget_consumed': line.practical_amount,
                    'budget_remaining': line.remaining_budget,
                    'pr_budget': line.pr_budget,
                    'po_budget': line.po_budget,
                }))

        if procurement_lines:
            budget.write({
                'procurement_lines_ids': procurement_lines
            })

        return budget

    def action_prepared(self, je_ref=None):

        #Rao Abdul Rehman
        if je_ref:
            # line_names = []
            for line in je_ref.invoice_line_ids:
                account = line.account_id.code
                budget_post_id = self.env['account.budget.post'].search([
                    ('account_ids.code', '=', account)
                ]).ids
                
                if budget_post_id:
                    # Search all budget.move.line records with those budget position IDs
                    budget_lines = self.env['budget.move.lines'].search([
                        ('budgetary_position_id', '=', budget_post_id)
                    ], order='id desc')  # Assuming 'date' is the field to sort by most recent
                    
                    if budget_lines:
                        most_recent_line = budget_lines[0]

                        existing_budget_id = most_recent_line.budget_id.id
                        existing_budget_approved = most_recent_line.budget_approved
                        existing_cumulative = most_recent_line.cumulative_budget
                        existing_budget_remaining = most_recent_line.budget_remaining
                        existing_crossovered_budget_line_id = most_recent_line.crossovered_budget_line_id.id
                        budgetary_position = most_recent_line.budgetary_position_id.id

                        new_cumulative = existing_cumulative + line.debit


                        self.env['budget.move.lines'].create({
                            'budget_approved': existing_budget_approved,
                            'reference': je_ref.name,
                            'budget_consumed_gl': line.debit,
                            'pr_budget': 0.0,
                            'po_budget': 0.0,
                            'cumulative_budget': new_cumulative,
                            'budget_remaining': existing_budget_approved - new_cumulative,
                            'budgetary_position_id': budgetary_position,
                            'crossovered_budget_line_id': existing_crossovered_budget_line_id,
                            'budget_id': existing_budget_id,
                            'move_line_id': je_ref.id,  # IMPORTANT: add this field to link back
                        })
                        break
                    
        #Rao Abdul Rehman

        else:
            for crossovered_budget_line in self.crossovered_budget_line:
                budgetary_position = crossovered_budget_line.general_budget_id

                if budgetary_position.account_ids:
                    journal_items = self.env['account.move.line'].search([
                        ('account_id', 'in', budgetary_position.account_ids.ids),
                        ('date', '>=', crossovered_budget_line.crossovered_budget_id.date_from),
                        ('date', '<=', crossovered_budget_line.crossovered_budget_id.date_to),
                        ('move_id.state', '=', 'posted')
                    ])

                    move_line_ids = journal_items.ids

                    # Get already existing budget lines for these journal entries
                    existing_lines = self.env['budget.move.lines'].search([
                        ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                        ('budgetary_position_id', '=', budgetary_position.id),
                        ('move_line_id', 'in', move_line_ids)
                    ])

                    existing_move_line_ids = set(existing_lines.mapped('move_line_id.id'))

                    cumulative = 0.0

                    for item in journal_items:
                        if item.id in existing_move_line_ids:
                            continue

                        budget_effect = item.debit - item.credit
                        cumulative += budget_effect

                        budget_id = self.get_budget_management()

                        self.env['budget.move.lines'].create({
                            'budget_approved': crossovered_budget_line.planned_amount,
                            'reference': item.name,
                            'budget_consumed_gl': budget_effect,
                            'pr_budget': 0.0,
                            'po_budget': 0.0,
                            'cumulative_budget': cumulative,
                            'budget_remaining': crossovered_budget_line.planned_amount - cumulative,
                            'budgetary_position_id': budgetary_position.id,
                            'crossovered_budget_line_id': crossovered_budget_line.id,
                            'budget_id': budget_id.id,
                            'move_line_id': item.id,  # IMPORTANT: add this field to link back
                        })


        # Rao Abdul Rehman
        for rec in self:
            rec.hide_update_budget_button = True
        # Rao Abdul Rehman