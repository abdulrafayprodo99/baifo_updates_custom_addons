# # # from odoo.exceptions import UserError, AccessError, ValidationError
# # # from odoo import _, api, fields, models
# # # from datetime import datetime

# # # # Fetch today's date
# # # today_date = datetime.today()

# # # # Format the date
# # # formatted_date = today_date.strftime("%Y-%m-%d")


# # # class CustomReport(models.AbstractModel):
# # #     _name = 'report.group_wise_summary.sales_group_summary_reports'
# # #     _description = 'Product Group Wise Sales Summary Report'

# # #     @api.model
# # #     def _get_report_values(self, docids, data=None):
# # #         other_details = {}
# # #         date_from = data.get('date_from')
# # #         date_to = data.get('date_to')
# # #         currency_id = data.get('currency_id')
# # #         product_id = data.get('product_id')
        

# # #         other_details.update({
# # #                 'date_from': date_from,
# # #                 'date_to': date_to,
# # #                 'currency_id': currency_id,
# # #                 'product_id': product_id,

# # #             })
        

# # #         if product_id != []:
# # #             product_id_str = ','.join(map(str,product_id))

# # #         if currency_id and currency_id != []:
# # #             currency_id_str = ','.join(map(str,currency_id))
        
# # #         cr = self._cr
# # #         query = ("""
# # #             SELECT
# # #                 distinct  
# # #                 cur.name as cur_name,
# # #                 cust.x_studio_new_code as code, 
# # #                 inv.id AS invoice_id,
# # #                 cust.name AS customer_name,
# # #                 prod.default_code AS product_default_code,
# # #                 pt.name ->> 'en_US' AS product_name,
# # #                 inv_line.name AS product_description,
# # #                 uom.name ->> 'en_US' AS unit,
# # #                 inv_line.quantity AS quantity,
# # #                 (inv_line.price_unit * inv_line.quantity) AS gross_amount,
# # #                 inv_line.price_unit AS value_excl,
# # #                 (inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# # #                 inv_line.price_total AS total_amount
# # #             FROM 
# # #                 account_move_line inv_line
# # #             INNER JOIN 
# # #                 account_move inv ON inv_line.move_id = inv.id
# # #             INNER JOIN 
# # #                 product_product prod ON inv_line.product_id = prod.id
# # #             INNER JOIN 
# # #                 product_template pt on pt.id  =  prod.product_tmpl_id
# # #             INNER JOIN 
# # #                 product_category pc ON pc.id = pt.categ_id
# # #             INNER JOIN 
# # #                 res_partner cust ON inv.partner_id = cust.id
# # #             INNER JOIN 
# # #                 res_currency cur ON cur.id = inv.currency_id
# # #             LEFT JOIN 
# # #                 account_tax tax ON inv_line.tax_line_id = tax.id
# # #             LEFT JOIN 
# # #                 uom_uom uom ON inv_line.product_uom_id = uom.id
# # #             WHERE
# # #                 inv.move_type = 'out_invoice'  
# # #                 AND inv.state = 'posted'
# # #         """) 



# # #         where_clauses = []

# # #         if currency_id:
# # #             where_clauses.append("AND cur.id in (%s)" % currency_id_str)
# # #         if product_id:
# # #             where_clauses.append("AND pt.id in (%s)" % product_id_str)
# # #         if date_from:
# # #             date_to = formatted_date
# # #             where_clauses.append("AND inv.invoice_date between '%s' AND '%s'" % (date_from, date_to))
# # #         if date_from and date_to:
# # #             where_clauses.append("AND inv.invoice_date between '%s' AND '%s'" % (date_from, date_to))
# # #         if date_from and date_to and currency_id:
# # #             where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))
# # #         if date_from and date_to and product_id:
# # #             where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND pt.id in (%s)" % (date_from, date_to, product_id_str))
        
# # #         if date_from and date_to and currency_id and product_id:
# # #             where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s) AND pt.id in (%s)" % (date_from, date_to, currency_id_str, product_id_str))

# # #         # if date_from and currency_id:
# # #         #     where_clauses.append("AND inv.invoice_date = '%s' AND cur.id in (%s)" % (date_from, currency_id_str))
# # #         # if date_from  and product_id:
# # #         #     where_clauses.append("AND inv.invoice_date = '%s' AND pt.id in (%s)" % (date_from, product_id_str))

        
# # #         query += ' '.join(where_clauses)
# # #         query += 'order by cust.name'
        
        
# # #         cr.execute(query)
# # #         result = cr.dictfetchall()

# # #         totals = {
# # #             'quantity': sum(item['quantity'] for item in result),
# # #             'gross_amount': sum(item['gross_amount'] for item in result),
# # #             'value_excl': sum(item['value_excl'] for item in result),
# # #             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
# # #             'total_amount': sum(item['total_amount'] for item in result),
# # #         }

# # #         return {
# # #             'data': result,
# # #             'totals': totals,
# # #             'other': other_details,
# # #         }



# # # from odoo.exceptions import UserError, AccessError, ValidationError
# # # from odoo import _, api, fields, models
# # # from datetime import datetime

# # # # Fetch today's date
# # # today_date = datetime.today()

# # # # Format the date
# # # formatted_date = today_date.strftime("%Y-%m-%d")


# # # class CustomReport(models.AbstractModel):
# # #     _name = 'report.group_wise_summary.sales_group_summary_reports'
# # #     _description = 'Product Group Wise Sales Summary Report'

# # #     @api.model
# # #     def _get_report_values(self, docids, data=None):
# # #         other_details = {}
# # #         date_from = data.get('date_from')
# # #         date_to = data.get('date_to')
# # #         currency_id = data.get('currency_id')
# # #         product_id = data.get('product_id')
        
# # #         other_details.update({
# # #             'date_from': date_from,
# # #             'date_to': date_to,
# # #             'currency_id': currency_id,
# # #             'product_id': product_id,
# # #         })
        
# # #         if product_id != []:
# # #             product_id_str = ','.join(map(str, product_id))

# # #         if currency_id and currency_id != []:
# # #             currency_id_str = ','.join(map(str, currency_id))
        
# # #         cr = self._cr
# # #         query = ("""
# # #             SELECT
# # #                 DISTINCT  
# # #                 cur.name AS cur_name,
# # #                 cust.x_studio_new_code AS code, 
# # #                 inv.id AS invoice_id,
# # #                 cust.name AS customer_name,
# # #                 prod.default_code AS product_default_code,
# # #                 pt.name ->> 'en_US' AS product_name,
# # #                 inv_line.name AS product_description,
# # #                 uom.name ->> 'en_US' AS unit,
# # #                 inv_line.quantity AS quantity,
# # #                 (inv_line.price_unit * inv_line.quantity) AS gross_amount,
# # #                 inv_line.price_unit AS value_excl,
# # #                 (inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# # #                 inv_line.price_total AS total_amount
# # #             FROM 
# # #                 account_move_line inv_line
# # #             INNER JOIN 
# # #                 account_move inv ON inv_line.move_id = inv.id
# # #             INNER JOIN 
# # #                 product_product prod ON inv_line.product_id = prod.id
# # #             INNER JOIN 
# # #                 product_template pt ON pt.id = prod.product_tmpl_id
# # #             INNER JOIN 
# # #                 product_category pc ON pc.id = pt.categ_id
# # #             INNER JOIN 
# # #                 res_partner cust ON inv.partner_id = cust.id
# # #             INNER JOIN 
# # #                 res_currency cur ON cur.id = inv.currency_id
# # #             LEFT JOIN 
# # #                 account_tax tax ON inv_line.tax_line_id = tax.id
# # #             LEFT JOIN 
# # #                 uom_uom uom ON inv_line.product_uom_id = uom.id
# # #             WHERE
# # #                 inv.move_type = 'out_invoice'  
# # #                 AND inv.state = 'posted'
# # #         """)

# # #         where_clauses = []

# # #         if currency_id:
# # #             where_clauses.append("AND cur.id IN (%s)" % currency_id_str)
# # #         if product_id:
# # #             where_clauses.append("AND pt.id IN (%s)" % product_id_str)
# # #         if date_from:
# # #             date_to = formatted_date
# # #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# # #         if date_from and date_to:
# # #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# # #         if date_from and date_to and currency_id:
# # #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s' AND cur.id IN (%s)" % (date_from, date_to, currency_id_str))
# # #         if date_from and date_to and product_id:
# # #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s' AND pt.id IN (%s)" % (date_from, date_to, product_id_str))
# # #         if date_from and date_to and currency_id and product_id:
# # #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s' AND cur.id IN (%s) AND pt.id IN (%s)" % (date_from, date_to, currency_id_str, product_id_str))
        
# # #         query += ' '.join(where_clauses)
# # #         query += ' ORDER BY prod.default_code'  # Added order by clause to sort by product code
        
# # #         cr.execute(query)
# # #         result = cr.dictfetchall()

# # #         totals = {
# # #             'quantity': sum(item['quantity'] for item in result),
# # #             'gross_amount': sum(item['gross_amount'] for item in result),
# # #             'value_excl': sum(item['value_excl'] for item in result),
# # #             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
# # #             'total_amount': sum(item['total_amount'] for item in result),
# # #         }

# # #         return {
# # #             'data': result,
# # #             'totals': totals,
# # #             'other': other_details,
# # #         }



# # from odoo.exceptions import UserError, AccessError, ValidationError
# # from odoo import _, api, fields, models
# # from datetime import datetime

# # # Fetch today's date
# # today_date = datetime.today()

# # # Format the date
# # formatted_date = today_date.strftime("%Y-%m-%d")


# # class CustomReport(models.AbstractModel):
# #     _name = 'report.group_wise_summary.sales_group_summary_reports'
# #     _description = 'Product Group Wise Sales Summary Report'

# #     @api.model
# #     def _get_report_values(self, docids, data=None):
# #         other_details = {}
# #         date_from = data.get('date_from')
# #         date_to = data.get('date_to')
# #         currency_id = data.get('currency_id')
# #         product_id = data.get('product_id')
        
# #         other_details.update({
# #             'date_from': date_from,
# #             'date_to': date_to,
# #             'currency_id': currency_id,
# #             'product_id': product_id,
# #         })
        
# #         if product_id != []:
# #             product_id_str = ','.join(map(str, product_id))

# #         if currency_id and currency_id != []:
# #             currency_id_str = ','.join(map(str, currency_id))
        
# #         cr = self._cr
# #         query = ("""
# #             SELECT
# #                 cur.name AS cur_name,
# #                 prod.default_code AS product_default_code,
# #                 pt.name ->> 'en_US' AS product_name,
# #                 uom.name ->> 'en_US' AS unit,
# #                 SUM(inv_line.quantity) AS quantity,
# #                 SUM(inv_line.price_unit * inv_line.quantity) AS gross_amount,
# #                 SUM(inv_line.price_unit) AS value_excl,
# #                 SUM(inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# #                 SUM(inv_line.price_total) AS total_amount
# #             FROM 
# #                 account_move_line inv_line
# #             INNER JOIN 
# #                 account_move inv ON inv_line.move_id = inv.id
# #             INNER JOIN 
# #                 product_product prod ON inv_line.product_id = prod.id
# #             INNER JOIN 
# #                 product_template pt ON pt.id = prod.product_tmpl_id
# #             INNER JOIN 
# #                 product_category pc ON pc.id = pt.categ_id
# #             INNER JOIN 
# #                 res_partner cust ON inv.partner_id = cust.id
# #             INNER JOIN 
# #                 res_currency cur ON cur.id = inv.currency_id
# #             LEFT JOIN 
# #                 account_tax tax ON inv_line.tax_line_id = tax.id
# #             LEFT JOIN 
# #                 uom_uom uom ON inv_line.product_uom_id = uom.id
# #             WHERE
# #                 inv.move_type = 'out_invoice'  
# #                 AND inv.state = 'posted'
# #         """)

# #         where_clauses = []

# #         if currency_id:
# #             where_clauses.append("AND cur.id IN (%s)" % currency_id_str)
# #         if product_id:
# #             where_clauses.append("AND pt.id IN (%s)" % product_id_str)
# #         if date_from:
# #             date_to = formatted_date
# #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# #         if date_from and date_to:
# #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# #         if date_from and date_to and currency_id:
# #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s' AND cur.id IN (%s)" % (date_from, date_to, currency_id_str))
# #         if date_from and date_to and product_id:
# #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s' AND pt.id IN (%s)" % (date_from, date_to, product_id_str))
# #         if date_from and date_to and currency_id and product_id:
# #             where_clauses.append("AND inv.invoice_date BETWEEN '%s' AND '%s' AND cur.id IN (%s) AND pt.id IN (%s)" % (date_from, date_to, currency_id_str, product_id_str))
        
# #         query += ' '.join(where_clauses)
# #         query += ' GROUP BY cur.name, prod.default_code, pt.name, uom.name'  # Added GROUP BY clause to group by product code
# #         query += ' ORDER BY prod.default_code'  # Added order by clause to sort by product code
        
# #         cr.execute(query)
# #         result = cr.dictfetchall()

# #         totals = {
# #             'quantity': sum(item['quantity'] for item in result),
# #             'gross_amount': sum(item['gross_amount'] for item in result),
# #             'value_excl': sum(item['value_excl'] for item in result),
# #             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
# #             'total_amount': sum(item['total_amount'] for item in result),
# #         }

# #         return {
# #             'data': result,
# #             'totals': totals,
# #             'other': other_details,
# #         }





# from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo import _, api, fields, models
# from datetime import datetime

# # Fetch today's date
# today_date = datetime.today()

# # Format the date
# formatted_date = today_date.strftime("%Y-%m-%d")


# class CustomReport(models.AbstractModel):
#     _name = 'report.group_wise_summary.sales_group_summary_reports'
#     _description = 'Product Group Wise Sales Summary Report'

#     @api.model
#     def _get_report_values(self, docids, data=None):
#         other_details = {}
#         date_from = data.get('date_from')
#         date_to = data.get('date_to')
#         currency_id = data.get('currency_id')
#         product_id = data.get('product_id')
        
#         other_details.update({
#             'date_from': date_from,
#             'date_to': date_to,
#             'currency_id': currency_id,
#             'product_id': product_id,
#         })
        
#         product_id_str = ','.join(map(str, product_id)) if product_id else ''
#         currency_id_str = ','.join(map(str, currency_id)) if currency_id else ''
        
#         cr = self._cr
#         query = """
#             SELECT
#                 cur.name AS cur_name,
#                 prod.default_code AS product_default_code,
#                 pt.name ->> 'en_US' AS product_name,
#                 uom.name ->> 'en_US' AS unit,
#                 SUM(inv_line.quantity) AS quantity,
#                 SUM(inv_line.price_unit * inv_line.quantity) AS gross_amount,
#                 SUM(CASE 
#                         WHEN cur.name = 'USD' THEN inv_line.price_subtotal * inv.currency_rate
#                         ELSE inv_line.price_subtotal 
#                     END) AS value_excl,
#                 SUM(inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
#                 SUM(CASE 
#                         WHEN cur.name = 'USD' THEN inv_line.price_total * inv.currency_rate
#                         ELSE inv_line.price_total 
#                     END) AS total_amount
#             FROM 
#                 account_move_line inv_line
#             INNER JOIN 
#                 account_move inv ON inv_line.move_id = inv.id
#             INNER JOIN 
#                 product_product prod ON inv_line.product_id = prod.id
#             INNER JOIN 
#                 product_template pt ON pt.id = prod.product_tmpl_id
#             INNER JOIN 
#                 product_category pc ON pc.id = pt.categ_id
#             INNER JOIN 
#                 res_partner cust ON inv.partner_id = cust.id
#             INNER JOIN 
#                 res_currency cur ON cur.id = inv.currency_id
#             LEFT JOIN 
#                 account_tax tax ON inv_line.tax_line_id = tax.id
#             LEFT JOIN 
#                 uom_uom uom ON inv_line.product_uom_id = uom.id
#             WHERE
#                 inv.move_type = 'out_invoice'  
#                 AND inv.state = 'posted'
#                 AND pt.name ->> 'en_US' != 'Opening Balance'
#         """

#         where_clauses = []

#         if currency_id_str:
#             where_clauses.append("cur.id IN (%s)" % currency_id_str)
#         if product_id_str:
#             where_clauses.append("pt.id IN (%s)" % product_id_str)
#         if date_from and date_to:
#             where_clauses.append("inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
#         elif date_from:  # In case only date_from is provided
#             where_clauses.append("inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, formatted_date))

#         if where_clauses:
#             query += ' AND ' + ' AND '.join(where_clauses)

#         query += ' GROUP BY cur.name, prod.default_code, pt.name, uom.name'
#         query += ' ORDER BY prod.default_code'

#         cr.execute(query)
#         result = cr.dictfetchall()

#         totals = {
#             'quantity': sum(item['quantity'] for item in result),
#             'gross_amount': sum(item['gross_amount'] for item in result),
#             'value_excl': sum(item['value_excl'] for item in result),
#             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
#             'total_amount': sum(item['total_amount'] for item in result),
#         }

#         return {
#             'data': result,
#             'totals': totals,
#             'other': other_details,
#         }





from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import _, api, fields, models
from datetime import datetime

# Fetch today's date
today_date = datetime.today()

# Format the date
formatted_date = today_date.strftime("%Y-%m-%d")

class CustomReport(models.AbstractModel):
    _name = 'report.group_wise_summary.sales_group_summary_reports'
    _description = 'Product Group Wise Sales Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        other_details = {}
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        currency_id = data.get('currency_id')
        product_id = data.get('product_id')
        prod_sel = data.get('prod_sel')
        product_code_from = data.get('product_code_from')
        product_code_to = data.get('product_code_to')



        other_details.update({
            'date_from': date_from,
            'date_to': date_to,
            'currency_id': currency_id,
            'product_id': product_id,
            'prod_sel': prod_sel,
            'product_code_from': product_code_from,
            'product_code_to': product_code_to,
        })

        cr = self._cr
        query = """
            SELECT
                cur.name AS cur_name,
                prod.default_code AS product_default_code,
                pt.name ->> 'en_US' AS product_name,
                uom.name ->> 'en_US' AS unit,
                SUM(inv_line.quantity) AS quantity,
                SUM(inv_line.price_unit * inv_line.quantity) AS gross_amount,
                SUM(CASE 
                        WHEN cur.name = 'USD' THEN inv_line.price_subtotal * inv.currency_rate
                        ELSE inv_line.price_subtotal 
                    END) AS value_excl,
                SUM(inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
                SUM(CASE 
                        WHEN cur.name = 'USD' THEN inv_line.price_total * inv.currency_rate
                        ELSE inv_line.price_total 
                    END) AS total_amount
            FROM 
                account_move_line inv_line
            INNER JOIN 
                account_move inv ON inv_line.move_id = inv.id
            INNER JOIN 
                product_product prod ON inv_line.product_id = prod.id
            INNER JOIN 
                product_template pt ON pt.id = prod.product_tmpl_id
            INNER JOIN 
                product_category pc ON pc.id = pt.categ_id
            INNER JOIN 
                res_partner cust ON inv.partner_id = cust.id
            INNER JOIN 
                res_currency cur ON cur.id = inv.currency_id
            LEFT JOIN 
                account_tax tax ON inv_line.tax_line_id = tax.id
            LEFT JOIN 
                uom_uom uom ON inv_line.product_uom_id = uom.id
            WHERE
                inv.move_type = 'out_invoice'  
                AND inv.state = 'posted'
                AND pt.name ->> 'en_US' != 'Opening Balance'
        """

        where_clauses = []
        params = []

        # Currency filter
        if currency_id:
            where_clauses.append("cur.id IN %s")
            params.append(tuple(currency_id))

        # Date filter
        if date_from and date_to:
            where_clauses.append("inv.invoice_date BETWEEN %s AND %s")
            params.extend([date_from, date_to])
        elif date_from:
            where_clauses.append("inv.invoice_date BETWEEN %s AND %s")
            params.extend([date_from, formatted_date])

        # Product range filter
        if product_code_from and product_code_to:
            where_clauses.append("prod.default_code BETWEEN %s AND %s")
            params.extend([product_code_from, product_code_to])

        if where_clauses:
            query += ' AND ' + ' AND '.join(where_clauses)

        query += ' GROUP BY cur.name, prod.default_code, pt.name, uom.name'
        query += ' ORDER BY prod.default_code'

        cr.execute(query, params)
        result = cr.dictfetchall()

        totals = {
            'quantity': sum(item['quantity'] for item in result),
            'gross_amount': sum(item['gross_amount'] for item in result),
            'value_excl': sum(item['value_excl'] for item in result),
            'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
            'total_amount': sum(item['total_amount'] for item in result),
        }


        # raise UserError(str(other_details))
        return {
            'data': result,
            'totals': totals,
            'other': other_details,
        }

