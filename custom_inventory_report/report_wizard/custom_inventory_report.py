from odoo import fields, models, api, _
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from . import xlsxwriter
from . import excel_formatter
import base64
from io import BytesIO
import json
from odoo.exceptions import UserError
import io
from datetime import datetime , timedelta
from dateutil.relativedelta import relativedelta
try:
    import xlwt
except ImportError:
    xlwt = None
import pytz

class CustomInventoryReport(models.TransientModel):
    _name = 'custom.inventory.report'

    report_type = fields.Selection([('closing_balance',' Closing Balances')],string="Report",default="closing_balance")

    # products section
    product_filter = fields.Selection([('all','All'),('single','Single'),('range','Range')],string="Product",default="all")
    from_product =  fields.Many2one('product.product',string="From")
    to_product = fields.Many2one('product.product',string="To")
    product_id = fields.Many2one('product.product',string="Product")
    product_ids = fields.Many2many("product.product", string="Products")

    # Dates Section
    date_filter =  fields.Selection([('all','All'),('range','Range')],string="Date",default="all")
   
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")

    #Location Section
    location_filter = fields.Selection([('all','All'),('single','Single')],string="Location",default="all")
    location = fields.Many2many('stock.location',string="Location")  

    stock_file_data = fields.Binary('Inventory Age Report File')
    company_ids = fields.Many2many("res.company", string="Companies")

    # Category Filter
    category_filter = fields.Selection([('all','All'),('single','Single')],string="Category",default="all")
    product_category_ids = fields.Many2many("product.category", string="Product Categories")

    # With amount without amount
    with_amount = fields.Selection([('amount_true','With Amount'),('amount_false','Without Amount')],string="Select Type",default="amount_true")
    with_qty =fields.Selection([('qty_true','Including Zero Quantity'),('qty_false','Without Zero Qty')],string="Select Quantity",default="qty_true")

    # def Valuation_values_gen(self, move):
    #     if self.location_filter == 'all':
    #         valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
    #         valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id  or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) )
    #     else:
    #         valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
    #         valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.move_id.id  or (not x.stock_move_id and move.move_id.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.move_id.id or move.move_id.reference in x.stock_valuation_layer_id.reference)) )
    #     Valuation_values = valuations.mapped("value")

    #     return sum(Valuation_values)

    def Valuation_values_gen(self, move):
        if self.location_filter == 'all':
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id)])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id and ((x.account_move_id and x.account_move_id.date <= self.to_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) )
        else:
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id)])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.move_id.id and (x.account_move_id and x.account_move_id.date <= self.to_date or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.move_id.id or move.reference in x.stock_valuation_layer_id.reference)) )
        Valuation_values = valuations.mapped("value")
        return sum(Valuation_values)

    def product_search_by_range(self):
        for rec in self:
            products_in_order = []
            if rec.product_filter == 'range' and rec.from_product and rec.to_product:
                from_product = int(''.join((rec.from_product.default_code).split('-')))
                to_product = int(''.join((rec.to_product.default_code).split('-')))
                
                if from_product < to_product:
                    start = from_product
                    end = to_product
                elif  from_product > to_product:
                    start = to_product
                    end = from_product
                    
                all_products= rec.env['product.product'].search([])
                products_in_order = all_products.filtered(lambda x: x.default_code and int(''.join((x.default_code).split('-'))) >= start and int(''.join((x.default_code).split('-'))) <= end)
            else:
                all_products= rec.env['product.product'].search([])
                products_in_order = all_products.filtered(lambda x: x.default_code and int(''.join((x.default_code).split('-'))[0]) >=1  and int(''.join((x.default_code).split('-'))[0]) <= 3)
            return products_in_order

    def product_filteration(self):
        for rec in self:
            domain = [('product_id.detailed_type','=','product')]
            if rec.product_filter == 'all':
                products = rec.product_search_by_range()
                domain += [('product_id','in',products.ids)]
            elif rec.product_filter == 'single' and rec.product_ids:
                domain += [('product_id','in',rec.product_ids.ids)]
            elif rec.product_filter == 'range':
                products = rec.product_search_by_range()
                domain += [('product_id','in',products.ids)]
            if rec.location_filter == 'single':
                domain += [('move_id', '!=', False)]
                product_move =  rec.env['stock.move.line'].search(domain)
                product_move = product_move.filtered(lambda x:x.state == 'done' or x.move_id.state == 'done')
            elif rec.location_filter == 'all':
                product_move =  rec.env['stock.move'].search(domain)
                product_move= product_move.filtered(lambda x:x.state == 'done')
            if rec.category_filter == 'single' and rec.product_category_ids:
                product_move = product_move.filtered(lambda x : x.product_id.categ_id in rec.product_category_ids)
            return product_move

    def _aggregate_products_with_qty(self,moves):
        result = {}
        counter = 0
        standard_price = {}
        for move in moves:
            counter += 1
            product_name = move.product_id.name
            
            if move.product_id.detailed_type != 'consu':
                rate_value = self.Valuation_values_gen(move)
                qty = abs(move.qty_done)
            else:
                rate_value = 0
                qty = abs(move.qty_done)
            if product_name not in standard_price.keys():
                standard_price[product_name] = move.product_id.standard_price
            if product_name not in result.keys():
                result[product_name] = {
                    'id':move.product_id.id,
                    'name': move.product_id.name,
                    'product_code': move.product_id.default_code,
                    'product_type': move.product_id.type,
                    'unit':move.product_id.uom_name,
                    'qty':qty or 0.0,
                    'ref_dict': {move.reference: [move.qty_done]},
                    'rate': rate_value or 0.0,
                    'activity_in':0,
                    'activity_out':0,
                    'ref':[move.reference],
                    'moves':[move.move_id.id],
                    'opening':0,
                    'standard_price_product' : move.product_id.standard_price
                }
                continue
            result[product_name]['qty'] = result[product_name]['qty'] + qty
            if move.reference not in result[product_name]['ref']:
                result[product_name]['ref'].append(move.reference)
                result[product_name]['ref_dict'][move.reference] = [move.qty_done]
                
            elif move.reference in result[product_name]['ref'] and qty == result[product_name]['qty']:
                continue
            else:
                if qty not in result[product_name]['ref_dict'].get(move.reference):
                    result[product_name]['ref_dict'][move.reference].append(qty)  
            if move.move_id.id not in result[product_name]['moves']:
                result[product_name]['rate'] = result[product_name].get('rate') + rate_value
                result[product_name]['moves'].append(move.move_id.id)        
        return result      


    def _aggregate_products_with_qty_all_location(self,moves):
        result = {}
        counter = 0
        standard_price = {}
        for move in moves:
            counter += 1
            product_name = move.product_id.name

            if move.product_id.detailed_type != 'consu':
                rate_value = self.Valuation_values_gen(move)

                qty = abs(move.product_uom_qty)
            else:
                rate_value = 0
                qty = abs(move.product_uom_qty)

            if product_name not in standard_price.keys():
                standard_price[product_name] = move.product_id.standard_price
            if product_name not in result.keys():
                result[product_name] = {
                    'id':move.product_id.id,
                    'name': move.product_id.name,
                    'product_code': move.product_id.default_code,
                    'product_type': move.product_id.type,
                    'unit':move.product_id.uom_name,
                    'qty':qty or 0.0,
                    'ref_dict': {move.reference: [move.product_uom_qty]},
                    'rate':rate_value or 0.0,
                    'activity_in':0,
                    'activity_out':0,
                    'ref':[move.reference],
                    'opening':0,
                    'standard_price_product' : move.product_id.standard_price
                }
                continue
            result[product_name]['qty'] = result[product_name]['qty'] + qty
            result[product_name]['rate'] = result[product_name].get('rate') + rate_value

            if move.reference not in result[product_name]['ref']:
                result[product_name]['ref'].append(move.reference)
                result[product_name]['ref_dict'][move.reference] = [move.product_uom_qty]
            elif move.reference in result[product_name]['ref'] and qty == result[product_name]['qty']:
                continue
            else:
                if qty not in result[product_name]['ref_dict'].get(move.reference):
                    result[product_name]['ref_dict'][move.reference].append(qty)        
        
        return result     


    def _prepare_report_data_for_closing_balance(self):
        for rec in self:
            if rec.date_filter == 'all':
                rec.to_date = datetime.now().date()
            moves = rec.product_filteration()
            if rec.date_filter == 'range' and rec.to_date >= rec.from_date:
                moves = moves.filtered(lambda x: x.move_date <= self._get_timezone_converted_date(rec.to_date, date_type='end'))

            if rec.location_filter == 'single':
                in_moves = moves.filtered(lambda x: x.location_dest_id in rec.location)
                out_moves = moves.filtered(lambda x: x.location_id in rec.location)
                in_products = rec._aggregate_products_with_qty(in_moves)
                out_products = rec._aggregate_products_with_qty(out_moves)
            elif rec.location_filter == 'all':
                in_moves = moves.filtered(lambda move: move.location_usage not in ("internal", "transit") and
                                                    move.location_dest_usage in ("internal", "transit"))
                out_moves = moves.filtered(lambda move: (
                                            (move.location_usage in ("internal", "transit") and 
                                            move.location_dest_usage not in ("internal", "transit"))
                                            or 
                                            ('RTN-VEN' in (move.reference or ''))
                                        ))

                in_products = rec._aggregate_products_with_qty_all_location(in_moves)
                out_products = rec._aggregate_products_with_qty_all_location(out_moves)
            final_products = in_products.copy()
            to_be_deleted = []
            

            for product_name, product_details in out_products.items():
                if product_name not in final_products:
                    final_products[product_name] = product_details
                    continue
                final_products[product_name]['qty'] = round(final_products[product_name].get('qty', 0) - abs(product_details.get('qty', 0)), 4)
                final_products[product_name]['rate'] = round(final_products[product_name].get('rate', 0) - abs(product_details.get('rate', 0)), 4)

            for product_name, product_details in final_products.items():
                if rec.with_qty == 'qty_false' and float(product_details.get('qty')) <= 0:
                    to_be_deleted.append(product_name)

            for pr_name in to_be_deleted:
                del final_products[pr_name]

            sorted_products = sorted(
                filter(lambda x: isinstance(x['product_code'], str), final_products.values()),
                key=lambda x: x['product_code']
            )
            final_products = {product['name']: product for product in sorted_products}

            if self.location_filter == 'single':
                for p_name, data in final_products.items():
                    data['rate'] = round(data['qty'] * data['standard_price_product'], 4)
            return final_products

            
    def _prepare_report_data(self):
        records = {}
        # Build data to pass to the report
        match self.report_type:
            case 'all':
                if self.date_filter != 'range':
                    raise UserError("Select Date Range")
                return 1
                xml_id = "custom_inventory_report.report_inventory_report_all_btn"
                # records = self._prepare_report_data_for_all_balance()
            case 'opening_balance':
                xml_id = "custom_inventory_report.report_inventory_report_opening_balance_btn"
            case 'activity_in':
                xml_id = "custom_inventory_report.report_inventory_report_activity_in_btn"
            case 'activity_out':
                xml_id = "custom_inventory_report.report_inventory_report_activity_out_btn"
            case 'closing_balance':
                xml_id = "custom_inventory_report.report_inventory_report_closing_balance_btn"
                records = self._prepare_report_data_for_closing_balance()
            case _:
                xml_id = "custom_inventory_report.report_inventory_report_all_btn"

        data = {
            'active_model': 'stock.move',
            'layout_wizard': self.id,
            'context':self.env.context,
            'products':list(records.values()),
            'with_amount':self.with_amount,
        }
        
        if self.date_filter == 'range':
            data['from_date'] = self.from_date.strftime('%d-%b-%Y')
            data['to_date']   = self.to_date.strftime('%d-%b-%Y')
        if self.product_filter == 'range':
            data['from_product'] = self.from_product.display_name
            data['to_product'] = self.to_product.display_name
        data['at_locations'] = ''
        if self.location_filter == 'single':
            data['at_locations']= f"At Locations "
            for loc in self.location:
                data['at_locations'] += str(loc.name) 
        return xml_id, data
    
    def _get_timezone_converted_date(self, conv_date, date_type='start'):
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
        if date_type == 'start':
            return user_tz.localize(datetime.combine(conv_date, datetime.min.time())).astimezone(pytz.UTC).replace(tzinfo=None)
        else:
            return user_tz.localize(datetime.combine(conv_date, datetime.max.time())).astimezone(pytz.UTC).replace(tzinfo=None)
        

    def downlaod_report_pdf(self):
        self.ensure_one()
        xml_id, data = self._prepare_report_data()
        if not xml_id:
            raise UserError(_('Unable to find report template for %s format', self.print_format))
        if 'context' in data and isinstance(data['context'], dict):
            data['context'] = json.dumps(data['context'])
        report_action = self.env.ref(xml_id).report_action(None,data=data,config=False)
        report_action.update({'close_on_report_download': True})
        return report_action
    
    
    def action_print_excel_report(self):
        xml_id, datas = self._prepare_report_data()
        
        excel_encode = io.BytesIO()
        filename = "Inventory Closing Report - " + str(datetime.now().strftime("%d-%m-%Y")) + ".xlsx"
        workbook = xlsxwriter.Workbook(excel_encode)
        sheet = workbook.add_worksheet('Inventory Closing reports')
        header = workbook.add_format({'bold': True, 'align': 'center', 'size': 13, 'bg_color': '#d9d4d4'})
        header.set_border()
        normal_text = workbook.add_format({'align': 'left', 'size': 12})
        normal_amount = workbook.add_format({'align': 'right', 'size': 12})

        summary_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 12, 'bg_color': '#d9d4d4'})

        
        big_heading = "Biafo Industries Limited"
        sub_heading = "Inventory List (Closing)"
        sub_heading_1 = f"""({"From: "+ datas.get('from_date') if datas.get('from_date') else ''}{", To: "+ datas.get('to_date') if datas.get('to_date') else ''}{',' + str(datas.get('at_locations')) if datas.get('at_locations',False) else '' } Rupees, Stock Items)"""

        sheet.merge_range(0, 0, 1, 6, big_heading, summary_format)
        sheet.merge_range(2, 0, 2, 6, sub_heading, summary_format)
        sheet.merge_range(3, 0, 3, 6, sub_heading_1, summary_format)

        for i in range(0, 20):
            sheet.set_column(0, i, 22)        
        sheet.write(4, 0, 'Product Code', header)
        sheet.write(4, 1, 'Description', header)
        sheet.write(4, 2, 'Units', header)
        sheet.write(4, 3, 'Quantity', header)
        col = 4
        if self.with_amount == 'amount_true':
            sheet.write(4, col, 'Rate', header)
            sheet.write(4, col + 1, 'Amount', header)
        inv_row = 5
        count = 1
        total_amount = 0
        for product in datas.get('products',[]):
            if self.with_qty == 'qty_false' and product.get('qty') == 0:
                continue
            quantity = round(product.get('qty'),4)
            rate = round(product.get('rate'),4)
            if self.with_qty == 'qty_false' and quantity <= 0:
                continue
            sheet.write(inv_row, 0, product['product_code'], normal_text)
            sheet.write(inv_row, 1, product['name'], normal_text)
            sheet.write(inv_row, 2, product['unit'], normal_text)
            sheet.write(inv_row, 3, '{:,.4f}'.format(quantity), normal_amount)
            col = 4
            if self.with_amount == 'amount_true':
                sheet.write(inv_row, col, '{:,.4f}'.format(abs(rate/quantity) if product['qty'] != 0 else 0), normal_amount)
                sheet.write(inv_row, col + 1, '{:,.4f}'.format(float(rate) if product['qty'] != 0 else 0), normal_amount)
            
            total_amount += product.get('rate',0) if product['qty'] != 0 else 0
            inv_row += 1
            count += 1

        # Write the summary row
        if self.with_amount == 'amount_true':
            summary_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 11, 'bg_color': '#d9d4d4'})
            sheet.merge_range(inv_row, 0, inv_row, 4, 'TOTAL', summary_format)
            sheet.write(inv_row, 5, '{:,.4f}'.format(round(total_amount,4)), normal_amount)

        workbook.close()
        excel_data = excel_encode.getvalue()
        encoded_excel_data = base64.b64encode(excel_data).decode()

        export_id = self.env['customer.invoices.report.excel'].create({'excel_file': encoded_excel_data, 'file_name': filename})
        res = {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'customer.invoices.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
        return res


class customer_invoices_report_excel(models.TransientModel):
    _name = "customer.invoices.report.excel"
    _description = "Customer Invoices Report Excel"
    
    excel_file = fields.Binary('Excel file')
    file_name = fields.Char('Excel File', size=64)