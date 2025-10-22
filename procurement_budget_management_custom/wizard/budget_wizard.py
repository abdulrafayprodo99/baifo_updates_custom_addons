from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class BudgetWizard(models.TransientModel):
    _name = 'procurement.budget.wizard'
    _description = 'Budget Wizard'

    budget = fields.Many2one('procurement.budget.management', string='Budget')
    name = fields.Char(string='Name', readonly=False)
    budget_type = fields.Selection(related='budget.budget_type', string='Budget Type', readonly=False)
    date_from = fields.Date(string='Start Date', readonly=False)
    date_to = fields.Date(string='End Date', readonly=False)

    opex_hide = fields.Boolean(string='Hide Opex', compute='_compute_opex_hide', store=True)

    @api.depends('budget_type')
    def _compute_opex_hide(self):
        for rec in self:
            rec.opex_hide = rec.budget_type == 'capex'

    @api.onchange('budget_type')
    def _onchange_budget_type(self):
        for rec in self:
            rec._compute_opex_hide()


    def action_confirm(self):
        return {'type': 'ir.actions.act_window_close'}
    

    def data(self):
        wizard_budget = self.budget
        wizard_budget_type = self.budget_type
        wizard_start_date = self.date_from
        wizard_end_date = self.date_to
        wizard_budget_lines = wizard_budget.procurement_lines_ids
        procurement_lines = {
            'Plants':[],
            'HO_Admin':[],
            'HO_Distribution':[],
            'Others':[]
             }
        
        total_theoretical_amount = 0

        if wizard_budget_lines:
            for line in wizard_budget_lines:
                budget_start = line.budget_id.date_from
                budget_end = line.budget_id.date_to 
                total_days = (budget_end - budget_start).days + 1 or 1
                days_passed = (wizard_end_date - budget_start).days + 1
                total_days_passed = max(0, min(days_passed, total_days))


                move_lines = self.env['budget.move.lines'].search([
                    ('budget_id', '=', line.budget_id.id),
                    ('budgetary_position_id', '=', line.budgetary_position_id.id),
                    ('create_date', '>=', budget_start),
                    ('create_date', '<=', wizard_end_date),
                ], order='id desc', limit=1)


                if move_lines:
                    budget_approved = move_lines.budget_approved
                    theoretical_amount = (budget_approved / total_days) * days_passed

                    # Determine the category based on the first 4 digits of the account code
                    account_code = move_lines.budgetary_position_id.account_ids[0].code
                    if account_code.startswith('5010'):
                        category = 'Plants'
                    elif account_code.startswith('6010'):
                        category = 'HO_Admin'
                    elif account_code.startswith('6020'):
                        category = 'HO_Distribution'
                    else:
                        category = 'Others'

                    # Append procurement line to the corresponding category
                    procurement_lines[category].append({
                        'budgetary_position': move_lines.budgetary_position_id.name,
                        'category': category,
                        'budget_approved': budget_approved,
                        'cumulative_budget': move_lines.cumulative_budget,
                        'remaining_budget': move_lines.budget_remaining,
                        'theoretical_amount': round(theoretical_amount, 3),
                    })
        total_budget_approved = 0
        total_budget_cumulative = 0
        total_budget_remaining = 0


        for lines in self.budget.procurement_lines_ids:
            total_budget_approved += lines.budget_approved
            total_budget_cumulative += lines.cumulative_budget
            total_budget_remaining += lines.budget_remaining

        total_theoretical_amount = (sum(line['theoretical_amount'] for line in procurement_lines['Plants'])+
            sum(line['theoretical_amount'] for line in procurement_lines['HO_Admin']) +
            sum(line['theoretical_amount'] for line in procurement_lines['HO_Distribution'])+
            sum(line['theoretical_amount'] for line in procurement_lines['Others']))
        

        result = {
            'procurement_id': wizard_budget.name,
            'Type': wizard_budget_type,
            'Start': wizard_start_date,
            'End': wizard_end_date,
            'procurement_line': procurement_lines,
            'budget_approved': total_budget_approved,
            'budget_cumulative': total_budget_cumulative,
            'remaining_budget': total_budget_remaining,
            'theoretical_amount': total_theoretical_amount,
        }


        return result

    
    def print_budget_report(self):

        result = self.data()  
        
        return self.env.ref('procurement_budget_management_custom.action_report_budget').report_action(
            self, 
            data={'result': result}
        )

    # Rao Abdul Rehman
    def capex_data(self):

        # assume self.budget and self.budget_type are already set from the wizard
        record = self.env['procurement.budget.management'].search([
            ('id', '=', self.budget.id),
            ('budget_type', '=', self.budget_type)
        ], limit=1)

        lines = record.procurement_lines_ids

        # 1) Group by analytic account, include plan
        groups = {}
        for line in lines:
            aa = line.analytic_account_id
            plan_name = aa.plan_id.name if aa.plan_id else False

            if aa.id not in groups:
                groups[aa.id] = {
                    'account_name':    aa.name,       # e.g. "Plant" / "Head Office" / "Others"
                    'plan':            plan_name,     # new!
                    'lines':           [],
                    'total_approved':  0.0,
                    'total_cumulative':0.0,
                    'total_variance':  0.0,
                }

            variance = line.budget_approved - line.cumulative_budget
            groups[aa.id]['lines'].append({
                'budget_position': line.budgetary_position_id.name,
                'approved':        line.budget_approved,
                'cumulative':      line.cumulative_budget,
                'variance':        variance,
            })
            groups[aa.id]['total_approved']   += line.budget_approved
            groups[aa.id]['total_cumulative'] += line.cumulative_budget
            groups[aa.id]['total_variance']   += variance

        # 2) Preserve ordering by converting to list
        group_list = list(groups.values())

        # 3) Grand totals
        grand_approved   = sum(g['total_approved']   for g in group_list)
        grand_cumulative = sum(g['total_cumulative'] for g in group_list)
        grand_variance   = sum(g['total_variance']   for g in group_list)

        # 4) Final context for your QWeb
        plans = {}
        for grp in group_list:
            plan = grp.get('plan') or 'No Plan'
            plans.setdefault(plan, []).append(grp)

        # turn into a list, so ordering is kept
        plan_list = [{
            'plan':    plan_name,
            'accounts': plans[plan_name],
        } for plan_name in plans]

        # 5) Bucket analytic_accounts by plan
        report_data = {
            'budget_name':      record.name,
            'budget_type':      record.budget_type,
            # we’ll drop start/end dates per your request
            'total_approved':   grand_approved,
            'total_cumulative': grand_cumulative,
            'total_variance':   grand_variance,
            'plan_groups':      plan_list,
            'grand_total': {
                'approved':   grand_approved,
                'cumulative': grand_cumulative,
                'variance':   grand_variance,
            },
        }

        # raise UserError(str(report_data))

        return report_data

    # Rao Abdul Rehman
    def print_capex_report(self):
        
        report_data = self.capex_data()

        # No extra data needed—just launch the QWeb template
        return self.env.ref('procurement_budget_management_custom.action_report_capex').report_action(
            self, 
            data={'report_data': report_data}
        )
    










