# # # # from odoo.exceptions import UserError, AccessError, ValidationError
# # # # from odoo import _, api, fields, models
# # # # from datetime import datetime

# # # # # Fetch today's date
# # # # today_date = datetime.today()

# # # # # Format the date
# # # # formatted_date = today_date.strftime("%Y-%m-%d")


# # # # class CustomReport(models.AbstractModel):
# # # #     _name = 'report.sales_summary.sales_summary_reports'
# # # #     _description = 'Sales Summary Report'

# # # #     @api.model
# # # #     def _get_report_values(self, docids, data=None):
# # # #         other_details = {}
# # # #         date_from = data.get('date_from')
# # # #         date_to = data.get('date_to')
# # # #         cust_sel = data.get('cust_sel')
# # # #         prod_sel = data.get('prod_sel')
# # # #         customer_id = data.get('customer_id')
# # # #         category_id = data.get('category_id')
# # # #         currency_id = data.get('currency_id')
# # # #         product_id = data.get('product_id')
# # # #         product_code_from = data.get('product_code_from')
# # # #         product_code_to = data.get('product_code_to')

# # # #         other_details.update({
# # # #             'from_date': date_from,
# # # #             'to_date': date_to,
# # # #             'cust_sel': cust_sel,
# # # #             'prod_sel': prod_sel,
# # # #             'customer_id': customer_id,
# # # #             'category_id': category_id,
# # # #             'currency_id': currency_id,
# # # #             'product_id': product_id,
# # # #             'product_code_from': product_code_from,
# # # #             'product_code_to': product_code_to,
# # # #         })
        
# # # #         if category_id and category_id != []:
# # # #             category_id_str = ','.join(map(str, category_id))
# # # #         if customer_id and customer_id != []:
# # # #             customer_id_str = ','.join(map(str, customer_id))
# # # #         if product_id and product_id != []:
# # # #             product_id_str = ','.join(map(str, product_id))
# # # #         if currency_id and currency_id != []:
# # # #             currency_id_str = ','.join(map(str, currency_id))
        
# # # #         cr = self._cr
# # # #         query = ("""
# # # #             SELECT
# # # #                 DISTINCT  
# # # #                 cur.name AS cur_name,
# # # #                 cust.x_studio_new_code AS code, 
# # # #                 inv.id AS invoice_id,
# # # #                 cust.name AS customer_name,
# # # #                 prod.default_code AS product_default_code,
# # # #                 pt.name ->> 'en_US' AS product_name,
# # # #                 inv_line.name AS product_description,
# # # #                 uom.name ->> 'en_US' AS unit,
# # # #                 inv_line.quantity AS quantity,
# # # #                 (inv_line.price_unit * inv_line.quantity) AS gross_amount,
# # # #                 inv_line.price_unit AS value_excl,
# # # #                 (inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# # # #                 inv_line.price_total AS total_amount
# # # #             FROM 
# # # #                 account_move_line inv_line
# # # #             INNER JOIN 
# # # #                 account_move inv ON inv_line.move_id = inv.id
# # # #             INNER JOIN 
# # # #                 product_product prod ON inv_line.product_id = prod.id
# # # #             INNER JOIN 
# # # #                 product_template pt ON pt.id = prod.product_tmpl_id
# # # #             INNER JOIN 
# # # #                 product_category pc ON pc.id = pt.categ_id
# # # #             INNER JOIN 
# # # #                 res_partner cust ON inv.partner_id = cust.id
# # # #             INNER JOIN 
# # # #                 res_currency cur ON cur.id = inv.currency_id
# # # #             LEFT JOIN 
# # # #                 account_tax tax ON inv_line.tax_line_id = tax.id
# # # #             LEFT JOIN 
# # # #                 uom_uom uom ON inv_line.product_uom_id = uom.id
# # # #             WHERE
# # # #                 inv.move_type = 'out_invoice'  
# # # #                 AND inv.state = 'posted'
# # # #         """)

# # # #         where_clauses = []

# # # #         if currency_id:
# # # #             where_clauses.append("cur.id IN (%s)" % currency_id_str)
# # # #         if date_from and date_to:
# # # #             where_clauses.append("inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# # # #         if customer_id:
# # # #             where_clauses.append("cust.id IN (%s)" % customer_id_str)
# # # #         if product_id:
# # # #             where_clauses.append("pt.id IN (%s)" % product_id_str)
# # # #         if product_code_from and product_code_to:
# # # #             where_clauses.append("pt.default_code BETWEEN '%s' AND '%s'" % (product_code_from, product_code_to))
# # # #         if category_id:
# # # #             where_clauses.append("pc.id IN (%s)" % category_id_str)

# # # #         if where_clauses:
# # # #             query += ' AND ' + ' AND '.join(where_clauses)

# # # #         query += ' ORDER BY prod.default_code'

# # # #         cr.execute(query)
# # # #         result = cr.dictfetchall()

# # # #         totals = {
# # # #             'quantity': sum(item['quantity'] for item in result),
# # # #             'gross_amount': sum(item['gross_amount'] for item in result),
# # # #             'value_excl': sum(item['value_excl'] for item in result),
# # # #             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
# # # #             'total_amount': sum(item['total_amount'] for item in result),
# # # #         }

# # # #         return {
# # # #             'data': result,
# # # #             'totals': totals,
# # # #             'other': other_details,
# # # #         }



# # # # Bilal Correct Code start from here  

# # # # from odoo.exceptions import UserError, AccessError, ValidationError
# # # # from odoo import _, api, fields, models
# # # # from datetime import datetime

# # # # # Fetch today's date
# # # # today_date = datetime.today()

# # # # # Format the date
# # # # formatted_date = today_date.strftime("%Y-%m-%d")


# # # # class CustomReport(models.AbstractModel):
# # # #     _name = 'report.sales_summary.sales_summary_reports'
# # # #     _description = 'Sales Summary Report'

# # # #     @api.model
# # # #     def _get_report_values(self, docids, data=None):
# # # #         other_details = {}
# # # #         date_from = data.get('date_from')
# # # #         date_to = data.get('date_to')
# # # #         cust_sel = data.get('cust_sel')
# # # #         prod_sel = data.get('prod_sel')
# # # #         customer_id = data.get('customer_id')
# # # #         category_id = data.get('category_id')
# # # #         currency_id = data.get('currency_id')
# # # #         product_id = data.get('product_id')
# # # #         product_code_from = data.get('product_code_from')
# # # #         product_code_to = data.get('product_code_to')

# # # #         other_details.update({
# # # #             'from_date': date_from,
# # # #             'to_date': date_to,
# # # #             'cust_sel': cust_sel,
# # # #             'prod_sel': prod_sel,
# # # #             'customer_id': customer_id,
# # # #             'category_id': category_id,
# # # #             'currency_id': currency_id,
# # # #             'product_id': product_id,
# # # #             'product_code_from': product_code_from,
# # # #             'product_code_to': product_code_to,
# # # #         })
        
# # # #         if category_id and category_id != []:
# # # #             category_id_str = ','.join(map(str, category_id))
# # # #         if customer_id and customer_id != []:
# # # #             customer_id_str = ','.join(map(str, customer_id))
# # # #         if product_id and product_id != []:
# # # #             product_id_str = ','.join(map(str, product_id))
# # # #         if currency_id and currency_id != []:
# # # #             currency_id_str = ','.join(map(str, currency_id))
        
# # # #         cr = self._cr
# # # #         query = ("""
# # # #             SELECT
# # # #                 DISTINCT  
# # # #                 cur.name AS cur_name,
# # # #                 cust.x_studio_new_code AS code, 
# # # #                 inv.id AS invoice_id,
# # # #                 cust.name AS customer_name,
# # # #                 prod.default_code AS product_default_code,
# # # #                 pt.name ->> 'en_US' AS product_name,
# # # #                 inv_line.name AS product_description,
# # # #                 uom.name ->> 'en_US' AS unit,
# # # #                 inv_line.quantity AS quantity,
# # # #                 (inv_line.price_unit * inv_line.quantity) AS gross_amount,
# # # #                 inv_line.price_unit AS value_excl,
# # # #                 (inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# # # #                 inv_line.price_total AS total_amount
# # # #             FROM 
# # # #                 account_move_line inv_line
# # # #             INNER JOIN 
# # # #                 account_move inv ON inv_line.move_id = inv.id
# # # #             INNER JOIN 
# # # #                 product_product prod ON inv_line.product_id = prod.id
# # # #             INNER JOIN 
# # # #                 product_template pt ON pt.id = prod.product_tmpl_id
# # # #             INNER JOIN 
# # # #                 product_category pc ON pc.id = pt.categ_id
# # # #             INNER JOIN 
# # # #                 res_partner cust ON inv.partner_id = cust.id
# # # #             INNER JOIN 
# # # #                 res_currency cur ON cur.id = inv.currency_id
# # # #             LEFT JOIN 
# # # #                 account_tax tax ON inv_line.tax_line_id = tax.id
# # # #             LEFT JOIN 
# # # #                 uom_uom uom ON inv_line.product_uom_id = uom.id
# # # #             WHERE
# # # #                 inv.move_type = 'out_invoice'  
# # # #                 AND inv.state = 'posted'
# # # #                 AND pt.name ->> 'en_US' != 'Opening Balance'
# # # #         """)

# # # #         where_clauses = []

# # # #         if currency_id:
# # # #             where_clauses.append("cur.id IN (%s)" % currency_id_str)
# # # #         if date_from and date_to:
# # # #             where_clauses.append("inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# # # #         if customer_id:
# # # #             where_clauses.append("cust.id IN (%s)" % customer_id_str)
# # # #         if product_id:
# # # #             where_clauses.append("pt.id IN (%s)" % product_id_str)
# # # #         if product_code_from and product_code_to:
# # # #             where_clauses.append("pt.default_code BETWEEN '%s' AND '%s'" % (product_code_from, product_code_to))
# # # #         if category_id:
# # # #             where_clauses.append("pc.id IN (%s)" % category_id_str)

# # # #         if where_clauses:
# # # #             query += ' AND ' + ' AND '.join(where_clauses)

# # # #         query += ' ORDER BY prod.default_code'

# # # #         cr.execute(query)
# # # #         result = cr.dictfetchall()

# # # #         totals = {
# # # #             'quantity': sum(item['quantity'] for item in result),
# # # #             'gross_amount': sum(item['gross_amount'] for item in result),
# # # #             'value_excl': sum(item['value_excl'] for item in result),
# # # #             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
# # # #             'total_amount': sum(item['total_amount'] for item in result),
# # # #         }

# # # #         return {
# # # #             'data': result,
# # # #             'totals': totals,
# # # #             'other': other_details,
# # # #         }

# # # # Bilal Correct Code End from here  





# # # from odoo.exceptions import UserError, AccessError, ValidationError
# # # from odoo import _, api, fields, models
# # # from datetime import datetime

# # # # Fetch today's date
# # # today_date = datetime.today()

# # # # Format the date
# # # formatted_date = today_date.strftime("%Y-%m-%d")


# # # class CustomReport(models.AbstractModel):
# # #     _name = 'report.sales_summary.sales_summary_reports'
# # #     _description = 'Sales Summary Report'

# # #     @api.model
# # #     def _get_report_values(self, docids, data=None):
# # #         other_details = {}
# # #         date_from = data.get('date_from')
# # #         date_to = data.get('date_to')
# # #         cust_sel = data.get('cust_sel')
# # #         prod_sel = data.get('prod_sel')
# # #         customer_id = data.get('customer_id')
# # #         category_id = data.get('category_id')
# # #         currency_id = data.get('currency_id')
# # #         product_id = data.get('product_id')
# # #         product_code_from = data.get('product_code_from')
# # #         product_code_to = data.get('product_code_to')

# # #         other_details.update({
# # #             'from_date': date_from,
# # #             'to_date': date_to,
# # #             'cust_sel': cust_sel,
# # #             'prod_sel': prod_sel,
# # #             'customer_id': customer_id,
# # #             'category_id': category_id,
# # #             'currency_id': currency_id,
# # #             'product_id': product_id,
# # #             'product_code_from': product_code_from,
# # #             'product_code_to': product_code_to,
# # #         })
        
# # #         if category_id and category_id != []:
# # #             category_id_str = ','.join(map(str, category_id))
# # #         if customer_id and customer_id != []:
# # #             customer_id_str = ','.join(map(str, customer_id))
# # #         if product_id and product_id != []:
# # #             product_id_str = ','.join(map(str, product_id))
# # #         if currency_id and currency_id != []:
# # #             currency_id_str = ','.join(map(str, currency_id))
        
# # #         cr = self._cr
# # #         query = ("""
# # #             SELECT
# # #                 cur.name AS cur_name,
# # #                 cust.x_studio_new_code AS code, 
# # #                 cust.name AS customer_name,
# # #                 prod.default_code AS product_default_code,
# # #                 pt.name ->> 'en_US' AS product_name,
# # #                 uom.name ->> 'en_US' AS unit,
# # #                 SUM(inv_line.quantity) AS quantity,
# # #                 SUM(inv_line.price_unit * inv_line.quantity) AS gross_amount,
# # #                 AVG(inv_line.price_unit) AS value_excl,
# # #                 SUM(inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# # #                 SUM(inv_line.price_total) AS total_amount
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
# # #                 AND pt.name ->> 'en_US' != 'Opening Balance'
# # #         """)

# # #         where_clauses = []

# # #         if currency_id:
# # #             where_clauses.append("cur.id IN (%s)" % currency_id_str)
# # #         if date_from and date_to:
# # #             where_clauses.append("inv.invoice_date BETWEEN '%s' AND '%s'" % (date_from, date_to))
# # #         if customer_id:
# # #             where_clauses.append("cust.id IN (%s)" % customer_id_str)
# # #         if product_id:
# # #             where_clauses.append("pt.id IN (%s)" % product_id_str)
# # #         if product_code_from and product_code_to:
# # #             where_clauses.append("pt.default_code BETWEEN '%s' AND '%s'" % (product_code_from, product_code_to))
# # #         if category_id:
# # #             where_clauses.append("pc.id IN (%s)" % category_id_str)

# # #         if where_clauses:
# # #             query += ' AND ' + ' AND '.join(where_clauses)

# # #         query += """
# # #             GROUP BY cur.name, cust.x_studio_new_code, cust.name, prod.default_code, pt.name, uom.name
# # #             ORDER BY prod.default_code
# # #         """

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
# #     _name = 'report.sales_summary.sales_summary_reports'
# #     _description = 'Sales Summary Report'

# #     @api.model
# #     def _get_report_values(self, docids, data=None):

# #         # raise UserError('this is calling!')
# #         other_details = {}
# #         date_from = data.get('date_from')
# #         date_to = data.get('date_to')
# #         cust_sel = data.get('cust_sel')
# #         prod_sel = data.get('prod_sel')
# #         customer_id = data.get('customer_id')
# #         category_id = data.get('category_id')
# #         currency_id = data.get('currency_id')
# #         product_id = data.get('product_id')
# #         product_code_from = data.get('product_code_from')
# #         product_code_to = data.get('product_code_to')

# #         # raise UserError(f'{product_code_from} {product_code_to}')
# #         other_details.update({
# #             'from_date': date_from,
# #             'to_date': date_to,
# #             'cust_sel': cust_sel,
# #             'prod_sel': prod_sel,
# #             'customer_id': customer_id,
# #             'category_id': category_id,
# #             'currency_id': currency_id,
# #             'product_id': product_id,
# #             'product_code_from': product_code_from,
# #             'product_code_to': product_code_to,
# #         })

# #         # Prepare SQL conditions
# #         where_clauses = []
# #         params = []

# #         if currency_id:
# #             currency_id_str = ','.join(map(str, currency_id))
# #             where_clauses.append("cur.id IN (%s)" % currency_id_str)
        
# #         if date_from and date_to:
# #             where_clauses.append("inv.date BETWEEN %s AND %s")
# #             params.extend([date_from, date_to])
        
# #         if customer_id:
# #             customer_id_str = ','.join(map(str, customer_id))
# #             where_clauses.append("cust.id IN (%s)" % customer_id_str)
        
# #         if product_id:
# #             product_id_str = ','.join(map(str, product_id))
# #             where_clauses.append("pt.id IN (%s)" % product_id_str)
        
# #         if product_code_from and product_code_to:
# #             where_clauses.append("pt.default_code BETWEEN %s AND %s")
# #             params.extend([product_code_from, product_code_to])
        
# #         if category_id:
# #             category_id_str = ','.join(map(str, category_id))
# #             where_clauses.append("pc.id IN (%s)" % category_id_str)

# #         # Base query
# #         query = """
# #             SELECT
# #             cur.name AS cur_name,
# #             cust.x_studio_new_code AS code, 
# #             cust.name AS customer_name,
# #             prod.default_code AS product_default_code,
# #             pt.name ->> 'en_US' AS product_name,
# #             uom.name ->> 'en_US' AS unit,
# #             SUM(inv_line.quantity) AS quantity,
# #             SUM(inv_line.price_unit * inv_line.quantity) AS gross_amount,
# #             SUM(CASE 
# #                     WHEN cur.name = 'USD' THEN inv_line.price_subtotal * inv.currency_rate
# #                     ELSE inv_line.price_subtotal 
# #                 END) AS value_excl,
# #             SUM(inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
# #             SUM(CASE 
# #                     WHEN cur.name = 'USD' THEN inv_line.price_total * inv.currency_rate
# #                     ELSE inv_line.price_total 
# #                 END) AS total_amount

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
# #                 AND pt.name ->> 'en_US' != 'Opening Balance'
# #         """

# #         # Add conditions if available
# #         if where_clauses:
# #             query += ' AND ' + ' AND '.join(where_clauses)

# #         query += """
# #             GROUP BY cur.name, cust.x_studio_new_code, cust.name, prod.default_code, pt.name, uom.name
# #             ORDER BY prod.default_code
# #         """

# #         cr = self._cr
# #         cr.execute(query, params)
# #         result = cr.dictfetchall()


# #         # raise UserError(str(result))

# #         # Calculate totals
# #         totals = {
# #             'quantity': sum(item['quantity'] for item in result),
# #             'gross_amount': sum(item['gross_amount'] for item in result),
# #             'value_excl': sum(item['value_excl'] for item in result),
# #             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
# #             'total_amount': sum(item['total_amount'] for item in result),
# #         }
# #         # raise UserError(str(totals['value_excl']))

# #         result = self.sort_by_customer_name(result)
# #         # raise UserError(str(result))

# #         return {
# #             'data': result,
# #             'totals': totals,
# #             'other': other_details,
# #         }

# #     def sort_by_customer_name(self, records):
# #         return sorted(records, key=lambda x: x['customer_name'])



# from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo import _, api, fields, models
# from datetime import datetime

# # Fetch today's date
# today_date = datetime.today()

# # Format the date
# formatted_date = today_date.strftime("%Y-%m-%d")


# class CustomReport(models.AbstractModel):
#     _name = 'report.sales_summary.sales_summary_reports'
#     _description = 'Sales Summary Report'

#     @api.model
#     def _get_report_values(self, docids, data=None):

#         other_details = {}
#         date_from = data.get('date_from')
#         date_to = data.get('date_to')
#         cust_sel = data.get('cust_sel')
#         prod_sel = data.get('prod_sel')
#         customer_id = data.get('customer_id')
#         category_id = data.get('category_id')
#         currency_id = data.get('currency_id')
#         product_id = data.get('product_id')
#         product_code_from = data.get('product_code_from')
#         product_code_to = data.get('product_code_to')
#         customer_code_from = data.get('customer_code_from')
#         customer_code_to = data.get('customer_code_to')

#         other_details.update({
#             'from_date': date_from,
#             'to_date': date_to,
#             'cust_sel': cust_sel,
#             'prod_sel': prod_sel,
#             'customer_id': customer_id,
#             'category_id': category_id,
#             'currency_id': currency_id,
#             'product_id': product_id,
#             'product_code_from': product_code_from,
#             'product_code_to': product_code_to,
#             'customer_code_from': customer_code_from,
#             'customer_code_to': customer_code_to,
#         })

#         # Prepare SQL conditions
#         where_clauses = []
#         params = []

#         if currency_id:
#             currency_id_str = ','.join(map(str, currency_id))
#             where_clauses.append("cur.id IN (%s)" % currency_id_str)
        
#         if date_from and date_to:
#             where_clauses.append("inv.date BETWEEN %s AND %s")
#             params.extend([date_from, date_to])
        
#         if customer_id:
#             customer_id_str = ','.join(map(str, customer_id))
#             where_clauses.append("cust.id IN (%s)" % customer_id_str)
        
#         if product_id:
#             product_id_str = ','.join(map(str, product_id))
#             where_clauses.append("pt.id IN (%s)" % product_id_str)
        
#         if product_code_from and product_code_to:
#             where_clauses.append("pt.default_code BETWEEN %s AND %s")
#             params.extend([product_code_from, product_code_to])

#         # Adding the condition for customer code range
#         if customer_code_from and customer_code_to:
#             where_clauses.append("cust.x_studio_new_code BETWEEN %s AND %s")
#             params.extend([customer_code_from, customer_code_to])
        
#         if category_id:
#             category_id_str = ','.join(map(str, category_id))
#             where_clauses.append("pc.id IN (%s)" % category_id_str)

#         # Base query
#         query = """
#             SELECT
#             cur.name AS cur_name,
#             cust.x_studio_new_code AS code, 
#             cust.name AS customer_name,
#             prod.default_code AS product_default_code,
#             pt.name ->> 'en_US' AS product_name,
#             uom.name ->> 'en_US' AS unit,
#             SUM(inv_line.quantity) AS quantity,
#             SUM(inv_line.price_unit * inv_line.quantity) AS gross_amount,
#             SUM(CASE 
#                     WHEN cur.name = 'USD' THEN inv_line.price_subtotal * inv.currency_rate
#                     ELSE inv_line.price_subtotal 
#                 END) AS value_excl,
#             SUM(inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
#             SUM(CASE 
#                     WHEN cur.name = 'USD' THEN inv_line.price_total * inv.currency_rate
#                     ELSE inv_line.price_total 
#                 END) AS total_amount

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

#         # Add conditions if available
#         if where_clauses:
#             query += ' AND ' + ' AND '.join(where_clauses)

#         query += """
#             GROUP BY cur.name, cust.x_studio_new_code, cust.name, prod.default_code, pt.name, uom.name
#             ORDER BY prod.default_code
#         """

#         cr = self._cr
#         cr.execute(query, params)
#         result = cr.dictfetchall()

#         # Calculate totals
#         totals = {
#             'quantity': sum(item['quantity'] for item in result),
#             'gross_amount': sum(item['gross_amount'] for item in result),
#             'value_excl': sum(item['value_excl'] for item in result),
#             'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
#             'total_amount': sum(item['total_amount'] for item in result),
#         }

#         result = self.sort_by_customer_name(result)

#         # raise UserError(str(result))

#         return {
#             'data': result,
#             'totals': totals,
#             'other': other_details,
#         }

#     def sort_by_customer_name(self, records):
#         return sorted(records, key=lambda x: x['code'])





from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import _, api, fields, models
from datetime import datetime

# Fetch today's date
today_date = datetime.today()

# Format the date
formatted_date = today_date.strftime("%Y-%m-%d")


class CustomReport(models.AbstractModel):
    _name = 'report.sales_summary.sales_summary_reports'
    _description = 'Sales Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):

        other_details = {}
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        cust_sel = data.get('cust_sel')
        prod_sel = data.get('prod_sel')
        customer_id = data.get('customer_id')
        category_id = data.get('category_id')
        currency_id = data.get('currency_id')
        product_id = data.get('product_id')
        product_code_from = data.get('product_code_from')
        product_code_to = data.get('product_code_to')
        customer_code_from = data.get('customer_code_from')
        customer_code_to = data.get('customer_code_to')
        group_by = data.get('group_by', 'product')  # Default to 'product' if not specified

        other_details.update({
            'from_date': date_from,
            'to_date': date_to,
            'cust_sel': cust_sel,
            'prod_sel': prod_sel,
            'customer_id': customer_id,
            'category_id': category_id,
            'currency_id': currency_id,
            'product_id': product_id,
            'product_code_from': product_code_from,
            'product_code_to': product_code_to,
            'customer_code_from': customer_code_from,
            'customer_code_to': customer_code_to,
            'group_by': group_by,
        })

        # Prepare SQL conditions
        where_clauses = []
        params = []

        if currency_id:
            currency_id_str = ','.join(map(str, currency_id))
            where_clauses.append("cur.id IN (%s)" % currency_id_str)
        
        if date_from and date_to:
            where_clauses.append("inv.date BETWEEN %s AND %s")
            params.extend([date_from, date_to])
        
        if customer_id:
            customer_id_str = ','.join(map(str, customer_id))
            where_clauses.append("cust.id IN (%s)" % customer_id_str)
        
        if product_id:
            product_id_str = ','.join(map(str, product_id))
            where_clauses.append("pt.id IN (%s)" % product_id_str)
        
        if product_code_from and product_code_to:
            where_clauses.append("pt.default_code BETWEEN %s AND %s")
            params.extend([product_code_from, product_code_to])

        # Adding the condition for customer code range
        if customer_code_from and customer_code_to:
            where_clauses.append("cust.x_studio_new_code BETWEEN %s AND %s")
            params.extend([customer_code_from, customer_code_to])
        
        if category_id:
            category_id_str = ','.join(map(str, category_id))
            where_clauses.append("pc.id IN (%s)" % category_id_str)

        # Base query
        query = """
            SELECT
            cur.name AS cur_name,
            cust.x_studio_new_code AS code, 
            cust.name AS customer_name,
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

        # Add conditions if available
        if where_clauses:
            query += ' AND ' + ' AND '.join(where_clauses)

        query += """
            GROUP BY cur.name, cust.x_studio_new_code, cust.name, prod.default_code, pt.name, uom.name
            ORDER BY prod.default_code
        """

        cr = self._cr
        cr.execute(query, params)
        result = cr.dictfetchall()

        # Calculate totals
        totals = {
            'quantity': sum(item['quantity'] for item in result),
            'gross_amount': sum(item['gross_amount'] for item in result),
            'value_excl': sum(item['value_excl'] for item in result),
            'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
            'total_amount': sum(item['total_amount'] for item in result),
        }

        if group_by == 'customer':
            result = self.sort_by_customer_name(result)
        elif group_by == 'product':
            result = self.sort_by_product_name(result)

        other_details['sorted_by'] = group_by


        # raise UserError(str(other_details))
        # raise UserError(str(result))


        return {
            'data': result,
            'totals': totals,
            'other': other_details,
        }

    def sort_by_customer_name(self, records):
        return sorted(records, key=lambda x: x['code'])

    def sort_by_product_name(self, records):
        return sorted(records, key=lambda x: x['product_default_code'])

