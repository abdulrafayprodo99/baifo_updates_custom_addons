from odoo import api,models,fields
from odoo.exceptions import UserError
import datetime
import base64

class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'
    
    def action_draft(self):
        res = super(InheritAccountPayment,self).action_draft()
        self.reset_prepared_entry()
        
    def reset_prepared_entry(self):
        for rec in self:
            # if not rec.approval_state_customer_payment:
            rec['approval_state_customer_payment']=False
            rec['approval_state']=False
            rec['prepare_customer_payment'] = False
            rec['prepare_customer_payment_timestamp'] = False
            rec['readonly_check'] = False
            
            # amount = rec.amount
            
            
            rec.reset_journal_items()
            rec['wht_line_ids'] = False    
    
    def reset_journal_items(self):
        debit_line = False
        credit_line = False
        
        if self.payment_type == 'inbound':
            for tax in self.wht_line_ids:
                for line in self.move_id.line_ids:
                    if line.credit == 0:
                        if not line.account_id.is_tax:
                            debit_line = line
                            # line['debit'] = rec.amount
                        else:
                            if tax.name == line.name:
                                # raise UserError('here')
                                tax_amount = line['debit']
                                # new_amnt = debit_line.debit
                                vals = {'line_ids': [(1,debit_line.id, {'debit': debit_line.debit + tax_amount}),(1,line.id, {'debit': 0})]}
                                self.move_id.write(vals)
                                line.unlink()
                                break
                        
        elif self.payment_type == 'outbound':
            lst = []
            for tax in self.wht_line_ids:
                for line in self.move_id.line_ids:
                    if 'tax'in line.account_id.name.lower():
                        lst.append(line.account_id.name.lower())
                    if line.debit == 0:
                        if not line.account_id.is_tax:
                            credit_line = line
                            # line['debit'] = rec.amount
                        else:
                            if tax.name == line.name:
                                # raise UserError(line.account_id.name.lower())
                                # raise UserError('here')
                                tax_amount = line['credit']
                                # new_amnt = credit_line.credit
                                vals = {'line_ids': [(1,credit_line.id, {'credit': credit_line.credit + tax_amount}),(1,line.id, {'credit': 0})]}
                                self.move_id.write(vals)
                                line.unlink()
                                break
            # raise UserError(lst)