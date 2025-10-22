from odoo import fields, models, api
import re

class Accounting_inherit(models.Model):
    _name = 'bank.position'
    _description = 'Bank Position'

    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    bank_id = fields.Many2one('account.account', string="Bank" , domain=[('account_type','=','asset_cash')])
    bank_name = fields.Char(string="Bank Name", compute='compute_bank_name_account', stored=True)
    account_no = fields.Char(string="Account Number" , compute='compute_bank_name_account', stored=True)
    available_balance = fields.Float(string="Sum of Available Balance")

    @api.depends('bank_id')
    def compute_bank_name_account(self):
        for rec in self:
            if rec.bank_id and"A/C" in rec.bank_id.name:

                bank_match = re.match(r'^(.*?)-\s*A/C', rec.bank_id.name)
                rec.bank_name = bank_match.group(1).strip() if bank_match else ''

                account_match = re.search(r'A/C\s+No\.\s?(\d+)', rec.bank_id.name)
                rec.account_no = account_match.group(1) if account_match else ''
            else:
                rec.account_no = ''
                rec.bank_name = ''    