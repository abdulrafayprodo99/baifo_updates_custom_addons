from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

class  RecordExpense(models.Model):
    _inherit = "expense.module"
    
    readonly_check = fields.Boolean('Readonly Check',copy = False)
    
    # def create_journal_entries(self):
    #      lines = []
    #         for rec1 in self:
                
    #             if rec1.state == 'posted':
    #                 raise UserError('This Document is already posted')
    #             else:
    #                 credit = 0
    #                 for rec in rec1.expense_line:
    #                     if rec.general_item_type == 'debit':
    #                         line = (0, 0, {
    #                             'account_id': rec.account.id,
    #                             'debit': rec.value,
    #                             'name':rec.description,
    #                             'partner_id': rec.partner.id,
    #                             'analytic_distribution': rec.analytical_field,
    #                             # 'analytic_tag_ids': rec.tags,
    #                         })
    #                         lines.append(line)
    #                     if rec.general_item_type == 'credit':     
    #                         credit = rec.value
    #                         line_ = (0, 0, {
    #                             # 'account_id': rec1.journal.default_account_id.id if rec1.journal.is_miscellaneous_journal else rec1.account_id.id ,
    #                             'account_id': rec.account.id,
    #                             'credit': credit,
    #                             'name':rec.description,
    #                             'partner_id': rec.partner.id,
    #                             'analytic_distribution': rec.analytical_field
    #                             })
    #                         lines.append(line_)
                    
    #                 self.env['account.move'].with_context(check_move_validity=False).create({
    #                     'name':rec1.name,
    #                     'journal_id': rec1.journal.id,
    #                     'date': rec1.date,
    #                     'invoice_date': rec1.date,
    #                     'line_ids': lines,
    #                     'expense_id': rec1.id, 
    #                 })
            
    def server_post_expense_action(self):
        # super
        if self.state != 'posted':
            for rec in self:
                # rec.create_journal_entries()
                    # super(RecordExpense, self).action_prepared_expense()
            # if rec.payment_type == 'Bank Payment':
                rec.readonly_check = True
        super(RecordExpense, self).server_post_expense_action()
        
    
    def action_reset_to_draft(self):
        """Reset the state to draft."""
        for record in self:
            record.state = 'draft'
            record.approval_state_expense = False
            # record.approval_state_expense = False
            record.readonly_check = False
            journal_entry = record.env['account.move'].search([('expense_id', '=', record.id)])
            journal_entry.button_draft()
            journal_entry.unlink()
            
