from odoo import models,api,fields,_
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    budget_id =  fields.Many2one('crossovered.budget', string='Budget',compute="_compute_budget_id",store=True)
    
    budget_estimation_lines = fields.One2many('purchase.budget.estimation.lines','purchase_order_id',string="Budget Estimation ")
    
    @api.depends('purchase_request_id')
    def _compute_budget_id(self):
        for rec in self:
            if rec.purchase_request_id:
                rec.budget_id = rec.purchase_request_id.budget_.id
            else:
                rec.budget_id = False
    
    def budget_validations(self):
        if not self.purchase_request_id:
            raise UserError(_("Please set the purchase request for this purchase order."))
        if not self.budget_id or not self.pr_type:
            raise UserError(_("Please set the budget and budget type for this purchase order."))
        if self.pr_type == 'opex' and not self.opex_type and not self.opex_sub_type:
            raise UserError(_("Please set the opex type and sub type for this purchase order."))
        if self.pr_type == 'capex' and not self.capex_type:
            raise UserError(_("Please set the capex type for this purchase order."))
        return self
    
    def action_approve(self):
        for rec in self:
            rec.budget_validations()
            if rec.opex_type != 'production':
                rec.create_budget_management_lines()               
        return super(PurchaseOrder, self).action_approve()

    def get_budget_management(self):
        self.ensure_one()
        BudgetManagement = self.env['procurement.budget.management']
        budget = BudgetManagement.search([
            ('name', '=', self.budget_id.name),
            ('budget_type', '=', self.pr_type)
        ], limit=1)

        if not budget:
            budget = BudgetManagement.create({
                'name': self.budget_id.name,
                'budget_type': self.pr_type,
                'date_from': self.budget_id.date_from,
                'date_to': self.budget_id.date_to,
            })

        existing_positions = budget.procurement_lines_ids.mapped('budgetary_position_id.id')

        procurement_lines = []
        for line in self.budget_id.crossovered_budget_line:
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


    def get_crossovered_budget_line(self,line):
        crossovered_budget_line = self.env['crossovered.budget.lines'].search([('crossovered_budget_id', '=', self.budget_id.id),('general_budget_id.account_ids','in',self.get_account_id(line))], limit=1)
        if not crossovered_budget_line:
            raise UserError("No matching crossovered budget line found.")
        return crossovered_budget_line
    
    def get_account_id(self,line):
        return self.purchase_request_id.line_ids.filtered(lambda l:l.product_id.id == line.product_id.id).mapped('account_id').id
    

    def create_budget_management_lines(self, reverse=False):
        self.ensure_one()
        budget = self.get_budget_management()

        if reverse:
            # Prepare reversed budget lines
            reversed_move_line_vals = self.prepare_reverse_budget_move_lines()
            budget.budget_move_lines = reversed_move_line_vals
        else:
            # Prepare normal budget move lines
            pos_move_line_vals, neg_move_line_vals = self.prepare_positive_budget_move_lines()
            budget.budget_move_lines = neg_move_line_vals + pos_move_line_vals


    def prepare_positive_budget_move_lines(self):
        self.ensure_one()
        positive_lines = []
        negative_lines = []
        for line in self.order_line:
            crossovered_budget_line = self.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id),('reference','=',self.purchase_request_id.name)], order="id desc", limit=1)
            last_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            cumulative_budget = (last_budget_line.cumulative_budget if last_budget_line else 0.0) - prev_budget_line.pr_budget
            budget_remaining = (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) + prev_budget_line.pr_budget
            negative_lines.append((0,0,{
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.name}-Knockoff",
                'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': 0.0,
                'pr_budget': - prev_budget_line.pr_budget,
                'po_budget': 0.0,
                'cumulative_budget': cumulative_budget ,
                'budget_remaining': budget_remaining,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

            positive_lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': self.name,
                # 'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': 0.0,
                'pr_budget': 0.0,
                'po_budget': line.price_subtotal,
                'cumulative_budget': cumulative_budget + line.price_subtotal,
                'budget_remaining': budget_remaining - line.price_subtotal,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))
        return positive_lines,negative_lines
    

    def prepare_negative_budget_move_lines(self):
        self.ensure_one()
        lines=[]
        for line in self.order_line:
            crossovered_budget_line = self.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id),('reference','=',self.purchase_request_id.name)], order="id desc", limit=1)
            last_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.name}-Knockoff",
                'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': 0.0,
                'pr_budget': - prev_budget_line.pr_budget,
                'po_budget': 0.0,
                'cumulative_budget': (last_budget_line.cumulative_budget if last_budget_line else 0.0) - prev_budget_line.pr_budget,
                'budget_remaining': (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) + prev_budget_line.pr_budget,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))
        return lines





    def prepare_reverse_budget_move_lines(self):
        # self.ensure_one()

        # for rec in self:

        #     # raise UserError(self.name)

        #     bills = rec.env['account.move'].search([
        #         ('origin_name', '=', rec.name),
        #         ('state', '!=', 'cancel'),
        #         ('move_type', '=', 'in_invoice')
        #     ])

        #     raise UserError(str(bills))

        #     not_draft_bills = bills.filtered(lambda m: m.state != 'draft')
        #     if not_draft_bills:
        #         bill_names = ', '.join(not_draft_bills.mapped('name'))
        #         raise UserError(_(
        #             f"Cannot reverse budget because the following Vendor Bills are not in draft state: {bill_names}"
        #         ))

        reversed_lines = []

        for line in self.order_line:
            crossovered_budget_line = self.get_crossovered_budget_line(line)

            current_budget_line = self.env['budget.move.lines'].search([
                ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                ('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id),
                '|', 
                ('reference', '=', self.rfq_sequence),
                ('reference', '=', self.name),
            ], order="id desc", limit=1)

            knockoff_line = self.env['budget.move.lines'].search([
                ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                ('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id),
                '|', 
                ('reference', '=', f"{self.rfq_sequence}-Knockoff"),
                ('reference', '=', f"{self.name}-Knockoff"),
            ], order="id desc", limit=1)

            if not current_budget_line or not knockoff_line:
                continue

            # Reverse PO impact
            reversed_lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.rfq_sequence}-ReversePO",
                'budget_consumed_gl': 0.0,
                'pr_budget': 0.0,
                'po_budget': -line.price_subtotal,
                'cumulative_budget': current_budget_line.cumulative_budget - line.price_subtotal,
                'budget_remaining': current_budget_line.budget_remaining + line.price_subtotal,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

            # Reverse Knockoff impact
            reversed_lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.rfq_sequence}-ReverseKnockoff",
                'old_reference': knockoff_line.old_reference,
                'budget_consumed_gl': 0.0,
                'pr_budget': -knockoff_line.pr_budget,
                'po_budget': 0.0,
                'cumulative_budget': knockoff_line.cumulative_budget + abs(knockoff_line.pr_budget),
                'budget_remaining': abs(knockoff_line.budget_remaining) - abs(knockoff_line.pr_budget),
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

        return reversed_lines



    
    def button_draft(self):
        self.ensure_one()
        self.create_budget_management_lines(reverse=True)
        self.write({'state': 'draft'})
        return {}



from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CancelPOWizard(models.TransientModel):
    _inherit = 'cancel.po.wizard'


    def action_confirm(self):
            # raise UserError(_("Please set the purchase request for this purchase order."))
            # Get the active purchase order
            purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))

            # Reverse the budget lines
            # purchase_order.create_budget_management_lines(reverse=True)

            # Reset stock moves to draft if they're in 'done' state
            for order in purchase_order:
                for move in order.order_line.mapped('move_ids'):
                    if move.state == 'done':
                        move.state = 'draft'

            # Now call the original method to handle close_reason, state update, and window close
            return super().action_confirm()