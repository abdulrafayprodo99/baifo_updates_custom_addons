from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RecordExpense(models.Model):
    _inherit = 'expense.module'

    def create_expense_journal_entry(self):
        if (self.is_bank_payment == 'yes' and self.approval_state_expense == "prepared") or (self.is_bank_payment == 'no' and self.approval_state_expense == "prepared"):
            lines = []
            for rec1 in self:
                if rec1.state == 'posted':
                    raise UserError('This Document is already posted')
                else:
                    credit = 0
                    for rec in rec1.expense_line:
                        if rec.general_item_type == 'debit':
                            line = (0, 0, {
                                'account_id': rec.account.id,
                                'debit': rec.value*self.conversion_rate if self.conversion_rate else rec.value,
                                'name':rec.description,
                                'partner_id': rec.partner.id,
                                'analytic_distribution': rec.analytical_field,
                                'currency_rate':rec1.conversion_rate,
                                # 'analytic_tag_ids': rec.tags,
                            })
                            lines.append(line)
                        if rec.general_item_type == 'credit':     
                            credit = rec.value
                            line_ = (0, 0, {
                                # 'account_id': rec1.journal.default_account_id.id if rec1.journal.is_miscellaneous_journal else rec1.account_id.id ,
                                'account_id': rec.account.id,
                                'credit': credit*self.conversion_rate if self.conversion_rate else rec.value,
                                'name':rec.description,
                                'partner_id': rec.partner.id,
                                'analytic_distribution': rec.analytical_field,
                                'currency_rate':rec1.conversion_rate,
                                })
                            lines.append(line_)
                    self.env['account.move'].with_context(check_move_validity=False).create({
                        'name':rec1.name,
                        'journal_id': rec1.journal.id,
                        'date': rec1.date,
                        'invoice_date': rec1.date,
                        'line_ids': lines,
                        'expense_id': rec1.id, 
                        'currency_rate':rec1.conversion_rate,
                    })


    def action_update_journal_entry(self):
        if self.state != 'posted':
            for rec in self:
                journal_entry = self.env['account.move'].search([('expense_id', '=', rec.id)])
                if journal_entry:
                    journal_entry.unlink()
                    lines = []
                    for rec1 in self:
                        credit = 0
                        for rec in rec1.expense_line:
                            if rec.general_item_type == 'debit':
                                line = (0, 0, {
                                    'account_id': rec.account.id,
                                    'debit': rec.value*self.conversion_rate if self.conversion_rate else rec.value,
                                    'name':rec.description,
                                    'partner_id': rec.partner.id,
                                    'analytic_distribution': rec.analytical_field,
                                    # 'analytic_tag_ids': rec.tags,
                                })
                                lines.append(line)
                            if rec.general_item_type == 'credit':     
                                credit = rec.value
                                line_ = (0, 0, {
                                    'account_id': rec.account.id,
                                    'credit': credit*self.conversion_rate if self.conversion_rate else rec.value,
                                    'name':rec.description,
                                    'partner_id': rec.partner.id,
                                    'analytic_distribution': rec.analytical_field
                                    })
                                lines.append(line_)
                        self.env['account.move'].with_context(check_move_validity=False).create({
                            'name':rec1.name,
                            'journal_id': rec1.journal.id,
                            'date': rec1.date,
                            'invoice_date': rec1.date,
                            'line_ids': lines,
                            'expense_id': rec1.id, 
                            'currency_rate':rec1.conversion_rate,
                        })
                    # Reset the flag after updating the journal entry
                    self.lines_modified = False
        else:
            raise UserError('This Document is already posted')

