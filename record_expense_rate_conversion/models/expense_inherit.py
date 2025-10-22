from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

class  RecordExpenseInherit(models.Model):
    _inherit = "expense.module"

    currency__convert_id = fields.Many2one('res.currency' , 'Currency' , default=lambda self: self.env.ref('base.PKR').id)
    conversion_rate = fields.Float('Conversion Rate')

    

    def action_prepared_expense(self):
        if self.currency__convert_id.name != "PKR" and not self.conversion_rate:
            raise ValidationError('Enter Conversion Rate For the chosen currency')
        if self.total_debit != self.total_credit:
            raise UserError("Debit and Credit are not equal")
        if self.currency__convert_id and self.conversion_rate and self.currency__convert_id.name != 'PKR' and self.date:
            rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency__convert_id.id),
                ('name', '=', self.date)
            ], limit=1)
            
            if rate:
                # Update the existing rate
                rate.write({
                    'company_rate' : 1/self.conversion_rate,
                    'inverse_company_rate': self.conversion_rate})
            else:
                # Create a new rate
                self.env['res.currency.rate'].create({
                    'currency_id': self.currency__convert_id.id,
                    'name': self.date,
                    'company_rate' : 1/self.conversion_rate,
                    'inverse_company_rate': self.conversion_rate,
                })
                
            return super(RecordExpenseInherit, self).action_prepared_expense()

        else:
            return super(RecordExpenseInherit, self).action_prepared_expense()


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
                    })

from odoo import models, fields, api

class RecordExpenseLineInherit(models.Model):
    _inherit = 'expense.line'

    convert_currency_id = fields.Many2one('res.currency', related="expense_module_id.currency__convert_id")
    
    # def _onchange_account(self):
    #     if self.account and self.account.is_analytic_required:
    #         if not self.partner or not self.analytic_field:
    #             return {
    #                 'warning': {
    #                     'title': "Missing Required Fields",
    #                     'message': "Partner and Analytic Account are required when the selected account requires analytics."
    #                 }
    #             }

    # @api.constrains('account', 'partner', 'analytic_field')
    # def _check_required_fields(self):
    #     for record in self:
    #         if record.account and record.account.is_analytic_required:
    #             if not record.partner or not record.analytic_field:
    #                 raise ValidationError("Partner and Analytic Account must be set when the selected account requires analytics.")



    @api.model
    def create(self, vals):
        account = self.env['account.account'].browse(vals.get('account'))
        if account and account.is_analytic_required:
            if not vals.get('analytical_field'):
                raise ValidationError("Cannot create record: Analytic Account is required when the selected account requires analytics.")
        if account and account.name == "Creditors - Import, Local, Services":
            if not vals.get('partner'):
                raise ValidationError("Cannot create record: Partner is required.")
        return super(RecordExpenseLineInherit, self).create(vals)

