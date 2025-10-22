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
        # invocie_type = data.get('invocie_type')
        # all_products = data.get('all_products')



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
                # 'invocie_type' : invocie_type,
                # 'all_products': all_products

            })
        

        
        if category_id:
            if category_id != []:
                category_id_str = ','.join(map(str,category_id))

        if customer_id:
            if customer_id != []:
                customer_id_str = ','.join(map(str,customer_id))

        if product_id:
            if product_id != []:
                product_id_str = ','.join(map(str,product_id))

        if currency_id:
            if currency_id != []:
                currency_id_str = ','.join(map(str,currency_id))

        
        
        cr = self._cr
        query = ("""
            SELECT
                distinct  
                cur.name as cur_name,
                cust.x_studio_new_code as code, 
                inv.id AS invoice_id,
                cust.name AS customer_name,
                prod.default_code AS product_default_code,
                pt.name ->> 'en_US' AS product_name,
                inv_line.name AS product_description,
                uom.name ->> 'en_US' AS unit,
                inv_line.quantity AS quantity,
                (inv_line.price_unit * inv_line.quantity) AS gross_amount,
                inv_line.price_unit AS value_excl,
                (inv_line.price_total - inv_line.price_subtotal) AS sales_tax_amount,
                inv_line.price_total AS total_amount
            FROM 
                account_move_line inv_line
            INNER JOIN 
                account_move inv ON inv_line.move_id = inv.id
            INNER JOIN 
                product_product prod ON inv_line.product_id = prod.id
            INNER JOIN 
                product_template pt on pt.id  =  prod.product_tmpl_id
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
        """) 





        where_clauses = []

        # if invocie_type == 'draft' or invocie_type == 'posted' or invocie_type == 'cancel':
        #     where_clauses.append("AND inv.state = %s" % invocie_type)
            



        if currency_id:
            where_clauses.append("AND cur.id in (%s)" % currency_id_str)


        if date_from:
            date_to = formatted_date
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s'" % (date_from, date_to))

        if date_from and date_to:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s'" % (date_from, date_to))
        if date_from and date_to and currency_id:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))


        if date_from and date_to and currency_id and cust_sel == 'customer wise' and prod_sel == 'product wise' and customer_id:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))
            where_clauses.append("AND cust.id in (%s)"  % customer_id_str)
            where_clauses.append('AND pt.id in (%s)'  % product_id_str)
        
        if date_from and date_to and currency_id and cust_sel == 'all customers' and prod_sel == 'product wise' and product_id:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))
            where_clauses.append('AND pt.id in (%s)'  % product_id_str)
        
        if date_from and date_to and currency_id and cust_sel == 'customer wise' and prod_sel == 'range wise' and customer_id and product_id:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))
            where_clauses.append("AND cust.id in (%s)"  % customer_id_str)
            where_clauses.append("AND pt.default_code between '%s' AND '%s'"  % (product_code_from, product_code_to))
            
        
        if date_from and date_to and currency_id and cust_sel == 'all customers' and prod_sel == 'range wise':
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))
            where_clauses.append("AND pt.default_code between '%s' AND '%s'"  % (product_code_from, product_code_to))
        

        if date_from and date_to and currency_id and cust_sel == 'customer wise' and prod_sel == 'category wise' and category_id and customer_id:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id = %s" % (date_from, date_to, currency_id_str))
            where_clauses.append("AND cust.id in (%s)"  % customer_id_str)
            where_clauses.append("AND pc.id in (%s)"  % category_id_str)
            
        
        if date_from and date_to and currency_id and cust_sel == 'all customers' and prod_sel == 'category wise' and category_id:
            where_clauses.append("AND inv.invoice_date between '%s' AND '%s' AND cur.id in (%s)" % (date_from, date_to, currency_id_str))
            where_clauses.append("AND pc.id in (%s)"  % category_id_str)
        

        # query += 'WHERE '
        query += ' '.join(where_clauses)
        query += 'order by cust.name'
        
        
        cr.execute(query)
        result = cr.dictfetchall()

        totals = {
            'quantity': sum(item['quantity'] for item in result),
            'gross_amount': sum(item['gross_amount'] for item in result),
            'value_excl': sum(item['value_excl'] for item in result),
            'sales_tax_amount': sum(item['sales_tax_amount'] for item in result),
            'total_amount': sum(item['total_amount'] for item in result),
        }
        # raise UserError(str(result))

        return {
            'data': result,
            'totals': totals,
            'other': other_details,
        }
    

    # 



# <!-- <?xml version="1.0" encoding="utf-8"?>
# <odoo>
#     <template id="sales_summary_reports">
#             <t t-call="web.basic_layout">
#                 <div class="header">
#                     <div class="row">
#                         <div class="col-12 text-left">
#                             <h4>Biafo Industries Limited</h4>
#                             <h4>Sales Summary - Customer Wise / Product wise</h4>
#                         </div>
#                     </div>
#                 </div>
#                 <br/>                
#                 <div class="page">
                    
#                     <div class="row mt-5 mb-3">
#                         <div class="col-12">

#                             <table style="border-collapse:collapse ;" class="table-borderless">
#                                 <thead>
#                                     <tr>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:120px">
#                                             <b>Product</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:200px">
#                                             <b>Description</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:80px">
#                                             <b>Unit</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:80px">
#                                             <b>Quantity</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:170px">
#                                             <b>Gross Amount</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:250px">
#                                             <b>Sales Excluding Sales Tax And Excise Duty</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:150px">
#                                             <b>Sales Tax Amount</b>
#                                         </th>
#                                         <th style="text-align:center;border-bottom:1px solid black;padding:10px;width:150px">
#                                             <b>Total Amount</b>
#                                         </th>
                                        
#                                     </tr>
#                                 </thead>


#                                 <tbody>
#                                     <t t-set="customer_name" t-value="None" />
#                                     <t t-set="customer_code" t-value="None" />

#                                     <!-- Initialize variables to store customer-wise totals -->
#                                     <t t-set="customer_quantity_total" t-value="0.0" />
#                                     <t t-set="customer_gross_amount_total" t-value="0.0" />
#                                     <t t-set="customer_value_excl_total" t-value="0.0" />
#                                     <t t-set="customer_sales_tax_total" t-value="0.0" />
#                                     <t t-set="customer_total_amount_total" t-value="0.0" />

#                                     <!-- Initialize variable to track the first customer -->
#                                     <t t-set="is_first_customer" t-value="True" /> <!-- chatgpt changed this -->

#                                     <t t-foreach="data" t-as="value">
#                                         <!-- Check if the customer name has changed -->
#                                         <t t-if="customer_name != value['customer_name']">
#                                             <!-- Display totals for the previous customer, if any -->
#                                             <t t-if="customer_name != 'None' and not is_first_customer"> <!-- chatgpt changed this -->
#                                                 <tr>
#                                                     <td colspan="3" style="text-align:right; font-weight:bold; padding:4px;">
#                                                         Subtotal 
#                                                         <!-- <t t-esc="customer_name" /> -->
#                                                     </td>
#                                                     <td style="text-align:center; font-weight:bold; padding:4px;">
#                                                         <span t-esc="customer_quantity_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                                     </td>
#                                                     <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                         <span t-esc="customer_gross_amount_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                                     </td>
#                                                     <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                         <span t-esc="customer_value_excl_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                                     </td>
#                                                     <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                         <span t-esc="customer_sales_tax_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                                     </td>
#                                                     <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                         <span t-esc="customer_total_amount_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                                     </td>
#                                                 </tr>

#                                                 <!-- Reset customer totals -->
#                                                 <t t-set="customer_quantity_total" t-value="0.0" />
#                                                 <t t-set="customer_gross_amount_total" t-value="0.0" />
#                                                 <t t-set="customer_value_excl_total" t-value="0.0" />
#                                                 <t t-set="customer_sales_tax_total" t-value="0.0" />
#                                                 <t t-set="customer_total_amount_total" t-value="0.0" />
#                                             </t>

#                                             <!-- Update customer name and code -->
#                                             <t t-set="customer_name" t-value="value['customer_name']" />
#                                             <t t-set="customer_code" t-value="value['code']" />
#                                             <t t-set="is_first_customer" t-value="False" /> <!-- chatgpt changed this -->
#                                             <tr>
#                                                 <td style="text-align:center; padding:4px;" colspan="1">
#                                                     <h5><t t-esc="customer_code" /></h5>
#                                                 </td>
#                                                 <td style="text-align:center; padding:4px;" colspan="1">
#                                                     <h5><t t-esc="customer_name" /></h5>
#                                                 </td>
#                                                 <td colspan="6"></td>
#                                             </tr>
#                                         </t>

#                                         <!-- Update customer totals -->
#                                         <t t-set="customer_quantity_total" t-value="customer_quantity_total + value['quantity']" />
#                                         <t t-set="customer_gross_amount_total" t-value="customer_gross_amount_total + value['gross_amount']" />
#                                         <t t-set="customer_value_excl_total" t-value="customer_value_excl_total + value['value_excl']" />
#                                         <t t-set="customer_sales_tax_total" t-value="customer_sales_tax_total + value['sales_tax_amount']" />
#                                         <t t-set="customer_total_amount_total" t-value="customer_total_amount_total + value['total_amount']" />

#                                         <tr>
#                                             <td style="text-align:center; padding:4px;">
#                                                 <span>
#                                                     <t t-esc="value['product_default_code']"/>
#                                                 </span>
#                                             </td>
#                                             <td style="text-align:center; padding:4px;">
#                                                 <span t-esc="value['product_name']"/>
#                                             </td>
#                                             <td style="text-align:center; padding:4px;">
#                                                 <span t-esc="value['unit']"/>
#                                             </td>
#                                             <td style="text-align:center; padding:4px;">
#                                                 <span t-esc="value['quantity']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; padding:4px;">
#                                                 <span t-esc="value['gross_amount']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; padding:4px;">
#                                                 <span t-esc="value['value_excl']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; padding:4px;">
#                                                 <span t-esc="value['sales_tax_amount']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; padding:4px;">
#                                                 <span t-esc="value['total_amount']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                         </tr>
#                                     </t>

#                                     <!-- Display totals for the last customer -->
#                                     <t t-if="customer_name != 'None'">
#                                         <tr>
#                                             <td colspan="3" style="text-align:right; font-weight:bold; padding:4px;">
#                                                 Subtotal 
#                                                 <!-- <t t-esc="customer_name" /> -->
#                                             </td>
#                                             <td style="text-align:center; font-weight:bold; padding:4px;">
#                                                 <span t-esc="customer_quantity_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                 <span t-esc="customer_gross_amount_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                 <span t-esc="customer_value_excl_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                 <span t-esc="customer_sales_tax_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                             <td style="text-align:right; font-weight:bold; padding:4px;">
#                                                 <span t-esc="customer_total_amount_total" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                             </td>
#                                         </tr>
#                                     </t>

#                                     <tr>
#                                         <td colspan="3" style="text-align:right; font-weight:bold; padding:4px;">
#                                             Total 
#                                             <!-- <t t-esc="customer_name" /> -->
#                                         </td>
#                                         <td style="text-align:center; font-weight:bold; padding:4px;">
#                                             <span t-esc="totals['quantity']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                         </td>
#                                         <td style="text-align:right; font-weight:bold; padding:4px;">
#                                             <span t-esc="totals['gross_amount']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                         </td>
#                                         <td style="text-align:right; font-weight:bold; padding:4px;">
#                                             <span t-esc="totals['value_excl']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                         </td>
#                                         <td style="text-align:right; font-weight:bold; padding:4px;">
#                                             <span t-esc="totals['sales_tax_amount']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                         </td>
#                                         <td style="text-align:right; font-weight:bold; padding:4px;">
#                                             <span t-esc="totals['total_amount']" t-options='{"widget": "float", "precision": 2, "thousands_sep": ","}'/>
#                                         </td>
#                                     </tr>
#                                 </tbody>



                                

                                
                                
#                             </table>
#                         </div>
#                     </div>
#                 </div>
#             </t>
        

#     </template>
# </odoo> -->


    # 