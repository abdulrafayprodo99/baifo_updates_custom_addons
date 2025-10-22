# # from odoo import models, fields, api
# # from odoo.exceptions import UserError

# # # -*- coding: utf-8 -*-

# # from collections import defaultdict
# # from contextlib import ExitStack, contextmanager
# # from datetime import date, timedelta
# # from dateutil.relativedelta import relativedelta
# # from hashlib import sha256
# # from json import dumps
# # import re
# # from textwrap import shorten
# # from unittest.mock import patch

# # from odoo import api, fields, models, _, Command
# # from odoo.addons.base.models.decimal_precision import DecimalPrecision
# # from odoo.addons.account.tools import format_rf_reference
# # from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
# # from odoo.tools import (
# #     date_utils,
# #     email_re,
# #     email_split,
# #     float_compare,
# #     float_is_zero,
# #     float_repr,
# #     format_amount,
# #     format_date,
# #     formatLang,
# #     frozendict,
# #     get_lang,
# #     is_html_empty,
# #     sql
# # )

# # class AccountMove(models.Model):
# #     _inherit = 'account.move'

# #     origin_name = fields.Char(string='Origin', compute='_compute_origin_name')
# #     invoice_payments_widget = fields.Binary(
# #         groups="account.group_account_invoice,account.group_account_readonly",
# #         compute='_compute_payments_widget_reconciled_info',
# #         exportable=False,
# #     )


# #     journal_entry_name = fields.Char(string='JEname')#, compute='_compute_journal_name')
# #     payement_entry_name = fields.Char(string='Pname')
# #     def get_payment_ref(self, data):
# #         # Check if data is not a bool and contains 'content'
# #         if isinstance(data, dict) and 'content' in data:
# #             # Extract the payment ref where account_payment_id is present
# #             return next((entry['ref'] for entry in data['content'] if entry['account_payment_id']), None)
# #         return None  # Return None if data is not valid

# #     def get_journal_entry_ref(self, data):
# #         # Extract the journal entry ref where account_payment_id is absent (False)
# #         return next((entry['ref'] for entry in data['content'] if not entry['account_payment_id']), None)



# #     def get_invoice_name(self, data):
# #         # Check if data is not a bool and contains 'content'
# #         if isinstance(data, dict) and 'content' in data:
# #             # Extract the invoice_name from the content
# #             return next((entry['invoice_name'] for entry in data['content'] if 'invoice_name' in entry), None)
# #         return None  # Return None if data is not valid



# #     # @api.depends('payment_id')
# #     # def _compute_journal_name(self):
# #     #     for move in self:
            

# #     #         move.journal_entry_name =  move.invoice_payments_widget#["content"][0]["ref"]
# #     #         raise UserError(str(move.journal_entry_name)) #self.get_payment_ref(move.invoice_payments_widget)
        

# #     @api.depends('payment_id')
# #     def _compute_origin_name(self):
# #         for move in self:
# #             journal_entry_name  = self.get_invoice_name(move.invoice_payments_widget)
# #             # raise UserError(str(journal_entry_name))

# #             # journal_entry_name = move['journal_entry_name']
# #             # raise UserError(str(journal_entry_name))

# #             # if journal_entry_name == move.name:
# #             #     raise UserError(f"{journal_entry_name} same as {move.name}")
# #             # else:
# #             #     raise UserError(f"{journal_entry_name} not same as {move.name}")

# #             # raise UserError(type(move.name))

# #             # journal_entry_name = move.name

# #             # Load all journal entries into a recordset
# #             journal_entries = self.env['account.move'].search([])  # Adjust the search domain as needed
# #             # entries_name=journal_entries.mapped(lambda je: [je.name,je.journal_entry_name])
# #             # raise UserError(str(entries_name))
# #             # Use filter to get the specific journal entry by name
# #             journal_entry = journal_entries.filtered(lambda entry: entry.journal_entry_name == journal_entry_name )

# #             # raise UserError(str(journal_entry_name == 'EXCH-2024-10-0019') + " " + str(journal_entry_name))
# #             # journal_entry = self.env['account.move'].search([('journal_entry_name', '=', journal_entry_name)])

# #             # raise UserError(str(journal_entry.read()))
# #             # raise UserError(str(journal_entry.name))
            
# #             # journal_entry = move.env['account.move.line'].search([])
# #             # raise UserError(str(journal_entry.read()))

# #             # raise UserError(str(move.read()))

# #             # raise UserError(str(move.invoice_line_ids.read()))

# #             payment_ref = self.get_payment_ref(move.invoice_payments_widget)

# #             invoice_name = journal_entry.name if journal_entry else ''
# #             # payment_name = move.payment_id.name if move.payment_id else ''
            
# #             if invoice_name and payment_ref:
# #                 move.origin_name = f"{invoice_name} / {payment_ref}"
# #             elif invoice_name:
# #                 move.origin_name = invoice_name
# #             elif payment_ref:
# #                 move.origin_name = payment_ref
# #             else:
# #                 move.origin_name = ''

# #     @api.depends('move_type', 'line_ids.amount_residual')
# #     def _compute_payments_widget_reconciled_info(self):
# #         for move in self:
# #             payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}


# #             if move.state == 'posted':# and move.is_invoice(include_receipts=True):
# #                 reconciled_vals = []
# #                 reconciled_partials = move._get_all_reconciled_invoice_partials()
# #                 # raise UserError(str(reconciled_partials))
# #                 for reconciled_partial in reconciled_partials:
# #                     counterpart_line = reconciled_partial['aml']
# #                     # raise UserError(str(counterpart_line.read()))
# #                     if counterpart_line.move_id.ref:
# #                         reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
# #                         move.payement_entry_name = reconciliation_ref
# #                     else:
# #                         reconciliation_ref = counterpart_line.move_id.name
# #                         move.journal_entry_name = reconciliation_ref
# #                     if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
# #                         foreign_currency = counterpart_line.currency_id
# #                     else:
# #                         foreign_currency = False

# #                     reconciled_vals.append({
# #                         'invoice_name': move.name,
# #                         'name': counterpart_line.name,
# #                         'journal_name': counterpart_line.journal_id.name,
# #                         'amount': reconciled_partial['amount'],
# #                         'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else reconciled_partial['currency'].id,
# #                         'date': counterpart_line.date,
# #                         'partial_id': reconciled_partial['partial_id'],
# #                         'account_payment_id': counterpart_line.payment_id.id,
# #                         'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
# #                         'move_id': counterpart_line.move_id.id,
# #                         'ref': reconciliation_ref,
# #                         # these are necessary for the views to change depending on the values
# #                         'is_exchange': reconciled_partial['is_exchange'],
# #                         'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance), currency_obj=counterpart_line.company_id.currency_id),
# #                         'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(counterpart_line.amount_currency), currency_obj=foreign_currency)
# #                     })
# #                 payments_widget_vals['content'] = reconciled_vals

# #             if payments_widget_vals['content']:
# #                 move.invoice_payments_widget = payments_widget_vals
# #             else:
# #                 move.invoice_payments_widget = False







# from odoo import models, fields, api
# from odoo.exceptions import UserError

# # -*- coding: utf-8 -*-

# from collections import defaultdict
# from contextlib import ExitStack, contextmanager
# from datetime import date, timedelta
# from dateutil.relativedelta import relativedelta
# from hashlib import sha256
# from json import dumps
# import re
# from textwrap import shorten
# from unittest.mock import patch

# from odoo import api, fields, models, _, Command
# from odoo.addons.base.models.decimal_precision import DecimalPrecision
# from odoo.addons.account.tools import format_rf_reference
# from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
# from odoo.tools import (
#     date_utils,
#     email_re,
#     email_split,
#     float_compare,
#     float_is_zero,
#     float_repr,
#     format_amount,
#     format_date,
#     formatLang,
#     frozendict,
#     get_lang,
#     is_html_empty,
#     sql
# )

# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     origin_name = fields.Char(string='Origin', compute='_compute_origin_name')
#     invoice_payments_widget = fields.Binary(
#         groups="account.group_account_invoice,account.group_account_readonly",
#         compute='_compute_payments_widget_reconciled_info',
#         exportable=False,
#     )


#     journal_entry_name = fields.Char(string='JEname')#, compute='_compute_journal_name')
#     payement_entry_name = fields.Char(string='Pname')
#     def get_payment_ref(self, data):
#         # Check if data is not a bool and contains 'content'
#         if isinstance(data, dict) and 'content' in data:
#             # Extract the payment ref where account_payment_id is present
#             return next((entry['ref'] for entry in data['content'] if entry['account_payment_id']), None)
#         return None  # Return None if data is not valid

#     def get_journal_entry_ref(self, data):
#         # Extract the journal entry ref where account_payment_id is absent (False)
#         return next((entry['ref'] for entry in data['content'] if not entry['account_payment_id']), None)



#     def get_invoice_name(self, data):
#         # Check if data is not a bool and contains 'content'
#         if isinstance(data, dict) and 'content' in data:
#             # Extract the invoice_name from the content
#             return next((entry['invoice_name'] for entry in data['content'] if 'invoice_name' in entry), None)
#         return None  # Return None if data is not valid



#     # @api.depends('payment_id')
#     # def _compute_journal_name(self):
#     #     for move in self:
            

#     #         move.journal_entry_name =  move.invoice_payments_widget#["content"][0]["ref"]
#     #         raise UserError(str(move.journal_entry_name)) #self.get_payment_ref(move.invoice_payments_widget)
        
#     def extract_foreign_currency(self, data):
#         # Extract the foreign currency amount string
#         if  data['content']:
#             amount_str = data['content'][0]['amount_foreign_currency']
#             if amount_str:
#                 # Remove any non-numeric characters (such as the dollar sign or spaces)
#                 cleaned_amount = ''.join(char for char in amount_str if char.isdigit() or char == '.')

#                 # Convert the cleaned string to float
#                 return float(cleaned_amount)
#             else:
#                 return None


#     def calculate_exchange_rate(self, data):
#         # Extract the foreign currency amount string
#         if  data['content']:
#             foreign_amount_str = data['content'][0]['amount_foreign_currency']
#             company_amount_str = data['content'][0]['amount_company_currency']

#             if foreign_amount_str and company_amount_str:
                    
#                 # Clean the strings to remove non-numeric characters except for the decimal point
#                 cleaned_foreign_amount = ''.join(char for char in foreign_amount_str if char.isdigit() or char == '.')
#                 cleaned_company_amount = ''.join(char for char in company_amount_str if char.isdigit() or char == '.')
                
#                 # Remove any trailing periods
#                 if cleaned_foreign_amount.endswith('.'):
#                     cleaned_foreign_amount = cleaned_foreign_amount[:-1]
#                 if cleaned_company_amount.endswith('.'):
#                     cleaned_company_amount = cleaned_company_amount[:-1]
                
#                 # Convert the cleaned strings to float
#                 foreign_amount = float(cleaned_foreign_amount)
#                 company_amount = float(cleaned_company_amount)

#                 # Calculate and return the exchange rate
#                 return company_amount / foreign_amount if foreign_amount != 0 else None
#             else:
#                 return None



#     @api.depends('payment_id')
#     def _compute_origin_name(self):
#         for move in self:
            
#             if move.invoice_payments_widget:

#                 usd_amount = self.extract_foreign_currency(move.invoice_payments_widget)
#                 # raise UserError(str(usd_amount))
#                 rate = self.calculate_exchange_rate(move.invoice_payments_widget)
#             journal_entry_name  = self.get_invoice_name(move.invoice_payments_widget)


#             # journal_entry_name = move['journal_entry_name']
#             # raise UserError(str(journal_entry_name))

#             # if journal_entry_name == move.name:
#             #     raise UserError(f"{journal_entry_name} same as {move.name}")
#             # else:
#             #     raise UserError(f"{journal_entry_name} not same as {move.name}")

#             # raise UserError(type(move.name))

#             # journal_entry_name = move.name

#             # Load all journal entries into a recordset
#             journal_entries = self.env['account.move'].search([])  # Adjust the search domain as needed
#             # entries_name=journal_entries.mapped(lambda je: [je.name,je.journal_entry_name])
#             # raise UserError(str(entries_name))
#             # Use filter to get the specific journal entry by name
#             journal_entry = journal_entries.filtered(lambda entry: entry.journal_entry_name == journal_entry_name )

#             # raise UserError(str(journal_entry_name == 'EXCH-2024-10-0019') + " " + str(journal_entry_name))
#             # journal_entry = self.env['account.move'].search([('journal_entry_name', '=', journal_entry_name)])

#             # raise UserError(str(journal_entry.read()))
#             # raise UserError(str(journal_entry.name))
            
#             # journal_entry = move.env['account.move.line'].search([])
#             # raise UserError(str(journal_entry.read()))

#             # raise UserError(str(move.read()))

#             # raise UserError(str(move.invoice_line_ids.read()))

#             payment_ref = self.get_payment_ref(move.invoice_payments_widget)

#             invoice_name = journal_entry.name if journal_entry else ''
#             # payment_name = move.payment_id.name if move.payment_id else ''
            
#             if invoice_name and payment_ref:
#                 move.origin_name = f"{invoice_name} USD {usd_amount} @ {rate} pkr / {payment_ref} USD {usd_amount} @ {rate} pkr"
#             elif invoice_name:
#                 move.origin_name = invoice_name
#             elif payment_ref:
#                 move.origin_name = payment_ref
#             else:
#                 move.origin_name = ''

#     @api.depends('move_type', 'line_ids.amount_residual')
#     def _compute_payments_widget_reconciled_info(self):
#         for move in self:
#             payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}


#             if move.state == 'posted':# and move.is_invoice(include_receipts=True):
#                 reconciled_vals = []
#                 reconciled_partials = move._get_all_reconciled_invoice_partials()
#                 # raise UserError(str(reconciled_partials))
#                 for reconciled_partial in reconciled_partials:
#                     counterpart_line = reconciled_partial['aml']
#                     # raise UserError(str(counterpart_line.read()))
#                     if counterpart_line.move_id.ref:
#                         reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
#                         move.payement_entry_name = reconciliation_ref
#                     else:
#                         reconciliation_ref = counterpart_line.move_id.name
#                         move.journal_entry_name = reconciliation_ref
#                     if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
#                         foreign_currency = counterpart_line.currency_id
#                     else:
#                         foreign_currency = False

#                     reconciled_vals.append({
#                         'invoice_name': move.name,
#                         'name': counterpart_line.name,
#                         'journal_name': counterpart_line.journal_id.name,
#                         'amount': reconciled_partial['amount'],
#                         'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else reconciled_partial['currency'].id,
#                         'date': counterpart_line.date,
#                         'partial_id': reconciled_partial['partial_id'],
#                         'account_payment_id': counterpart_line.payment_id.id,
#                         'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
#                         'move_id': counterpart_line.move_id.id,
#                         'ref': reconciliation_ref,
#                         # these are necessary for the views to change depending on the values
#                         'is_exchange': reconciled_partial['is_exchange'],
#                         'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance), currency_obj=counterpart_line.company_id.currency_id),
#                         'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(counterpart_line.amount_currency), currency_obj=foreign_currency)
#                     })
#                 payments_widget_vals['content'] = reconciled_vals

#             if payments_widget_vals['content']:
#                 move.invoice_payments_widget = payments_widget_vals
#             else:
#                 move.invoice_payments_widget = False


from odoo import models, fields, api
from odoo.exceptions import UserError

# -*- coding: utf-8 -*-

from collections import defaultdict
from contextlib import ExitStack, contextmanager
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from hashlib import sha256
from json import dumps
import re
from textwrap import shorten
from unittest.mock import patch

from odoo import api, fields, models, _, Command
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.addons.account.tools import format_rf_reference
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    is_html_empty,
    sql
)

class AccountMove(models.Model):
    _inherit = 'account.move'

    origin_name = fields.Char(string='Origin', compute='_compute_origin_name')
    invoice_payments_widget = fields.Binary(
        groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_reconciled_info',
        exportable=False,
    )


    journal_entry_name = fields.Char(string='JEname')#, compute='_compute_journal_name')
    payement_entry_name = fields.Char(string='Pname')
    def get_payment_ref(self, data):
        # Check if data is not a bool and contains 'content'
        if isinstance(data, dict) and 'content' in data:
            # Extract the payment ref where account_payment_id is present
            return next((entry['ref'] for entry in data['content'] if entry['account_payment_id']), None)
        return None  # Return None if data is not valid

    def get_journal_entry_ref(self, data):
        # Extract the journal entry ref where account_payment_id is absent (False)
        return next((entry['ref'] for entry in data['content'] if not entry['account_payment_id']), None)



    def get_invoice_name(self, data):
        # Check if data is not a bool and contains 'content'
        if isinstance(data, dict) and 'content' in data:
            # Extract the invoice_name from the content
            return next((entry['invoice_name'] for entry in data['content'] if 'invoice_name' in entry), None)
        return None  # Return None if data is not valid



    def extract_payment_details(self, data):
        # Helper function to format amount_foreign_currency as a numeric value
        def format_currency(amount_str):
            if isinstance(amount_str, str):  # Ensure it's a string
                # Remove currency symbols, commas, and non-breaking spaces
                amount_str = amount_str.replace('$', '').replace('\xa0', '').replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    return None
            return None  # Return None if the input is not a string

        # Ensure that the data is a dictionary and has content
        if isinstance(data, dict) and 'content' in data and data['content']:
            # Extract the relevant fields from the first item in the 'content' list
            content_item = data['content'][0]
            invoice_exchange_rate = content_item.get('invoice_exchange_rate')
            payment_exchange_rate = content_item.get('payment_exchange_rate')
            amount_foreign_currency = format_currency(content_item.get('amount_foreign_currency', ''))

            return {
                'invoice_exchange_rate': invoice_exchange_rate,
                'payment_exchange_rate': payment_exchange_rate,
                'amount_foreign_currency': amount_foreign_currency
            }
        else:
            # Return an appropriate default or None if the data is not valid
            return None


    @api.depends('payment_id')
    def _compute_origin_name(self):
        for move in self:
            payment_details = self.extract_payment_details(move.invoice_payments_widget)
            journal_entry_name  = self.get_invoice_name(move.invoice_payments_widget)
            journal_entries = move.env['account.move'].search([])  # Adjust the search domain as needed
            journal_entry = journal_entries.filtered(lambda entry: entry.journal_entry_name == move.name )


            if len(journal_entry) > 1:
                invoice_name = journal_entry[0].name if journal_entry else ''
            else:
                invoice_name = journal_entry.name if journal_entry else ''
            payment_ref = move.get_payment_ref(move.invoice_payments_widget)

            
            if invoice_name and payment_ref:
                move.origin_name = f"{invoice_name} USD {payment_details['amount_foreign_currency']} @ {payment_details['invoice_exchange_rate']} PKR / {payment_ref} USD {payment_details['amount_foreign_currency']} @ {payment_details['payment_exchange_rate']} PKR"
            elif invoice_name:
                move.origin_name = invoice_name
            elif payment_ref:
                move.origin_name = payment_ref
            else:
                move.origin_name = ''




    # @api.depends('move_type', 'line_ids.amount_residual')
    # def _compute_payments_widget_reconciled_info(self):
    #     for move in self:
    #         payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}


    #         if move.state == 'posted':# and move.is_invoice(include_receipts=True):
    #             reconciled_vals = []
    #             reconciled_partials = move._get_all_reconciled_invoice_partials()
    #             # raise UserError(str(reconciled_partials))
    #             for reconciled_partial in reconciled_partials:
    #                 counterpart_line = reconciled_partial['aml']
    #                 invoice_exchange_rate = counterpart_line.move_id.currency_rate
    #                 payment_exchange_rate = counterpart_line.move_id.manual_currency_rate

                    
    #                 if counterpart_line.move_id.ref:
    #                     reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
    #                     move.payement_entry_name = reconciliation_ref

    #                 else:
    #                     reconciliation_ref = counterpart_line.move_id.name
    #                     move.journal_entry_name = reconciliation_ref
    #                 if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
    #                     foreign_currency = counterpart_line.currency_id 

    #                 else:
    #                     foreign_currency = False

    #                 reconciled_vals.append({
    #                     'invoice_name': move.name,
    #                     'name': counterpart_line.name,
    #                     'journal_name': counterpart_line.journal_id.name,
    #                     'amount': reconciled_partial['amount'],
    #                     'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else reconciled_partial['currency'].id,
    #                     'date': counterpart_line.date,
    #                     'partial_id': reconciled_partial['partial_id'],
    #                     'account_payment_id': counterpart_line.payment_id.id,
    #                     'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
    #                     'move_id': counterpart_line.move_id.id,
    #                     'ref': reconciliation_ref,
    #                     # these are necessary for the views to change depending on the values
    #                     'is_exchange': reconciled_partial['is_exchange'],
    #                     'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance), currency_obj=counterpart_line.company_id.currency_id),
    #                     'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(counterpart_line.amount_currency), currency_obj=foreign_currency),
    #                     'invoice_exchange_rate': invoice_exchange_rate,
    #                     'payment_exchange_rate': payment_exchange_rate,
    #                 })
    #             payments_widget_vals['content'] = reconciled_vals

    #         if payments_widget_vals['content']:
    #             move.invoice_payments_widget = payments_widget_vals
    #         else:
    #             move.invoice_payments_widget = False






