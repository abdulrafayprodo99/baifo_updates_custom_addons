from odoo import models,api,fields,_
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    budget_estimation_lines = fields.One2many('purchase.budget.estimation.lines','purchase_request_id',string="Budget Estimation ")


    def budget_validations(self):
        for rec in self:
            if rec.pr_type == 'opex' and rec.opex_type == 'production':
                return self
            if not rec.budget_ or not rec.pr_type:
                raise UserError(_("Please set the budget and budget type for this purchase request."))
            if rec.pr_type == 'opex' and not rec.opex_type and not rec.opex_sub_type:
                raise UserError(_("Please set the opex type and sub type for this purchase request."))
            if rec.pr_type == 'capex' and not rec.capex_type:
                raise UserError(_("Please set the capex type for this purchase request."))
        return self
   
    # Override the action_approve method to include budget management lines creation 

    def action_approve(self):
        for rec in self.budget_validations():
            rec.plant_state = 'approve'
            # M Azeem commented below Task: 42173
            # if rec.opex_type != 'production':
            #     rec.create_budget_management_lines()               
        return super(PurchaseRequest, self).action_approve()

        
    def create_budget_management_lines(self, reverse=False):
        self.ensure_one()
        budget = self.get_budget_management()

        if reverse:
            move_line_vals = self.prepare_reverse_budget_move_lines()
        else:
            move_line_vals = self.prepare_budget_move_lines()

        budget.budget_move_lines = move_line_vals


    def prepare_budget_move_lines(self):
        self.ensure_one()
        lines = []
        for line in self.line_ids:
            crossovered_budget_line = self.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': self.name,
                # 'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': 0.0,
                'pr_budget': line.estimated_cost,
                'po_budget': 0.0,
                'cumulative_budget': (prev_budget_line.cumulative_budget if prev_budget_line else 0.0) + line.estimated_cost,
                'budget_remaining': (prev_budget_line.budget_remaining if prev_budget_line else crossovered_budget_line.planned_amount) - line.estimated_cost,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))
        return lines

    def prepare_reverse_budget_move_lines(self):
        self.ensure_one()

        # Fetch all Purchase Orders linked to this Purchase Request
        purchase_orders = self.env['purchase.order'].search([('purchase_request_id', '=', self.id)])

        # Check if all are in draft state
        not_draft_pos = purchase_orders.filtered(lambda po: po.state != 'draft')
        if not_draft_pos:
            po_names = ', '.join(not_draft_pos.mapped('name'))
            raise UserError(_(
                f"Cannot reverse budget because the following Purchase Orders are not in draft state: {po_names}"
            ))

        reversed_lines = []

        for line in self.line_ids:
            crossovered_budget_line = self.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([
                ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                ('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)
            ], order="id desc", limit=1)

            reversed_lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.name}-Reverse",
                'budget_consumed_gl': 0.0,
                'pr_budget': -line.estimated_cost,
                'po_budget': 0.0,
                'cumulative_budget': (prev_budget_line.cumulative_budget if prev_budget_line else 0.0) - line.estimated_cost,
                'budget_remaining': (prev_budget_line.budget_remaining if prev_budget_line else crossovered_budget_line.planned_amount) + line.estimated_cost,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

        return reversed_lines


    def get_crossovered_budget_line(self,line):
        crossovered_budget_line = self.env['crossovered.budget.lines'].search([('crossovered_budget_id', '=', self.budget_.id),('general_budget_id.account_ids','in',line.account_id.id)], limit=1)
        if not crossovered_budget_line:
            raise UserError("No matching crossovered budget line found.")
        
        return crossovered_budget_line
    
    def get_budget_management(self):
        self.ensure_one()
        BudgetManagement = self.env['procurement.budget.management']
        budget = BudgetManagement.search([
            ('name', '=', self.budget_.name),
            ('budget_type', '=', self.pr_type)
        ], limit=1)

        if not budget:
            budget = BudgetManagement.create({
                'name': self.budget_.name,
                'budget_type': self.pr_type,
                'date_from': self.budget_.date_from,
                'date_to': self.budget_.date_to,
            })

        existing_positions = budget.procurement_lines_ids.mapped('budgetary_position_id.id')

        procurement_lines = []
        for line in self.budget_.crossovered_budget_line:
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

    
    # Override the action_prepare method to compute budget estimation

    def action_prepared(self):
        res = super(PurchaseRequest, self).action_prepared() # M Azeem Task: 42173
        for rec in self.budget_validations():
            if rec.opex_type != 'production':
                # M Azeem added two line below Task: 42173
                rec.compute_budget_estimation()
                rec.create_budget_management_lines()
        return res

    # def compute_budget_estimation(self):
    #     self.ensure_one()
    #     budget_estimation_lines = self.prepare_budget_estimation_lines()
    #     self.budget_estimation_lines = budget_estimation_lines


    def compute_budget_estimation(self):
        self.ensure_one()
        budget_estimation_lines = self.prepare_budget_estimation_lines()

        existing_lines = {(line.budgetary_position_id.id, line.analytic_account_id.id): line for line in self.budget_estimation_lines}

        for vals in budget_estimation_lines:
            budget_pos_id = vals[2]['budgetary_position_id']
            analytic_id = vals[2]['analytic_account_id']
            key = (budget_pos_id, analytic_id)

            if key in existing_lines:
                # Update existing line
                existing_line = existing_lines[key]
                existing_line.budget_approved = vals[2]['budget_approved']
                existing_line.budget_consumed = vals[2]['budget_consumed']
                existing_line.budget_remaining = vals[2]['budget_remaining']
            else:
                # Add new line
                self.budget_estimation_lines += self.env['purchase.budget.estimation.lines'].new(vals[2])

        
    # def prepare_budget_estimation_lines(self):
    #     self.ensure_one()
    #     lines = []
    #     for line in self.line_ids:
    #         crossovered_budget_line = self.get_crossovered_budget_line(line)
    #         prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
    #         lines.append((0, 0, {
    #             'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
    #             'analytic_account_id': crossovered_budget_line.analytic_account_id.id,
    #             'budget_approved': crossovered_budget_line.planned_amount,
    #             'budget_consumed': prev_budget_line.cumulative_budget if prev_budget_line else 0.0,
    #             'budget_remaining': prev_budget_line.budget_remaining if prev_budget_line else  crossovered_budget_line.planned_amount,
    #             'purchase_request_id': self.id,
    #         }))
    #     return lines


    def prepare_budget_estimation_lines(self):
        self.ensure_one()
        lines = []
        for line in self.line_ids:
            crossovered_budget_line = self.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([
                ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                ('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)
            ], order="id desc", limit=1)

            lines.append((0, 0, {
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'analytic_account_id': crossovered_budget_line.analytic_account_id.id,
                'budget_approved': crossovered_budget_line.planned_amount,
                'budget_consumed': prev_budget_line.cumulative_budget if prev_budget_line else 0.0,
                'budget_remaining': prev_budget_line.budget_remaining if prev_budget_line else crossovered_budget_line.planned_amount,
                'purchase_request_id': self.id,
            }))
        return lines



    # def action_prepared(self):
    #     self.ensure_one()

    #     super(PurchaseRequest, self).action_prepared()
    #     for line in self.line_ids:
    #         crossovered_budget_line = self.get_crossovered_budget_line(line)
    #         budgetary_position = crossovered_budget_line.general_budget_id

    #         if budgetary_position.account_ids:
    #             journal_items = self.env['account.move.line'].search([
    #                 ('account_id', 'in', budgetary_position.account_ids.ids),
    #                 ('date', '>=', crossovered_budget_line.crossovered_budget_id.date_from),
    #                 ('date', '<=', crossovered_budget_line.crossovered_budget_id.date_to),
    #                 ('move_id.state', '=', 'posted')
    #             ])

    #             cumulative = 0.0
    #             remaining = crossovered_budget_line.remaining_budget

    #             for item in journal_items:
    #                 budget_effect = item.debit - item.credit  
    #                 cumulative += budget_effect
    #                 remaining -= budget_effect

    #                 already_exists = self.env['budget.move.lines'].search_count([
    #                     ('reference', '=', item.move_id.name),
    #                     ('budget_consumed_gl', '=', budget_effect),
    #                     ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
    #                     ('budgetary_position_id', '=', budgetary_position.id),
    #                 ])

    #                 if already_exists:
    #                     continue  # Skip duplicate

    #                 budget_id = self.get_budget_management()

    #                 self.env['budget.move.lines'].create({
    #                     'budget_approved': crossovered_budget_line.planned_amount,
    #                     'reference': item.move_id.name,
    #                     'budget_consumed_gl': budget_effect,
    #                     'pr_budget': 0.0,
    #                     'po_budget': 0.0,
    #                     'cumulative_budget': cumulative,
    #                     'budget_remaining': remaining,
    #                     'budgetary_position_id': budgetary_position.id,
    #                     'crossovered_budget_line_id': crossovered_budget_line.id,
    #                     'budget_id': budget_id.id,
    #                 })
    #     for rec in self.budget_validations():
    #         rec.compute_budget_estimation()


from odoo import fields, models
from odoo.exceptions import UserError

class RejectionNote(models.TransientModel):
    _inherit = 'cancel.wizard'

    def pr_cancel(self, pr):
        pr.create_budget_management_lines(reverse=True)
        # Cancel the PR
        pr.action_cancel()



from odoo import models, api
from odoo.exceptions import ValidationError

class RfqComparison(models.Model):
    _inherit = 'rfq.comparison'

    def action_prepared(self):
        for rec in self:
            for pr_detail in rec.pr_detail_ids:
                matching_line = rec.purchase_request_id.line_ids.filtered(
                    lambda line: line.product_id == pr_detail.product_id
                )
                if not matching_line:
                    continue

                # for line in matching_line:
                #     if pr_detail.product_qty > line.product_qty:
                #         raise ValidationError(
                #             f"The quantity for product {pr_detail.product_id.display_name} "
                #             f"({pr_detail.product_qty}) exceeds the requested quantity "
                #             f"({line.product_qty})."
                #         )

        return super(RfqComparison, self).action_prepared()





from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.constrains('product_qty', 'price_unit')
    def _check_qty_and_price(self):
        for line in self:
            if line.product_qty <= 0:
                raise ValidationError("Product quantity must be greater than 0.")
            if line.price_unit <= 0:
                raise ValidationError("Unit price must be greater than 0.")

