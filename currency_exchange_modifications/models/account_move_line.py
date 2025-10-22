from odoo import models, fields, api, _,Command
from odoo.exceptions import UserError,ValidationError
from functools import lru_cache
from contextlib import contextmanager
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
from datetime import datetime


class AccountMoveLine(models.Model):
    _inherit="account.move.line"

    @api.depends('currency_id', 'company_id', 'move_id.date')
    def _compute_currency_rate(self):
        @lru_cache()
        def get_rate(from_currency, to_currency, company, date):
            return self.env['res.currency']._get_conversion_rate(
                from_currency=from_currency,
                to_currency=to_currency,
                company=company,
                date=date,
            )
        for line in self:
            if line.currency_id and not line.move_id.currency_rate:
                currency_rate = get_rate(
                    from_currency=line.company_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=line.move_id.invoice_date or line.move_id.date or fields.Date.context_today(line),
                )
                line.currency_rate = currency_rate
            else:
                line.currency_rate = line.move_id.currency_rate
                

    @contextmanager
    def _sync_invoice(self, container):
        if container['records'].env.context.get('skip_invoice_line_sync'):
            yield
            return  # avoid infinite recursion
        
        def existing():
            return {
                line: {
                    'amount_currency': line.currency_id.round(line.amount_currency),
                    'balance': line.company_id.currency_id.round(line.balance),
                    'currency_rate': line.currency_rate,
                    'price_subtotal': line.currency_id.round(line.price_subtotal),
                    'move_type': line.move_id.move_type,
                } for line in container['records'].with_context(
                    skip_invoice_line_sync=True,
                ).filtered(lambda l: l.move_id.is_invoice(True))
            }

        def changed(fname):
            return line not in before or before[line][fname] != after[line][fname]

        before = existing()
        yield
        after = existing()
        
        for line in after:
            if (
                line.display_type == 'product'
                and (not changed('amount_currency') or line not in before)
            ):
                amount_currency = line.move_id.direction_sign * line.currency_id.round(line.price_subtotal)
                if line.amount_currency != amount_currency or line not in before:
                    line.amount_currency = amount_currency
                if line.currency_id == line.company_id.currency_id:
                    line.balance = amount_currency
        after = existing()
        for line in after:
            if (
                (changed('amount_currency') or changed('currency_rate') or changed('move_type'))
                and (not changed('balance') or (line not in before and not line.balance))
            ):
                balance = line.company_id.currency_id.round(line.amount_currency * line.currency_rate)
                line.balance = balance
        # Since this method is called during the sync, inside of `create`/`write`, these fields
        # already have been computed and marked as so. But this method should re-trigger it since
        # it changes the dependencies.
        self.env.add_to_compute(self._fields['debit'], container['records'])
        self.env.add_to_compute(self._fields['credit'], container['records'])