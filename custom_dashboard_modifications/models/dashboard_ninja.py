from odoo import models, fields, api
from odoo.exceptions import UserError

from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
import datetime
import json
from odoo.addons.ks_dashboard_ninja.common_lib.ks_date_filter_selections import ks_get_date, ks_convert_into_local, \
    ks_convert_into_utc
from odoo.tools.safe_eval import safe_eval
import locale
from dateutil.parser import parse
from datetime import datetime,date

from dateutil.parser import parse
from odoo import fields



class KsDashboardNinjaBoard(models.Model):
    _inherit = 'ks_dashboard_ninja.board'


    def ks_set_date(self, ks_dashboard_id):
        ks_dashboard_rec = self.browse(ks_dashboard_id)
        if self._context.get('ksDateFilterSelection', False):
            ks_date_filter_selection = self._context['ksDateFilterSelection']
            if ks_date_filter_selection == 'l_custom':
                ks_start_dt_parse = parse(self._context['ksDateFilterStartDate'])
                ks_end_dt_parse = parse(self._context['ksDateFilterEndDate'])
                self = self.with_context(
                    ksDateFilterStartDate=fields.datetime.strptime(ks_start_dt_parse.strftime("%Y-%m-%d %H:%M:%S"),
                                                                "%Y-%m-%d %H:%M:%S"))
                self = self.with_context(
                    ksDateFilterEndDate=fields.datetime.strptime(ks_end_dt_parse.strftime("%Y-%m-%d %H:%M:%S"),
                                                                "%Y-%m-%d %H:%M:%S"))
                self = self.with_context(ksIsDefultCustomDateFilter=False)
        else:
            ks_date_filter_selection = ks_dashboard_rec.ks_date_filter_selection
            self = self.with_context(ksDateFilterStartDate=ks_dashboard_rec.ks_dashboard_start_date)
            self = self.with_context(ksDateFilterEndDate=ks_dashboard_rec.ks_dashboard_end_date)
            self = self.with_context(ksDateFilterSelection=ks_date_filter_selection)
            self = self.with_context(ksIsDefultCustomDateFilter=True)
            custom_query = f'''
            SELECT 
                CONCAT(
                    ROUND(
                        (COALESCE(SUM(CASE 
                            WHEN a.account_type IN ('liability_payable', 'liability_current') 
                            THEN aml.credit - aml.debit
                            ELSE 0 
                        END), 0) /
                        NULLIF(COALESCE(SUM(CASE 
                            WHEN a.account_type IN ('asset_cash', 'asset_receivable', 'asset_current', 'asset_non_current') 
                            THEN aml.debit - aml.credit 
                            ELSE 0 
                        END), 0), 0)) * 100, 
                        2
                    ), 
                    '%'
                ) AS debit_ratio
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id
            '''

            # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Debit Ratio")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query})
                

        if ks_date_filter_selection not in ['l_custom', 'l_none']:
            if ks_date_filter_selection in ['ls_past_until_now']:
                invoices = self.env['account.move'].search([('invoice_date', '!=', False)]).mapped('invoice_date')
                
                st_inv = sorted(invoices)
                start_date, end_date = st_inv[0],st_inv[-1]
                start_date = datetime.combine(start_date, datetime.min.time())
                end_date = datetime.combine(end_date, datetime.min.time())
                # raise UserError(str(start_date))
            else:    
                ks_date_data = ks_get_date(ks_date_filter_selection, self, 'datetime')
                start_date = ks_date_data["selected_start_date"]
                end_date = ks_date_data["selected_end_date"]
            
            
            # Format dates to string
            start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
            end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")


            # Update the custom query to include date filtering
            date_filter = ""
            if start_date_str and end_date_str:
                date_filter = f"WHERE aml.date BETWEEN '{start_date_str}' AND '{end_date_str}'"

            custom_query = f'''
            SELECT 
                CONCAT(
                    ROUND(
                        (COALESCE(SUM(CASE 
                            WHEN a.account_type IN ('liability_payable', 'liability_current') 
                            THEN aml.credit - aml.debit 
                            ELSE 0 
                        END), 0) /
                        NULLIF(COALESCE(SUM(CASE 
                            WHEN a.account_type IN ('asset_cash', 'asset_receivable', 'asset_current', 'asset_non_current') 
                            THEN aml.debit - aml.credit 
                            ELSE 0 
                        END), 0), 0)) * 100, 
                        2
                    ), 
                    '%'
                ) AS debit_ratio
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id
            {date_filter}
            '''

            # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Debit Ratio")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query})

            

            custom_query_working_capital = f'''
            SELECT 
                ROUND(
                    (SUM(CASE 
                        WHEN a.account_type IN ('asset_cash', 'asset_current', 'asset_non_current') 
                        THEN aml.debit - aml.credit 
                        ELSE 0 
                    END) 
                    - 
                    SUM(CASE 
                        WHEN a.account_type IN ('liability_payable', 'liability_current') 
                        THEN aml.credit - aml.debit 
                        ELSE 0 
                    END)), 
                    2
                ) AS working_capital
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id
            {date_filter}
            '''


            # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Working Capital")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query_working_capital})

            
            custom_query_current_ratio = f'''
            SELECT 
                CONCAT(
                    ROUND(
                        COALESCE(
                            SUM(CASE 
                                WHEN a.account_type IN ('asset_cash', 'asset_receivable', 'asset_current') 
                                THEN aml.debit - aml.credit 
                                ELSE 0 
                            END), 0
                        ) /
                        NULLIF(
                            SUM(CASE 
                                WHEN a.account_type IN ('liability_payable', 'liability_current') 
                                THEN aml.credit - aml.debit 
                                ELSE 0 
                            END), 0
                        ) * 100, 
                        2
                    ), 
                    '%'
                ) AS current_ratio_percentage
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id
            {date_filter}
            '''

                        # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Current Ratio")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query_current_ratio})



            self = self.with_context(ksDateFilterStartDate=start_date, ksDateFilterEndDate=end_date)
        else:
            custom_query = f'''
            SELECT 
                CONCAT(
                    ROUND(
                        (COALESCE(SUM(CASE 
                            WHEN a.account_type IN ('liability_payable', 'liability_current') 
                            THEN aml.credit - aml.debit 
                            ELSE 0 
                        END), 0) /
                        NULLIF(COALESCE(SUM(CASE 
                            WHEN a.account_type IN ('asset_cash', 'asset_receivable', 'asset_current', 'asset_non_current') 
                            THEN aml.debit - aml.credit 
                            ELSE 0 
                        END), 0), 0)) * 100, 
                        2
                    ), 
                    '%'
                ) AS debit_ratio
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id
            '''

            # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Debit Ratio")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query})

            custom_query_working_capital = f'''
            SELECT 
                ROUND(
                    (SUM(CASE 
                        WHEN a.account_type IN ('asset_cash', 'asset_current', 'asset_non_current') 
                        THEN aml.debit - aml.credit 
                        ELSE 0 
                    END) 
                    - 
                    SUM(CASE 
                        WHEN a.account_type IN ('liability_payable', 'liability_current') 
                        THEN aml.credit - aml.debit 
                        ELSE 0 
                    END)), 
                    2
                ) AS working_capital
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id

            '''


            # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Working Capital")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query_working_capital})


            custom_query_current_ratio = f'''
            SELECT 
                CONCAT(
                    ROUND(
                        COALESCE(
                            SUM(CASE 
                                WHEN a.account_type IN ('asset_cash', 'asset_receivable', 'asset_current') 
                                THEN aml.debit - aml.credit 
                                ELSE 0 
                            END), 0
                        ) /
                        NULLIF(
                            SUM(CASE 
                                WHEN a.account_type IN ('liability_payable', 'liability_current') 
                                THEN  aml.credit - aml.debit   
                                ELSE 0 
                            END), 0
                        ) * 100, 
                        2
                    ), 
                    '%'
                ) AS current_ratio_percentage
            FROM 
                account_move_line aml
            JOIN 
                account_account a ON aml.account_id = a.id
            '''

                        # Find the item by name and update the ks_custom_query field
            item = self.env['ks_dashboard_ninja.item'].search([('name', '=', "Current Ratio")], limit=1)
            if item:
                item.write({'ks_custom_query': custom_query_current_ratio})

        return self