# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError   

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'


    expense_bill_id = fields.Many2one('expense.module', 'Expense Bill', copy=False,)
    

# Ladedcost Analytic
 
class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    _description = 'Valuation Adjustment Lines'
    
    def _create_account_move_line(self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        """
        Generate the account.move.line values to track the landed cost.
        Afterwards, for the goods that are already out of stock, we should create the out moves
        """
        AccountMoveLine = super(AdjustmentLines,self)._create_account_move_line(move, credit_account_id, debit_account_id, qty_out, already_out_account_id)
        AccountMoveLine = []
    

        base_line = {
            'name': str(self.name),
            'product_id': self.product_id.id,
            'quantity': 0,
           
        }
        debit_line = dict(base_line, account_id=debit_account_id)
        credit_line = dict(base_line, account_id=credit_account_id)
        diff = self.additional_landed_cost
        if diff > 0:
            debit_line['debit'] = diff
            credit_line['credit'] = diff
        else:
            # negative cost, reverse the entry
            debit_line['credit'] = -diff
            credit_line['debit'] = -diff
            
        credit_line['analytic_distribution'] = self.cost_line_id.analytic_distribution_landed_cost
        AccountMoveLine.append([0, 0, debit_line])
        AccountMoveLine.append([0, 0, credit_line])

        # Create account move lines for quants already out of stock
        if qty_out > 0:
            debit_line = dict(base_line,
                            name=(self.name + ": " + str(qty_out) + _(' already out')),
                            quantity=0,
                            account_id=already_out_account_id)
            credit_line = dict(base_line,
                            name=(self.name + ": " + str(qty_out) + _(' already out')),
                            quantity=0,
                            account_id=debit_account_id,
                            )
            diff = diff * qty_out / self.quantity
            if diff > 0:
                debit_line['debit'] = diff
                credit_line['credit'] = diff
            else:
                # negative cost, reverse the entry
                debit_line['credit'] = -diff
                credit_line['debit'] = -diff

            AccountMoveLine.append([0, 0, debit_line])
            AccountMoveLine.append([0, 0, credit_line])

            if self.env.company.anglo_saxon_accounting:
                expense_account_id = self.product_id.product_tmpl_id.get_product_accounts()['expense'].id
                debit_line = dict(base_line,
                                name=(self.name + ": " + str(qty_out) + _(' already out')),
                                quantity=0,
                                account_id=expense_account_id)
                credit_line = dict(base_line,
                                name=(self.name + ": " + str(qty_out) + _(' already out')),
                                quantity=0,
                                account_id=already_out_account_id)

                if diff > 0:
                    debit_line['debit'] = diff
                    credit_line['credit'] = diff
                else:
                    # negative cost, reverse the entry
                    debit_line['credit'] = -diff
                    credit_line['debit'] = -diff
                AccountMoveLine.append([0, 0, debit_line])
                AccountMoveLine.append([0, 0, credit_line])
        
        # raise UserError(str(AccountMoveLine))
        return AccountMoveLine
