from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from itertools import chain
from dateutil.relativedelta import relativedelta
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import logging
import ast
import datetime
import io
import json
import logging
import math
import re
import base64
from ast import literal_eval
from collections import defaultdict
from functools import cmp_to_key

import markupsafe
from babel.dates import get_quarter_names
from dateutil.relativedelta import relativedelta

from odoo.addons.web.controllers.utils import clean_action
from odoo import models, fields, api, _, osv, _lt
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero
from odoo.tools.float_utils import float_round
from odoo.tools.misc import formatLang, format_date, xlsxwriter
from odoo.tools.safe_eval import expr_eval, safe_eval
from odoo.models import check_method_name
_logger = logging.getLogger(__name__)

class Inherit_aged_receviable(models.AbstractModel):
    _inherit = 'account.aged.partner.balance.report.handler'
    # _inherit = 'account.report.custom.handler'
    _description = 'Aged Partner Balance Custom Handler'

    def _report_custom_engine_aged_receivable(self, expressions, options, date_scope, current_groupby, next_groupby, offset=0, limit=None):
        super(Inherit_aged_receviable,self)._report_custom_engine_aged_receivable( expressions, options, date_scope, current_groupby, next_groupby, offset, limit)
        res=self._aged_partner_report_custom_engine_common(options, 'asset_receivable', current_groupby, next_groupby, offset=offset, limit=limit)
        # raise UserError(str(res))      
        _logger.warning("from _report_custom_engine_aged_receivable"+str(res))      
        return res
    
    def _aged_partner_report_custom_engine_common(self, options, internal_type, current_groupby, next_groupby, offset=0, limit=None):
        super(Inherit_aged_receviable, self)._aged_partner_report_custom_engine_common(options, internal_type, current_groupby, next_groupby, offset, limit)
        
        report = self.env['account.report'].browse(options['report_id'])
        report._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

        def minus_days(date_obj, days):
            return fields.Date.to_string(date_obj - relativedelta(days=days))

        date_to = fields.Date.from_string(options['date']['date_to'])
        periods = [
            (False, fields.Date.to_string(date_to)),
            (minus_days(date_to, 1), minus_days(date_to, 15)),
            (minus_days(date_to, 16), minus_days(date_to, 30)),
            (minus_days(date_to, 31), minus_days(date_to, 45)),
            (minus_days(date_to, 46), minus_days(date_to, 60)),
            (minus_days(date_to, 61), minus_days(date_to, 75)),
            (minus_days(date_to, 75), False),
        ]

        def build_result_dict(report, query_res_lines):
            rslt = {f'period{i}': 0 for i in range(len(periods))}

            for query_res in query_res_lines:
                for i in range(len(periods)):
                    period_key = f'period{i}'
                    rslt[period_key] += query_res[period_key]
            if current_groupby == 'id':
                query_res = query_res_lines[0] # We're grouping by id, so there is only 1 element in query_res_lines anyway
                currency = self.env['res.currency'].browse(query_res['currency_id'][0]) if len(query_res['currency_id']) == 1 else None
                rslt.update({
                    'due_date': query_res['due_date'][0] if len(query_res['due_date']) == 1 else None,
                    'amount_currency': query_res['amount_currency'],
                    'currency_id': query_res['currency_id'][0] if len(query_res['currency_id']) == 1 else None,
                    'currency': currency.display_name if currency else None,
                    'account_name': query_res['account_name'][0] if len(query_res['account_name']) == 1 else None,
                    'expected_date': query_res['expected_date'][0] if len(query_res['expected_date']) == 1 else None,
                    'total': None,
                    'has_sublines': query_res['aml_count'] > 0,
                    'invoice_date': query_res['invoice_date'][0] if len(query_res['invoice_date']) == 1 else None,
                    'exact_days': query_res['exact_days'][0] if len(query_res['exact_days']) == 1 else None,
                    'payment_term_days': query_res['payment_term_days'][0] if len(query_res['payment_term_days']) == 1 else None,
                    'over_due': query_res['over_due'][0] if len(query_res['over_due']) == 1 else None,

                     # custom fields end

                    #  new custom fields defined by Osama Nadeem
                    'new_code': query_res['new_code'][0] if len(query_res['new_code']) == 1 else None,
                    'partner_id': query_res['partner_id'][0] if query_res['partner_id'] else None,
                })
            else:
                rslt.update({
                    'due_date': None,
                    'amount_currency': None,
                    'currency_id': None,
                    'currency': None,
                    'account_name': None,
                    'expected_date': None,
                    'total': sum(rslt[f'period{i}'] for i in range(len(periods))),
                    'has_sublines': False,
                     # custom fields start
                    'invoice_date': None,
                    'exact_days': None,
                    'payment_term_days': None,
                    'over_due': None,
                    'new_code': None,

                })
            _logger.warning("from _aged_partner_report_custom_engine_common"+str(rslt))
            return rslt

        # Build period table
        period_table_format = ('(VALUES %s)' % ','.join("(%s, %s, %s)" for period in periods))
        params = list(chain.from_iterable(
            (period[0] or None, period[1] or None, i)
            for i, period in enumerate(periods)
        ))
        period_table = self.env.cr.mogrify(period_table_format, params).decode(self.env.cr.connection.encoding)

        # Build query
        tables, where_clause, where_params = report._query_get(options, 'strict_range', domain=[('account_id.account_type', '=', internal_type)])

        currency_table = self.env['res.currency']._get_query_currency_table(options)
        always_present_groupby = "period_table.period_index, currency_table.rate, currency_table.precision"
        if current_groupby:
            select_from_groupby = f"account_move_line.{current_groupby} AS grouping_key,"
            groupby_clause = f"account_move_line.{current_groupby}, {always_present_groupby}"
        else:
            select_from_groupby = ''
            groupby_clause = always_present_groupby
        select_period_query = ','.join(
            f"""
                CASE WHEN period_table.period_index = {i}
                THEN %s * (
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision))
                    - COALESCE(SUM(ROUND(part_debit.amount * currency_table.rate, currency_table.precision)), 0)
                    + COALESCE(SUM(ROUND(part_credit.amount * currency_table.rate, currency_table.precision)), 0)
                )
                ELSE 0 END AS period{i}
            """
            for i in range(len(periods))
        )

        tail_query, tail_params = report._get_engine_query_tail(offset, limit)
        query = f"""
            WITH period_table(date_start, date_stop, period_index) AS ({period_table})

            SELECT
                {select_from_groupby}
                %s * (
                    SUM(account_move_line.amount_currency)
                    - COALESCE(SUM(part_debit.debit_amount_currency), 0)
                    + COALESCE(SUM(part_credit.credit_amount_currency), 0)
                ) AS amount_currency,
                ARRAY_AGG(DISTINCT account_move_line.partner_id) AS partner_id,
                ARRAY_AGG(account_move_line.payment_id) AS payment_id,
                ARRAY_AGG(DISTINCT COALESCE(account_move_line.date_maturity, account_move_line.date)) AS report_date,
                ARRAY_AGG(DISTINCT account_move_line.expected_pay_date) AS expected_date,
                ARRAY_AGG(DISTINCT account.code) AS account_name,
                ARRAY_AGG(DISTINCT COALESCE(account_move_line.date_maturity, account_move_line.date)) AS due_date,
                ARRAY_AGG(DISTINCT account_move_line.currency_id) AS currency_id,
                COUNT(account_move_line.id) AS aml_count,
                ARRAY_AGG(account.code) AS account_code,
                
                ARRAY_AGG(DISTINCT COALESCE(move.invoice_date, move.invoice_date)) AS invoice_date,
                ARRAY_AGG(DISTINCT COALESCE(CURRENT_DATE - move.invoice_date, CURRENT_DATE - move.invoice_date)) AS exact_days,
                ARRAY_AGG(DISTINCT payment_term_line.days) AS payment_term_days,
                ARRAY_AGG(DISTINCT COALESCE((CURRENT_DATE - move.invoice_date) - payment_term_line.days, (CURRENT_DATE - move.invoice_date) - payment_term_line.days)) AS over_due,
                
                ARRAY_AGG(DISTINCT partner.new_code) AS new_code,
                ARRAY_AGG(DISTINCT move.name) AS name,
                
                {select_period_query}

            FROM {tables}
           
                JOIN account_move move ON move.id = account_move_line.move_id
            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            JOIN account_account account ON account.id = account_move_line.account_id
            JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            JOIN res_partner partner on partner.id = account_move_line.partner_id 
            JOIN account_payment_term payment_term on payment_term.id = move.invoice_payment_term_id 
            JOIN account_payment_term_line payment_term_line on payment_term_line.payment_id = payment_term.id
            LEFT JOIN LATERAL (
                SELECT
                    SUM(part.amount) AS amount,
                    SUM(part.debit_amount_currency) AS debit_amount_currency,
                    part.debit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %s
                GROUP BY part.debit_move_id
            ) part_debit ON part_debit.debit_move_id = account_move_line.id

            LEFT JOIN LATERAL (
                SELECT
                    SUM(part.amount) AS amount,
                    SUM(part.credit_amount_currency) AS credit_amount_currency,
                    part.credit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %s
                GROUP BY part.credit_move_id
            ) part_credit ON part_credit.credit_move_id = account_move_line.id

            JOIN period_table ON
                (
                    period_table.date_start IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
                )
                AND
                (
                    period_table.date_stop IS NULL
                    OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
                )

            WHERE {where_clause}

            GROUP BY {groupby_clause}

            HAVING
                (
                    SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))
                    - COALESCE(SUM(ROUND(part_debit.amount * currency_table.rate, currency_table.precision)), 0)
                ) != 0
                OR
                (
                    SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))
                    - COALESCE(SUM(ROUND(part_credit.amount * currency_table.rate, currency_table.precision)), 0)
                ) != 0
            {tail_query}
        """

        multiplicator = -1 if internal_type == 'liability_payable' else 1
        params = [
            multiplicator,
            *([multiplicator] * len(periods)),
            date_to,
            date_to,
            *where_params,
            *tail_params,
        ]
        self._cr.execute(query, params)
        query_res_lines = self._cr.dictfetchall()

        if not current_groupby:
            return build_result_dict(report, query_res_lines)
        else:
            rslt = []

            all_res_per_grouping_key = {}
            for query_res in query_res_lines:
                grouping_key = query_res['grouping_key']
                all_res_per_grouping_key.setdefault(grouping_key, []).append(query_res)

            for grouping_key, query_res_lines in all_res_per_grouping_key.items():
                rslt.append((grouping_key, build_result_dict(report, query_res_lines)))

            # _logger.warning("from _aged_partner_report_custom_engine_common_>>>>>>>>"+str(rslt)) 
            return rslt
    
    