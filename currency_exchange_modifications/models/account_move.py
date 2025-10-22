from odoo import models,api,fields,_,Command
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    exchange_account_move_id_payment = fields.Many2one('account.move',string="Exchange Payment")
    def apply_currency_rate(self):
        for rec in self:
            if rec.currency_rate:
                for line in rec.invoice_line_ids:
                    line.currency_rate = rec.currency_rate
                    qty = line.quantity
                    line.quantity = 0
                    line.quantity = qty
                for line in rec.line_ids:
                    line.currency_rate = rec.currency_rate
                    # if line.amount_currency >= 0 :
                    #     line.debit = abs(line.amount_currency * rec.currency_rate)
                    # if line.amount_currency < 0 :
                    #     line.credit = abs(line.amount_currency * rec.currency_rate)
                     
    def js_assign_outstanding_line(self, line_id):
        ''' Called by the 'payment' widget to reconcile a suggested journal item to the present
        invoice.

        :param line_id: The id of the line to reconcile with the current invoice.
        '''
        self.ensure_one()
        
        lines = self.env['account.move.line'].browse(line_id)
        lines += self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        results =  lines.reconcile()
        if self.currency_id and self.currency_id.name != 'PKR':
            payment_id = self.env['account.move.line'].browse(line_id)
            for rec in results.get('partials'):
                rec.exchange_move_id.exchange_account_move_id_payment = payment_id.move_id
                for line in rec.exchange_move_id.line_ids:
                    line.name = f"{self.name}-{self.amount_total}@{self.currency_rate}/{payment_id.move_name}-{round(abs(payment_id.move_id.payment_id.net_amount),2)}@{payment_id.move_id.currency_rate}"
        return results
    

# class StockValuation(models.Model):
#     _inherit= "stock.valuation.layer"

    # def _validate_accounting_entries(self):
    #     am_vals = []
    #     for svl in self:
    #         if not svl.with_company(svl.company_id).product_id.valuation == 'real_time':
    #             continue
    #         if svl.currency_id.is_zero(svl.value):
    #             continue
    #         move = svl.stock_move_id
    #         if not move:
    #             move = svl.stock_valuation_layer_id.stock_move_id
    #         am_vals += move.with_company(svl.company_id)._account_entry_move(svl.quantity, svl.description, svl.id, svl.value)
        
    #         for i in am_vals:
    #             if i['stock_move_id']:
    #                 st_move = svl.env['stock.move'].browse(i['stock_move_id'])
    #                 i.update({
    #                     'date':st_move.picking_id.date_done or st_move.raw_material_production_id.date_planned_start or st_move.production_id.date_planned_start 
    #                 })
    #     if am_vals:
    #         account_moves = self.env['account.move'].sudo().create(am_vals)
    #         account_moves._post()
    #     for svl in self:
    #         # Eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
    #         if svl.company_id.anglo_saxon_accounting:
    #             svl.stock_move_id._get_related_invoices()._stock_account_anglo_saxon_reconcile_valuation(product=svl.product_id)
                     
