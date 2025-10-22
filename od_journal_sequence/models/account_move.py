# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re

class AccountMove(models.Model):
    _inherit = "account.move"

    name = fields.Char(compute="_compute_name")
    
    name_once_posted = fields.Char()


    def restrictName(self):
        for rec in self:
            if rec.approval_state == 'prepared' and rec.name not in ['/','Draft'] and not rec.name_once_posted:
                rec.name_once_posted = rec.name
            else:
                continue    
    @api.onchange('name')
    def populate_name_once_posted(self):
        for rec in self:
            if rec.posted_before and rec.name_once_posted and rec.name != rec.name_once_posted :
                rec.name = rec.name_once_posted

    def action_prepared(self):
        res =  super(AccountMove,self).action_prepared()
        self.restrictName()

    # sher ahmed
    @api.depends('posted_before', 'state', 'journal_id', 'date','approval_state')
    def _compute_name(self):
        for move in self:
            name = "" #move.name or "/"
            # if not move.name:
            if not move.name or move.name in ["Draft", "/"]:
                
                # and (not move.name or move.name == "/") 
                # move.state == "posted" and 
                if (move.journal_id and move.journal_id.sequence_id):
                    if ( move.move_type in ("out_refund", "in_refund") and move.journal_id.type in ("sale", "purchase") and move.journal_id.refund_sequence and move.journal_id.refund_sequence_id):
                        # raise UserError('a')
                        seq = move.journal_id.refund_sequence_id
                    else:
                        # raise UserError('b')
                        seq = move.journal_id.sequence_id
                
                
                    move.journal_id.update_number_next()
                    # sher ahmed
                    # if move.state == "posted": 
                    if move.approval_state == "prepared" or (move.move_type=='entry' and move.state=="posted"):
                        if (move.invoice_date or move.date) and not move.payment_id:
                            if move.move_type == "out_invoice":
                                
                                name = str(move.journal_id.sequence_code_short)+ '-' + str(move.invoice_date.year) + '-' + str(move.invoice_date.month) + '-' + str(seq.next_by_id(sequence_date=move.invoice_date))
                                move['name'] = name
                            elif move.move_type in ["entry","in_invoice"]:
                                name = str(move.journal_id.sequence_code_short)+ '-' + str(move.date.year) + '-' + str(move.date.month) + '-' + str(seq.next_by_id(sequence_date=move.date))
                                move['name'] = name
                            else:
                                date_ = move.invoice_date if move.invoice_date else move.date 
                                name = str(move.journal_id.sequence_code_short)+ '-' + str(date_.year) + '-' + str(date_.month) + '-' + str(seq.next_by_id(sequence_date=date_))
                                move['name'] = name
                        elif move.date and move.payment_id:
                            if move.payment_id.payment_type == "outbound":

                                name = str(move.journal_id.sequence_code_short)+ '-' + str(move.date.year) + '-' + str(move.date.month) + '-' + str(seq.next_by_id(sequence_date=move.date))
                                move.name = name
                            elif move.payment_id.payment_type == "inbound":

                                name = str(move.journal_id.customer_payment_code)+ '-' + str(move.date.year) + '-' + str(move.date.month) + '-' + str(move.journal_id.sequence_id_2.next_by_id(sequence_date=move.date))
                                move.name = name

                    if move.state != "posted" and move.expense_id:
                        name = str(move.journal_id.sequence_code_short)+ '-' + str(move.date.year) + '-' + str(move.date.month) + '-' + str(seq.next_by_id(sequence_date=move.date))
                        move['name'] = name
                        raise UserError(str(move.name))

    def _constrains_date_sequence(self):
        return True

