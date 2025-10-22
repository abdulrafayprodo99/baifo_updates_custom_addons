from odoo import models,api,fields,_
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    budget_estimation_lines = fields.One2many('purchase.budget.estimation.lines','purchase_request_id',string="Budget Estimation ")


    def budget_validations(self):
        for rec in self:
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
            if rec.opex_type == 'consumable':
                rec.create_budget_management_lines()               
        return super(PurchaseRequest, self).action_approve()
        
    def create_budget_management_lines(self):
        self.ensure_one()
        budget = self.get_budget_management()
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

    def get_crossovered_budget_line(self,line):
        crossovered_budget_line = self.env['crossovered.budget.lines'].search([('crossovered_budget_id', '=', self.budget_.id),('general_budget_id.account_ids','in',line.account_id.id)], limit=1)
        if not crossovered_budget_line:
            raise UserError("No matching crossovered budget line found.")
        
        return crossovered_budget_line
    
    def get_budget_management(self):
        self.ensure_one()
        budet_management = self.env['procurement.budget.management']
        budget = budet_management.search([('name', '=', self.budget_.name),('budget_type', '=', self.pr_type)],limit=1)
        if not budget:
            budget = budet_management.create({
                'name': self.budget_.name,
                'budget_type': self.pr_type,
                'date_from': self.budget_.date_from,
                'date_to': self.budget_.date_to,
            })
        return budget
    
    # Override the action_prepare method to compute budget estimation

    def action_prepared(self):
        for rec in self.budget_validations():
            rec.compute_budget_estimation()
        return super(PurchaseRequest, self).action_prepared()

    def compute_budget_estimation(self):
        self.ensure_one()
        budget_estimation_lines = self.prepare_budget_estimation_lines()
        self.budget_estimation_lines = budget_estimation_lines
        
    def prepare_budget_estimation_lines(self):
        self.ensure_one()
        lines = []
        for line in self.line_ids:
            crossovered_budget_line = self.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            lines.append((0, 0, {
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'analytic_account_id': crossovered_budget_line.analytic_account_id.id,
                'budget_approved': crossovered_budget_line.planned_amount,
                'budget_consumed': prev_budget_line.cumulative_budget if prev_budget_line else 0.0,
                'budget_remaining': prev_budget_line.budget_remaining if prev_budget_line else  crossovered_budget_line.planned_amount,
                'purchase_request_id': self.id,
            }))
        return lines
    

from odoo import models, api
from odoo.exceptions import ValidationError

class RfqComparison(models.Model):
    _inherit = 'rfq.comparison'

    def action_prepared(self):
        for rec in self:
            # Check PR Details
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

            # Check PO Details
            for po_detail in rec.po_detail_ids:
                matching_line = rec.purchase_request_id.line_ids.filtered(
                    lambda line: line.product_id == po_detail.product_id
                )
                if not matching_line:
                    continue

                # for line in matching_line:
                #     if po_detail.product_qty > line.product_qty:
                #         raise ValidationError(
                #             f"The quantity for product {po_detail.product_id.display_name} "
                #             f"({po_detail.product_qty}) exceeds the requested quantity "
                #             f"({line.product_qty})."
                #         )

        return super(RfqComparison, self).action_prepared()
