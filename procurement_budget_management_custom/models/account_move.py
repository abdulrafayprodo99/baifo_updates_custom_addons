from odoo import models,api,fields,_
from odoo.exceptions import UserError
from datetime import date, timedelta


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

            #Rao Abdul Rehman
            purchase_order = rec.env['purchase.order'].search([('name', '=', rec.invoice_origin)], limit=1)
            if not purchase_order:
                budget = self.prepare_positive_budget_move_lines_je(purchase_order=False)
                budget.action_prepared(je_ref=rec)
                # rec.create_budget_management_lines(purchase_order=False)
            else:
                purchase_order.budget_validations()
                if purchase_order.opex_type == 'consumable':
                    rec.create_budget_management_lines(purchase_order)
            #Rao Abdul Rehman

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
    

    def create_budget_management_lines(self, purchase_order=False, reverse=False):
        self.ensure_one()


        if not purchase_order:
            account = self.invoice_line_ids[0].account_id.id

            if isinstance(account, int):
                    account = self.env['account.account'].browse(account)

            budgetary_position = self.env['account.budget.post'].search([
                ('account_ids.code', '=', account.code)
            ], limit=1)

            current_date = fields.Date.context_today(self)
            fiscal_year_start = fields.Date.to_date(f"{current_date.year}-07-01")
            fiscal_year_end = fields.Date.to_date(f"{current_date.year + 1}-06-30")

            budget = self.env['procurement.budget.management'].search([
                ('date_from', '>=', fiscal_year_start),
                ('date_to', '<=', fiscal_year_end),
                ('procurement_lines_ids.budgetary_position_id', '=', budgetary_position.id)
            ], limit=1)


            pos_move_line_vals, neg_move_line_vals, crossovered_budget_lines = self.prepare_positive_budget_move_lines_je(purchase_order=False)
            for crossovered_budget_line, price_total in crossovered_budget_lines:
                crossovered_budget_line.practical_amount += price_total

            budget.budget_move_lines = neg_move_line_vals + pos_move_line_vals


            raise UserError(budget.budget_move_lines.read())

        if reverse and purchase_order:

            budget = purchase_order.get_budget_management()

            pos_move_line_vals, neg_move_line_vals, crossovered_budget_lines = self.reverse_and_remove_budget_move_lines(purchase_order)
            for crossovered_budget_line, price_total in crossovered_budget_lines:
                crossovered_budget_line.practical_amount -= price_total
            
            budget.budget_move_lines = neg_move_line_vals + pos_move_line_vals
        elif purchase_order:
            budget = purchase_order.get_budget_management()
            pos_move_line_vals, neg_move_line_vals, crossovered_budget_lines = self.prepare_positive_budget_move_lines(purchase_order)
            for crossovered_budget_line, price_total in crossovered_budget_lines:
                crossovered_budget_line.practical_amount += price_total

            budget.budget_move_lines = neg_move_line_vals + pos_move_line_vals


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
    #             'budget_consumed_gl': line.price_subtotal,
    #             'pr_budget': 0.0,
    #             'po_budget': 0.0,
    #             'cumulative_budget': cumulative_budget + line.price_subtotal,
    #             'budget_remaining': budget_remaining - line.price_subtotal,
    #             'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
    #             'crossovered_budget_line_id': crossovered_budget_line.id,
    #         }))

    #         crossovered_budget_lines.append([crossovered_budget_line,line.price_subtotal])

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
            cumulative_budget = (last_budget_line.cumulative_budget if last_budget_line else 0.0) - line.price_subtotal
            budget_remaining = (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) + line.price_subtotal
            negative_lines.append((0,0,{
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': f"{self.name}-Knockoff",
                'old_reference': prev_budget_line.reference if prev_budget_line else '',
                'budget_consumed_gl': 0.0,
                'pr_budget': 0.0,
                'po_budget': - line.price_subtotal,
                'cumulative_budget': cumulative_budget ,
                'budget_remaining': budget_remaining,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

            positive_lines.append((0, 0, {
                'budget_approved': crossovered_budget_line.planned_amount,
                'reference': self.name,
                'budget_consumed_gl': line.price_subtotal,
                'pr_budget': 0.0,
                'po_budget': 0.0,
                'cumulative_budget': cumulative_budget + line.price_subtotal,
                'budget_remaining': budget_remaining - line.price_subtotal,
                'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                'crossovered_budget_line_id': crossovered_budget_line.id,
            }))

            crossovered_budget_lines.append([crossovered_budget_line,line.price_subtotal])

        return positive_lines,negative_lines,crossovered_budget_lines

    def prepare_positive_budget_move_lines_je(self,purchase_order=False):
        self.ensure_one()
        positive_lines = []
        negative_lines = []
        crossovered_budget_lines = []

        for line in self.invoice_line_ids:
            if not purchase_order:
                account = line.account_id.id

                if isinstance(account, int):
                    account = line.env['account.account'].browse(account)

                budgetary_position = line.env['account.budget.post'].search([
                    ('account_ids.code', '=', account.code)
                ], limit=1)



                # Get the current date
                current_date = date.today()

                # Calculate the fiscal year start and end dates
                fiscal_year_start = date(current_date.year - 1, 7, 1)
                fiscal_year_end = date(current_date.year, 6, 30)



                budget = line.env['crossovered.budget'].search([
                    ('date_from', '>=', fiscal_year_start),
                    ('date_to', '<=', fiscal_year_end)
                ], limit=1)

                return budget

                # if budget:
                # raise UserError(['rao1', 'budgetary_position', budgetary_position, 'current_date', current_date, 'fiscal_year_start', fiscal_year_start, 'fiscal_year_end', fiscal_year_end])


                # raise UserError(f"Budget: {budget.read()} Budgetary Position: {budgetary_position} date_from: {fiscal_year_start} date_to: {fiscal_year_end}")

                # raise UserError(str(budget.crossovered_budget_line.read()))
            #     for budget_line in budget.crossovered_budget_line:




            #         if budget_line.general_budget_id.id == budgetary_position.id:
            #             crossovered_budget_line = budget_line
            #             break

            #     prev_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            #     last_budget_line = self.env['budget.move.lines'].search([('crossovered_budget_line_id', '=', crossovered_budget_line.id),('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)], order="id desc", limit=1)
            #     cumulative_budget = (last_budget_line.cumulative_budget if last_budget_line else 0.0) - line.price_subtotal
            #     budget_remaining = (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) + line.price_subtotal
            #     negative_lines.append((0,0,{
            #         'budget_approved': crossovered_budget_line.planned_amount,
            #         'reference': f"{self.name}-Knockoff",
            #         'old_reference': prev_budget_line.reference if prev_budget_line else '',
            #         'budget_consumed_gl': 0.0,
            #         'pr_budget': 0.0,
            #         'po_budget': 0.0,
            #         'cumulative_budget': cumulative_budget ,
            #         'budget_remaining': budget_remaining,
            #         'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
            #         'crossovered_budget_line_id': crossovered_budget_line.id,
            #     }))

            #     positive_lines.append((0, 0, {
            #         'budget_approved': crossovered_budget_line.planned_amount,
            #         'reference': self.name,
            #         'budget_consumed_gl': line.price_subtotal,
            #         'pr_budget': 0.0,
            #         'po_budget': 0.0,
            #         'cumulative_budget': cumulative_budget + line.price_subtotal,
            #         'budget_remaining': budget_remaining - line.price_subtotal,
            #         'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
            #         'crossovered_budget_line_id': crossovered_budget_line.id,
            #     }))

            #     crossovered_budget_lines.append([crossovered_budget_line,line.price_subtotal])

            # raise UserError(['positive_lines', positive_lines, 'negative_lines', negative_lines, 'crossovered_budget_lines', crossovered_budget_lines])

            # return positive_lines,negative_lines,crossovered_budget_lines
        

    def reverse_and_remove_budget_move_lines(self, purchase_order):
        self.ensure_one()
        positive_lines = []
        negative_lines = []
        crossovered_budget_lines = []

        for rec in self:
            purchase_order = rec.env['purchase.order'].search([('name', '=', rec.invoice_origin)], limit=1)

            if purchase_order:
            

                for line in self.invoice_line_ids:
                    crossovered_budget_line = purchase_order.get_crossovered_budget_line(line)

                    original_lines = self.env['budget.move.lines'].search([
                        ('reference', '=', self.name),
                        ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                        ('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)
                    ])
                    # original_lines.unlink()

                    last_budget_line = self.env['budget.move.lines'].search([
                        ('crossovered_budget_line_id', '=', crossovered_budget_line.id),
                        ('budgetary_position_id', '=', crossovered_budget_line.general_budget_id.id)
                    ], order="id desc", limit=1)

                    cumulative_budget = (last_budget_line.cumulative_budget if last_budget_line else 0.0) + line.price_subtotal
                    budget_remaining = (last_budget_line.budget_remaining if last_budget_line else crossovered_budget_line.planned_amount) - line.price_subtotal

                    negative_lines.append((0, 0, {
                        'budget_approved': crossovered_budget_line.planned_amount,
                        'reference': f"{self.name}-Reverse",
                        'old_reference': self.name,
                        'budget_consumed_gl': -line.price_subtotal,
                        'pr_budget': 0.0,
                        'po_budget': 0.0,
                        'cumulative_budget': cumulative_budget,
                        'budget_remaining': budget_remaining,
                        'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                        'crossovered_budget_line_id': crossovered_budget_line.id,
                    }))

                    # Reverse the original negative line (PO budget knockoff)
                    positive_lines.append((0, 0, {
                        'budget_approved': crossovered_budget_line.planned_amount,
                        'reference': f"{self.name}-ReverseKnockoff",
                        'old_reference': self.name,
                        'budget_consumed_gl': 0.0,
                        'pr_budget': 0.0,
                        'po_budget': line.price_subtotal,
                        'cumulative_budget': cumulative_budget - line.price_subtotal,
                        'budget_remaining': budget_remaining + line.price_subtotal,
                        'budgetary_position_id': crossovered_budget_line.general_budget_id.id,
                        'crossovered_budget_line_id': crossovered_budget_line.id,
                    }))

                    crossovered_budget_lines.append([crossovered_budget_line, -line.price_subtotal])

                return positive_lines, negative_lines, crossovered_budget_lines




    def button_draft(self):
        # raise UserError("Budget lines reversed successfully.")
        res = super().button_draft()  # Call parent logic first

        for move in self:
            purchase_order = move.env['purchase.order'].search([('name', '=', move.invoice_origin)], limit=1)
            if purchase_order:
                move.create_budget_management_lines(purchase_order, reverse=True)
                # raise UserError("Budget lines reversed successfully.")

        return res