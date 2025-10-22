# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Merging(models.Model):
    _name = "merging"
    _description = "Merging"

    name = fields.Char(string="Name",copy=False)
    journal_id = fields.Many2one('account.journal',string="Journal")
    date = fields.Date(string="Document Date")
    amount = fields.Float(string="Amount")
    type = fields.Selection([('expense','Record Expense'),('payment', 'Payment')], string = 'Type' )
    payment_id = fields.Many2one('account.payment',string="Payment")
    expense_id = fields.Many2one('expense.module',string="Record Expense")
    journal_entry = fields.Many2one('account.move',string="Journal Entry",  domain=[('move_type', '=', 'entry')])
    
    
    
    
    