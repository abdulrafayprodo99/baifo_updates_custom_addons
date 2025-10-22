from odoo import models,api,fields,_
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit="account.move"

    def action_post(self):
        """
        Override the action_post method to include budget management logic
        when posting an invoice.
        """
        # Call the original action_post method
        res = super(AccountMove, self).action_post()
        for rec in self:
            purchase_order = rec.env['purchase.order'].search([('name', '=', rec.invoice_origin)], limit=1)
            purchase_order.budget_validations()
            if purchase_order.opex_type == 'consumable':
                rec.create_budget_management_lines(purchase_order)

        return res
    
    # def button_draft(self):
    #     """
    #     Override the button_draft method to include budget management logic
    #     when reverting an invoice.
    #     """
    #     # Call the original button_draft method
    #     res = super(AccountMove, self).button_draft()
    #     for rec in self:
    #         purchase_order = rec.env['purchase.order'].search([('name', '=', rec.invoice_origin)], limit=1)
    #         purchase_order.budget_validations()
    #         if purchase_order.opex_type == 'consumable':
    #             rec.create_budget_management_lines(purchase_order)

    #     return res
    

    def create_budget_management_lines(self,purchase_order):
        self.ensure_one()
        budget = purchase_order.get_budget_management()
        pos_move_line_vals,neg_move_line_vals,crossovered_budget_lines = self.prepare_positive_budget_move_lines(purchase_order)
        budget.budget_move_lines = neg_move_line_vals + pos_move_line_vals
        
        for crossovered_budget_line,price_total in crossovered_budget_lines:
            crossovered_budget_line.practical_amount = crossovered_budget_line.practical_amount + price_total

    # def prepare_positive_budget_move_lines(self,purchase_order):
    #     self.ensure_one()
    #     positive_lines = []
    #     negative_lines = []
    #     crossovered_budget_lines = []
    #     for line in self.invoice_line_ids:
    #         crossovered_budget_line = purchase_order.get_crossovered_budget_line(line)
    #         prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id),('reference','=',purchase_order.rfq_sequence)], order="id desc", limit=1)
    #         last_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
    #         cumulative_budget = (last_budget_line.cumulative_budget if last_budget_line else 0.0) - prev_budget_line.po_budget
    #         budget_remaining = (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) + prev_budget_line.po_budget
    #         negative_lines.append((0,0,{
    #             'budget_approved': crossovered_budget_line.planned_amount,
    #             'reference': f"{self.name}-Knockoff",
    #             'old_reference': prev_budget_line.reference if prev_budget_line else '',
    #             'budget_consumed_gl': 0.0,
    #             'pr_budget': 0.0,
    #             'po_budget': - prev_budget_line.po_budget,
    #             'cumulative_budget': cumulative_budget ,
    #             'budget_remaining': budget_remaining,
    #             'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
    #             'crossovered_budget_line_id': crossovered_budget_line.id,
    #         }))

    #         positive_lines.append((0, 0, {
    #             'budget_approved': crossovered_budget_line.planned_amount,
    #             'reference': self.name,
    #             # 'old_reference': prev_budget_line.reference if prev_budget_line else '',
    #             'budget_consumed_gl': line.price_total,
    #             'pr_budget': 0.0,
    #             'po_budget': 0.0,
    #             'cumulative_budget': cumulative_budget + line.price_total,
    #             'budget_remaining': budget_remaining - line.price_total,
    #             'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
    #             'crossovered_budget_line_id': crossovered_budget_line.id,
    #         }))

    #         crossovered_budget_lines.append([crossovered_budget_line,line.price_total])

    #     return positive_lines,negative_lines,crossovered_budget_lines
        


    def prepare_positive_budget_move_lines(self,purchase_order):
        self.ensure_one()
        positive_lines = []
        negative_lines = []
        crossovered_budget_lines = []
        for line in self.invoice_line_ids:
            crossovered_budget_line = purchase_order.get_crossovered_budget_line(line)
            prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id),('reference','=',purchase_order.rfq_sequence)], order="id desc", limit=1)
            last_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            cumulative_budget = (last_budget_line.cumulative_budget if last_budget_line else 0.0) - line.price_total
            budget_remaining = (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) + line.price_total
            # raise UserError([cumulative_budget,budget_remaining])
            negative_lines.append((0,0,{
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.name}-Knockoff",
                'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': 0.0,
                'pr_budget': 0.0,
                'po_budget': - line.price_total,
                'cumulative_budget': cumulative_budget ,
                'budget_remaining': budget_remaining,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

            positive_lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': self.name,
                # 'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': line.price_total,
                'pr_budget': 0.0,
                'po_budget': 0.0,
                'cumulative_budget': cumulative_budget + line.price_total,
                'budget_remaining': budget_remaining - line.price_total,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

            crossovered_budget_lines.append([crossovered_budget_line,line.price_total])

        return positive_lines,negative_lines,crossovered_budget_lines
        