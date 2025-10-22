from odoo import models, fields, api,_
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

class StockStatusInventoryReport(models.TransientModel):
    _name = 'stock.status.inventory.report.wizard'
    _description = 'Stock Status Inventory Report Wizard'

    report_type = fields.Selection([('all','All'),('closing_balance',' Closing Balances')],string="Report",default="all")
    # products section
    product_filter = fields.Selection([('all','All'),('single','Single'),('range','Range')],string="Product",default="all")
    from_product =  fields.Many2one('product.product',string="From")
    to_product = fields.Many2one('product.product',string="To")
    product_id = fields.Many2one('product.product',string="Product")
    product_ids = fields.Many2many("product.product", string="Products")
    # Dates Section
    date_filter =  fields.Selection([('all','All'),('range','Range')],string="Date",default="range")
    # from_date = fields.Datetime(string="From")
    # to_date = fields.Datetime(string="To")
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
    render_type = fields.Selection([('qty','Quantity'),('amount','Amount'),('both','Both')],string="Select Type",default="both")
    # with_qty =fields.Selection([('qty_true','Including Zero Quantity'),('qty_false','Without Zero Qty')],string="Select Quantity",default="qty_true")


    def product_search_by_range(self):
        for rec in self:
            products_in_order = []
            if rec.from_product and rec.to_product:
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
                    
            return products_in_order
    
    def filteration(self):
        domain = [('product_id.detailed_type','=','product')]    
        if self.product_filter == 'single' and self.product_ids:
            domain += [('product_id','in',self.product_ids.ids)]
        elif self.product_filter == 'range':
            products = self.product_search_by_range()
            domain += [('product_id','in',products.ids)]
        if self.location_filter == 'single':
            domain += [('move_id', '!=', False)]
            stock_moves =  self.env['stock.move.line'].search(domain)
            stock_moves = stock_moves.filtered(lambda x:x.state == 'done' or x.move_id.state == 'done')
        elif self.location_filter == 'all':
            domain += [('state', '=', 'done')]
            stock_moves =  self.env['stock.move'].search(domain)
            
        if self.category_filter == 'single' and self.product_category_ids:
            stock_moves = stock_moves.filtered(lambda x : x.product_id.categ_id in self.product_category_ids)
        # if self.location_filter == 'single' and self.location:
        #     stock_moves = stock_moves.filtered(lambda x: x.location_id in self.location or x.location_dest_id in self.location)
        return stock_moves

    def Valuation_values_gen(self, move):
        if self.location_filter == 'all':
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id and ((x.account_move_id and x.account_move_id.date <= self.from_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.from_date  )) or (not x.stock_move_id and move.reference in (x.description or '') and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) )
        else:
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.move_id.id and ((x.account_move_id and x.account_move_id.date <= self.from_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.from_date ))   or (not x.stock_move_id and move.reference in (x.description or '') and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.move_id.id or move.reference in x.stock_valuation_layer_id.reference)) )
        Valuation_values = valuations.mapped("value")

        return Valuation_values

    def Valuation_values_gen_closing(self, move):
        if self.location_filter == 'all':
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id and ((x.account_move_id and x.account_move_id.date <= self.to_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) or (not x.stock_move_id and move.reference in (x.description or '') and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) )
        else:
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.move_id.id and ((x.account_move_id and x.account_move_id.date <= self.to_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) or (not x.stock_move_id and move.reference in (x.description or '') and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.move_id.id or move.reference in x.stock_valuation_layer_id.reference)) )
        Valuation_values = valuations.mapped("value")
        
        return Valuation_values

    def _filter_moves_wrt_location(self,stock_moves):
        
        if self.location_filter == 'single' and self.location:
            in_moves = stock_moves.filtered(lambda x: x.location_id not in self.location and x.location_dest_id  in self.location)
            out_moves = stock_moves.filtered(lambda x: x.location_id in self.location and x.location_dest_id not in self.location)
        else:
            in_moves =  stock_moves.filtered(lambda x: x.location_usage not in ("internal", "transit") and 
                      x.location_dest_usage in ("internal", "transit"))
            out_moves =  stock_moves.filtered(lambda x: x.location_usage in ("internal", "transit") and x.location_dest_usage not in ("internal", "transit") or 'RTN-VEN' in (x.reference or ''))
        return in_moves, out_moves

    def _filter_moves_wrt_location_for_sales_purchases(self,stock_moves): 
        
        purchases = stock_moves.filtered(lambda x: x.location_usage == "supplier")
        sales_in    = stock_moves.filtered(lambda x: x.location_usage == "inventory" and x.location_id.name not in ['Stock adjustment','Inventory adjustment']) 
        sales_out = stock_moves.filtered(lambda x: x.location_dest_usage in ["customer","production","inventory"] and x.location_dest_id.name not in ['Stock adjustment','Inventory adjustment'])
        
        if self.location_filter == 'single' and self.location:
            purchases  = purchases.filtered(lambda x: x.location_id not in self.location and x.location_dest_id  in self.location)
            sales_in  = sales_in.filtered(lambda x: x.location_dest_id in self.location and x.location_id  not in self.location)
            sales_out  = sales_out.filtered(lambda x: x.location_id in self.location and x.location_dest_id  not in self.location)
        return sales_in,sales_out,purchases

    def _filter_moves_wrt_location_for_transfers_in_out(self,stock_moves):
        in_moves =  stock_moves.filtered(lambda x:  x.location_usage  in ("internal") and 
                      x.location_dest_usage in ("internal"))
        out_moves =  stock_moves.filtered(lambda x: x.location_usage in ("internal") and 
                      x.location_dest_usage in ("internal"))
        if self.location_filter == 'single' and self.location:
            in_moves = in_moves.filtered(lambda x: x.location_id not in self.location and x.location_dest_id  in self.location)
            out_moves = out_moves.filtered(lambda x: x.location_id in self.location and x.location_dest_id not in self.location)
        return in_moves, out_moves
    
    
    def _filter_moves_wrt_location_for_adjustments(self,stock_moves):
        
        in_moves =  stock_moves.filtered(lambda x: x.location_usage  == "inventory" and x.location_id.name in ['Stock adjustment','Inventory adjustment'])
        out_moves =  stock_moves.filtered(lambda x: x.location_dest_usage == "inventory" and x.location_dest_id.name in ['Stock adjustment','Inventory adjustment'])
        
        if self.location_filter == 'single' and self.location:
            in_moves = in_moves.filtered(lambda x: x.location_id  in self.location and x.location_dest_id  not in self.location)
            out_moves = out_moves.filtered(lambda x: x.location_id not in self.location and x.location_dest_id  in self.location)
        return in_moves, out_moves
    
    def calculate_opening_balances(self,stock_moves):
        if not self.from_date:
            raise UserError("Please Enter Dates")
        in_moves, out_moves = self._filter_moves_wrt_location(stock_moves)
        if self.from_date:
            in_moves = in_moves.filtered(lambda x: x.move_date.date() < self.from_date)
            out_moves = out_moves.filtered(lambda x: x.move_date.date() < self.from_date)
        opening_balance = {}
        for move in in_moves:
            
            if f"{move.product_id.default_code}" not in opening_balance.keys():
                opening_balance[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "standard_price":move.product_id.standard_price,
                    "qty":move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": sum(self.Valuation_values_gen(move))
                }
                continue

            opening_balance[f"{move.product_id.default_code}"]["qty"] = opening_balance[f"{move.product_id.default_code}"]["qty"] + move.product_uom_qty
            opening_balance[f"{move.product_id.default_code}"]["amount"] = opening_balance[f"{move.product_id.default_code}"]["amount"] + sum(self.Valuation_values_gen(move))


        for move in out_moves:

            if f"{move.product_id.default_code}" not in opening_balance:
                opening_balance[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "standard_price":move.product_id.standard_price,
                    "qty": - abs(move.product_uom_qty if self.location_filter == 'all' else move.qty_done),
                    "amount":- abs(sum(self.Valuation_values_gen(move)))
                }
                continue
        
            opening_balance[f"{move.product_id.default_code}"]["qty"]=opening_balance[f"{move.product_id.default_code}"]["qty"] - abs(move.product_uom_qty if self.location_filter == 'all' else move.qty_done)
            opening_balance[f"{move.product_id.default_code}"]["amount"] = opening_balance[f"{move.product_id.default_code}"]["amount"] - abs(sum(self.Valuation_values_gen(move)))
        return opening_balance  

    def calculate_transfers_in(self,stock_moves):
        in_moves, out_moves = self._filter_moves_wrt_location_for_transfers_in_out(stock_moves)
        if self.from_date and self.to_date:
            in_moves = in_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        transfers_in = {}
        for move in in_moves:
            if f"{move.product_id.default_code}" not in transfers_in.keys():
                transfers_in[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "standard_price":move.product_id.standard_price,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": 0
                }
                continue
            
            transfers_in[f"{move.product_id.default_code}"]["qty"]=transfers_in[f"{move.product_id.default_code}"]["qty"] + move.product_uom_qty if self.location_filter == 'all' else move.qty_done
            transfers_in[f"{move.product_id.default_code}"]["amount"]=0
             
        return transfers_in
    
    def calculate_transfers_out(self,stock_moves):
        in_moves, out_moves = self._filter_moves_wrt_location_for_transfers_in_out(stock_moves)
        if self.from_date and self.to_date:
            out_moves = out_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        transfers_out = {}
        for move in out_moves:
            if f"{move.product_id.default_code}" not in transfers_out.keys():
                transfers_out[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "standard_price":move.product_id.standard_price,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": 0
                }
                continue
            
            transfers_out[f"{move.product_id.default_code}"]["qty"] = transfers_out[f"{move.product_id.default_code}"]["qty"] + move.product_uom_qty if self.location_filter == 'all' else move.qty_done
            transfers_out[f"{move.product_id.default_code}"]["amount"] = 0
            
        return transfers_out

   
    def calculate_purchases(self, stock_moves):        
        sales_in,sales_out, purchases = self._filter_moves_wrt_location_for_sales_purchases(stock_moves)
        
        if self.from_date and self.to_date:
            purchases = purchases.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        # in_valuations = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', purchases.ids)]) if purchases else None
        
        purchases_balance = {}
        
        for move in purchases:
            product_code = f"{move.product_id.default_code}"
            valuation_values = self.Valuation_values_gen_closing(move)
            total_valuation = sum(valuation_values)  # Sum all valuation values for the move

            if product_code not in purchases_balance:
                purchases_balance[product_code] = {
                    "code": move.product_id.default_code,
                    "name": move.product_id.name,
                    "uom": move.product_uom.name,
                    "standard_price":move.product_id.standard_price,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": total_valuation,
                    
                }
            else:
                purchases_balance[product_code]["qty"] += move.product_uom_qty if self.location_filter == 'all' else move.qty_done
                purchases_balance[product_code]["amount"] += total_valuation

        vendor_returns = stock_moves.filtered(lambda x: 'RTN-VEN' in (x.reference or '') or x.location_dest_id.usage == 'supplier')
        for move in vendor_returns:
            product_code = f"{move.product_id.default_code}"
            valuation_values = self.Valuation_values_gen_closing(move)
            total_valuation = sum(valuation_values)  # Sum all valuation values for the move
            if product_code in purchases_balance:
                purchases_balance[product_code]["qty"] -= move.product_uom_qty if self.location_filter == 'all' else move.qty_done
                purchases_balance[product_code]["amount"] -= abs(total_valuation)
        return purchases_balance


    def calculate_sales(self, stock_moves):        
        sales_in,sales_out, purchases = self._filter_moves_wrt_location_for_sales_purchases(stock_moves)

        if self.from_date and self.to_date:
            sales_in = sales_in.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
            sales_out = sales_out.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        sales_balance = {}

        for move in sales_in:
            product_code = f"{move.product_id.default_code}"
            valuation_values = self.Valuation_values_gen_closing(move)
            total_valuation = sum(valuation_values)  # Sum all valuation values for the move

            if product_code not in sales_balance:
                sales_balance[product_code] = {
                    "code": move.product_id.default_code,
                    "name": move.product_id.name,
                    "uom": move.product_uom.name,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "standard_price":move.product_id.standard_price,
                    "amount": total_valuation,
                }
            else:
                sales_balance[product_code]["qty"] += move.product_uom_qty if self.location_filter == 'all' else move.qty_done
                sales_balance[product_code]["amount"] += total_valuation
        for move in sales_out:
            product_code = f"{move.product_id.default_code}"
            valuation_values = self.Valuation_values_gen_closing(move)
            total_valuation = sum(valuation_values)
            if product_code not in sales_balance:
                sales_balance[product_code] = {
                    "code": move.product_id.default_code,
                    "name": move.product_id.name,
                    "uom": move.product_uom.name,
                    "qty": - (move.product_uom_qty if self.location_filter == 'all' else move.qty_done),
                    "standard_price": move.product_id.standard_price,
                    "amount": -total_valuation,
                }
            else:
                sales_balance[product_code]["qty"] -= (move.product_uom_qty if self.location_filter == 'all' else move.qty_done)
                sales_balance[product_code]["amount"] -= total_valuation
        return sales_balance

   
    def calculate_adjustments(self,stock_moves):
        in_moves, out_moves = self._filter_moves_wrt_location_for_adjustments(stock_moves)
        if self.from_date and self.to_date:
            in_moves = in_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
            out_moves = out_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        adjustments = {}
        for move in in_moves:
            if f"{move.product_id.default_code}" not in adjustments.keys():
                adjustments[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "standard_price":move.product_id.standard_price,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": sum(self.Valuation_values_gen_closing(move))
                }
                continue

            adjustments[f"{move.product_id.default_code}"]["qty"] = adjustments[f"{move.product_id.default_code}"]["qty"] + move.product_uom_qty if self.location_filter == 'all' else move.qty_done
            adjustments[f"{move.product_id.default_code}"]["amount"] = adjustments[f"{move.product_id.default_code}"]["amount"] + sum(self.Valuation_values_gen_closing(move))
        
        for move in out_moves:
            if f"{move.product_id.default_code}" not in adjustments.keys():
                adjustments[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "standard_price":move.product_id.standard_price,
                    "qty": - abs(move.product_uom_qty if self.location_filter == 'all' else move.qty_done),
                    "amount": - abs(sum(self.Valuation_values_gen_closing(move)))
                }
                continue

            adjustments[f"{move.product_id.default_code}"]["qty"] = adjustments[f"{move.product_id.default_code}"]["qty"] - abs(move.product_uom_qty if self.location_filter == 'all' else move.qty_done)
            adjustments[f"{move.product_id.default_code}"]["amount"] = adjustments[f"{move.product_id.default_code}"]["amount"] - abs(sum(self.Valuation_values_gen_closing(move)))

        return adjustments

    def calculate_closing(self,stock_moves):
        in_moves, out_moves = self._filter_moves_wrt_location(stock_moves)
        if self.from_date and self.to_date:
            in_moves = in_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
            out_moves = out_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        closing_balance = {}
        for move in in_moves:
            if f"{move.product_id.default_code}" not in closing_balance.keys():
                closing_balance[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": sum(self.Valuation_values_gen_closing(move))}
                continue
            closing_balance[f"{move.product_id.default_code}"]["qty"] = closing_balance[f"{move.product_id.default_code}"]["qty"] + move.product_uom_qty if self.location_filter == 'all' else move.qty_done
            closing_balance[f"{move.product_id.default_code}"]["amount"] = closing_balance[f"{move.product_id.default_code}"]["amount"] + sum(self.Valuation_values_gen_closing(move))
        for move in out_moves:
            if f"{move.product_id.default_code}" not in closing_balance:
                closing_balance[f"{move.product_id.default_code}"] = {
                    "code":move.product_id.default_code,
                    "name":move.product_id.name,
                    "uom":move.product_id.uom_name,
                    "qty": - move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": - abs(sum(self.Valuation_values_gen_closing(move)))
                }
                continue
            closing_balance[f"{move.product_id.default_code}"]["qty"] = closing_balance[f"{move.product_id.default_code}"]["qty"] - abs(move.product_uom_qty) if self.location_filter == 'all' else abs(move.qty_done)
            closing_balance[f"{move.product_id.default_code}"]["amount"] = closing_balance[f"{move.product_id.default_code}"]["amount"] - abs(sum(self.Valuation_values_gen_closing(move)))
        return closing_balance

    def _prepare_report_data(self):
        stock_moves = self.filteration()
        final_data = {}
        opening_balances = list(self.calculate_opening_balances(stock_moves).values())
        transfers_in  = list(self.calculate_transfers_in(stock_moves).values())
        transfers_out = list(self.calculate_transfers_out(stock_moves).values())
        purchases     = list(self.calculate_purchases(stock_moves).values())
        sales         = list(self.calculate_sales(stock_moves).values())
        adjustments   = list(self.calculate_adjustments(stock_moves).values())
        closing_balances =  list(self.calculate_closing(stock_moves).values())
        for i in range(max(len(opening_balances),len(transfers_in),len(transfers_out),len(purchases),len(sales),len(adjustments),len(closing_balances))):
            if len(opening_balances) > i:
                current_value = opening_balances[i]
                if not current_value.get('code'):
                   continue
                if current_value.get('code') not in final_data.keys():
                        final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "opening":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })
            if len(transfers_in) > i:
                current_value = transfers_in[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}    
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "transfers_in":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })

            if len(transfers_out) > i:
                current_value = transfers_out[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "transfers_out":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })

            if len(purchases) > i:
                current_value = purchases[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "purchases":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })

            if len(sales) > i:
                current_value = sales[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "sales":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })

            if len(adjustments) > i:
                current_value = adjustments[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "adjustments":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })
            

            if len(closing_balances) > i:
                current_value = closing_balances[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "closing_balances":{
                        "qty":current_value.get('qty'),
                        "amount":current_value.get('amount')
                    },
                })
            
        sorted_products  = sorted(
        filter(lambda x: isinstance(x['product_code'], str), final_data.values()),
        key=lambda x: x['product_code']
        )
        final_data = {product['product_code']: product for product in sorted_products}
        # for i, j in final_data.items():
        #     j['closing'] = {'amount' : closing_balances.get(i, 0)}         

        return list(final_data.values())


    def action_print_excel_report(self):
        data =  self._prepare_report_data()
        excel_encode = io.BytesIO()
        filename = "Stock Status Inventory Report - " + str(self.to_date.strftime("%d-%m-%Y")) + ".xlsx"
        workbook = xlsxwriter.Workbook(excel_encode)
        sheet = workbook.add_worksheet('Inventory Closing reports')
        header = workbook.add_format({'bold': True, 'align': 'center', 'size': 12 ,'font_name': 'Times New Roman'})
        header.set_border()
        normal_text = workbook.add_format({'align': 'left', 'size': 12})
        normal_amount = workbook.add_format({'align': 'right', 'size': 12})
        current_date = datetime.now() + timedelta(hours=5)
        format_str = "%m/%d/%y %H:%M:%S"
        summary_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 12 , 'font_name': 'Times New Roman'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 12 , 'font_name': 'Times New Roman'})
        description_format = workbook.add_format({'align': 'left', 'size': 10 , 'font_name' : 'Times New Roman'})
        normal_format = workbook.add_format({'align': 'center', 'size': 10 , 'font_name': 'Times New Roman'})
        date_format = workbook.add_format({'align': 'left', 'size': 12 , 'font_name': 'Times New Roman'})
        time_format = workbook.add_format({ 'align': 'right', 'size': 12 , 'font_name': 'Times New Roman'})

        
        big_heading = "Biafo Industries Limited"
        sub_heading = "Stock Status Report - Summary"
        # sub_heading_1 = f"""({"From: "+ datas.get('from_date') if datas.get('from_date') else ''}{", To: "+ datas.get('to_date') if datas.get('to_date') else ''} Rupees, Stock Items)"""
        sub_heading_1 = f"( From Date: {self.from_date} To {self.to_date}"
        
        if self.product_filter == 'range':
            sub_heading_1 += f", From Product: {self.from_product.default_code} To {self.to_product.default_code}"
        elif self.product_filter == 'single':
            sub_heading_1 += f", Product: "
            for product in self.product_ids:
                if product.default_code:
                    sub_heading_1 += f", {product.default_code}"
        sub_heading_1 += ", Rupees, Stock Items )"
        sheet.merge_range(0, 1, 1, 61, big_heading, summary_format)
        sheet.merge_range(2, 1, 2, 61, sub_heading, summary_format)
        sheet.merge_range(3, 1, 3, 61, sub_heading_1, normal_format)
        column_widths = { 0 : 6.36 , 
                 1: 1.09, 2: 13.27, 3: 1.45, 4: 6.64, 5: 0.61, 6: 2.18, 7: 17, 8: 0.61, 9: 0.67,

            10: 5.64, 11: 1.91, 12: 0.67, 13: 10.18, 14: 1.55, 15: 1.36, 16: 0.61, 17:4.36,

            18: 9.64, 19: 3.45, 20: 11, 21: 2.09, 22: 1.18, 23: 7.82, 24: 6.09,  25: 3.64, 26: 6.73, 27: 6.27, 28: 0.78,

            29: 1.45, 30: 12.64, 31: 3.36, 32: 8.09, 33: 4.91, 34: 0.78, 35: 10.55, 36: 3.64,

            37: 3.55, 38: 10.36, 39: 2.64, 40: 0.78 , 41: 7.82 , 42: 6.36 , 43: 0.94, 44: 3.09, 45 : 7.91 , 
            46: 0.94 , 47: 0.61,48 : 3.36  , 49 : 0.78 , 50: 6.36 , 
            51: 1.27 , 52: 6.64 , 53: 4.09 , 54 : 2.64 , 55: 5.64 , 
            56 : 2.09 , 57: 3.82 , 58 : 0.78 , 59: 3.09 , 60: 11.09 
            }   

        for col, width in column_widths.items():
                sheet.set_column(col, col, width)
        sheet.set_row(4, 4.50)
        sheet.set_row(6, 7)

        sheet.merge_range(5, 1, 5, 6, f"Date:  {datetime.now().strftime('%d-%m-%Y')}", date_format)
        sheet.merge_range(5, 56, 5, 60, f"Time:  {datetime.now().strftime('%H:%M:%S')}", time_format)

        sheet.merge_range(7 ,14 ,7 , 17 , "Opening" , summary_format )
        sheet.merge_range(7 ,21 ,7 , 23 , "Transfers In" ,summary_format )
        sheet.merge_range(7 ,27 ,7 , 29 , "Purchases" ,summary_format )
        sheet.merge_range(7 ,33 ,7 , 35, "Consumptions/Sales" ,summary_format )
        sheet.merge_range(7 ,39 ,7 , 41  , "Adjustments" ,summary_format )
        sheet.merge_range(7 ,46 ,7 , 50 , "Transfers Out" ,summary_format )
        sheet.merge_range(7 ,57 ,7 , 59 , "Closing" ,summary_format )

        sheet.merge_range(8,2 ,8 , 3 , "Product Code" ,header_format )
        sheet.merge_range(8,6 ,8 , 8, "Description" ,header_format )

        sheet.merge_range(8,9 ,8 , 11 , "Units" ,header_format )

        sheet.merge_range(8,13,8 ,15 , "Quantity" ,header_format )
        sheet.merge_range(8,17 ,8 , 18 , "Amount " ,header_format )
        
        sheet.merge_range(8,20 ,8 , 21 , "Quantity" ,header_format )
        sheet.merge_range(8,23 ,8 , 24, "Amount" ,header_format )

         
        sheet.merge_range(8,26 ,8 , 27 , "Quantity" ,header_format )
        sheet.merge_range(8,29 ,8 , 30, "Amount" ,header_format )

        sheet.merge_range(8,32 ,8 , 33, "Quantity" ,header_format )
        sheet.merge_range(8,35 ,8 , 36, "Amount" ,header_format )

        sheet.merge_range(8,38 ,8 , 39, "Quantity" ,header_format )
        sheet.merge_range(8,41,8 , 42, "Amount" ,header_format )

        sheet.merge_range(8,44 ,8 , 48 , "Quantity" ,header_format )
        sheet.merge_range(8,50 ,8 , 52, "Amount" ,header_format )

        sheet.merge_range(8,54 ,8 ,57, "Quantity" ,header_format )
        sheet.merge_range(8,59,8 , 60, "Amount" ,header_format )
            #####
        # data implementation start
        counter = 9

        total_opening_qty = 0
        total_opening_amount = 0
        total_transfers_in_qty = 0
        total_transfers_in_amount = 0
        total_purchases_qty = 0
        total_purchases_amount = 0
        total_sales_qty = 0
        total_sales_amount = 0
        total_adjustments_qty = 0
        total_adjustments_amount = 0
        total_transfers_out_qty = 0 
        total_transfers_out_amount = 0 
        total_closing_balance_qty = 0 
        total_closing_balance_amount = 0
        
        for record in data:
            opening_balance = record.get('opening',{})
            transfers_in = record.get('transfers_in',{})
            purchases = record.get('purchases',{})
            sales = record.get('sales',{})
            adjustments = record.get('adjustments',{})
            transfers_out = record.get('transfers_out',{})
            closing_balances = record.get('closing_balances',{})
            qty = 0
            amount = 0

            if round(adjustments.get('qty', 0),2) > 0:
                qty = abs(opening_balance.get('qty', 0)) + abs(transfers_in.get('qty', 0)) + abs(purchases.get('qty', 0)) + abs(adjustments.get('qty', 0)) - (abs(sales.get('qty', 0)) + abs(transfers_out.get('qty', 0)))    
            else:
                qty = abs(opening_balance.get('qty', 0)) + abs(transfers_in.get('qty', 0)) + abs(purchases.get('qty', 0)) - (abs(sales.get('qty', 0)) + abs(transfers_out.get('qty', 0)) + abs(adjustments.get('qty', 0)))
            # Ensure qty is non-negative
            qty = max(0, qty)


            if round(adjustments.get('amount', 0),2) > 0:
                amount = abs(opening_balance.get('amount', 0)) + abs(transfers_in.get('amount', 0)) + abs(purchases.get('amount', 0)) + abs(adjustments.get('amount', 0)) - (abs(sales.get('amount', 0)) + abs(transfers_out.get('amount', 0)))
            else:
                amount = abs(opening_balance.get('amount', 0)) + abs(transfers_in.get('amount', 0)) + abs(purchases.get('amount', 0)) - (abs(sales.get('amount', 0)) + abs(adjustments.get('amount', 0)) + abs(transfers_out.get('amount', 0)))
            # Ensure amount is non-negative
            amount = max(0, amount)            


            sheet.merge_range(counter,2 , counter , 3 , record.get('product_code',None) , normal_format )
            sheet.merge_range(counter,6 , counter , 8, record.get('product_description',None) ,description_format)
            sheet.merge_range(counter,9 , counter, 11 , record.get('product_unit',None) ,normal_format )
            
            if round(opening_balance.get('qty',0),2) >= 0:
                sheet.merge_range(counter,13, counter ,15 , '{:,.2f}'.format(abs(opening_balance.get('qty',0))),normal_format )
            else:
                sheet.merge_range(counter,13, counter ,15 ,"(" + str('{:,.2f}'.format(abs(opening_balance.get('qty',0)))) + ")" ,normal_format )
            total_opening_qty +=  opening_balance.get('qty',0)
            
            if round(opening_balance.get('amount',0),2) >= 0:
                sheet.merge_range(counter,17 ,counter, 18 , '{:,.2f}'.format(abs(opening_balance.get('amount',0))),normal_format)
            else:
                sheet.merge_range(counter,17 ,counter, 18 ,"(" + str('{:,.2f}'.format(abs(opening_balance.get('amount',0)))) + ")" ,normal_format)
            total_opening_amount += opening_balance.get('amount',0)

            
            sheet.merge_range(counter,20 ,counter , 21 , '{:,.2f}'.format(abs(transfers_in.get('qty',0))),normal_format )
            sheet.merge_range(counter,23 ,counter, 24,'{:,.2f}'.format(abs(transfers_in.get('amount',0))), normal_format )
            total_transfers_in_qty += transfers_in.get('qty',0)
            total_transfers_in_amount += transfers_in.get('amount',0)
            
            if round(purchases.get('qty',0),2) >= 0 :
                sheet.merge_range(counter,26 ,counter , 27 , '{:,.2f}'.format(abs(purchases.get('qty',0))),normal_format )
            else:
                sheet.merge_range(counter,26 ,counter , 27 ,"(" + str('{:,.2f}'.format(abs(purchases.get('qty',0)))) + ")" ,normal_format )
            total_purchases_qty += purchases.get('qty',0)
            
            if round(purchases.get('amount',0),2) >= 0:
                sheet.merge_range(counter,29 ,counter , 30, '{:,.2f}'.format(abs(purchases.get('amount',0))),normal_format )
            else:
                sheet.merge_range(counter,29 ,counter , 30,"(" + str('{:,.2f}'.format(abs(purchases.get('amount',0)))) + ")" ,normal_format )
            total_purchases_amount += purchases.get('amount',0)
            
            # if sales.get('qty',0) >= 0:
                # sheet.merge_range(counter,32 ,counter , 33, '{:,.2f}'.format(sales.get('qty',0)),normal_format )
            # else:
            sheet.merge_range(counter,32 ,counter , 33,"(" + str('{:,.2f}'.format(abs(sales.get('qty',0)))) + ")" ,normal_format )
            total_sales_qty += sales.get('qty',0)
            sheet.merge_range(counter,35 ,counter, 36,"(" + str('{:,.2f}'.format(abs(sales.get('amount',0)))) + ")" ,normal_format )
            total_sales_amount += sales.get('amount',0)
            # if sales.get('amount',0) >= 0:
            #     sheet.merge_range(counter,35 ,counter, 36, '{:,.2f}'.format(sales.get('amount',0)),normal_format )
            # else:
            
            if round(adjustments.get('qty',0),2) >= 0:
                sheet.merge_range(counter,38 ,counter , 39, '{:,.2f}'.format(abs(adjustments.get('qty',0))),normal_format )
            else:
                sheet.merge_range(counter,38 ,counter , 39,"(" + str('{:,.2f}'.format(abs(adjustments.get('qty',0)))) + ")" ,normal_format )
            total_adjustments_qty += adjustments.get('qty',0)

            if  round(adjustments.get('amount',0),2) >= 0:
                sheet.merge_range(counter,41, counter, 42,'{:,.2f}'.format(abs(adjustments.get('amount',0))) , normal_format )
            else:
                sheet.merge_range(counter,41, counter, 42,  "(" + str('{:,.2f}'.format(abs(adjustments.get('amount',0)))) + ")"  , normal_format )
            total_adjustments_amount += adjustments.get('amount',0)

            # if adjustments.get('amount',0) >= 0:
            #     sheet.merge_range(counter,41, counter, 42,'{:,.2f}'.format(adjustments.get('amount',0)) , normal_format )
            # else:
            #     sheet.merge_range(counter,41, counter, 42,  "(" + str('{:,.2f}'.format(abs(adjustments.get('amount',0)))) + ")"  , normal_format )

            sheet.merge_range(counter,44 ,counter , 48 , "(" + str('{:,.2f}'.format(abs(transfers_out.get('qty',0)))) + ")"    , normal_format )
            total_transfers_out_qty += transfers_out.get('qty',0)
            
            sheet.merge_range(counter,50 ,counter , 52,  "(" + str('{:,.2f}'.format(abs(transfers_out.get('amount',0)))) + ")" ,normal_format )
            total_transfers_out_amount += transfers_out.get('amount',0)
            
            if round(closing_balances.get('qty',0) + opening_balance.get('qty',0),2) >= 0:
                sheet.merge_range(counter,54 ,counter ,57,   '{:,.2f}'.format(abs(closing_balances.get('qty',0) + opening_balance.get('qty',0))) , normal_format )
            else:
                sheet.merge_range(counter,54 ,counter ,57,  "(" + str('{:,.2f}'.format(abs(closing_balances.get('qty',0) + opening_balance.get('qty',0)))) + ")"  , normal_format )
            total_closing_balance_qty += (closing_balances.get('qty',0) + opening_balance.get('qty',0))
            
            if round(closing_balances.get('amount',0) + opening_balance.get('amount',0),2) >= 0:
                sheet.merge_range(counter,59, counter, 60,   '{:,.2f}'.format(abs(closing_balances.get('amount',0) + opening_balance.get('amount',0))) , normal_format )
            else:
                sheet.merge_range(counter,59, counter, 60,  "(" + str('{:,.2f}'.format(abs(closing_balances.get('amount',0) + opening_balance.get('amount',0)))) + ")"  , normal_format )
            total_closing_balance_amount += ((closing_balances.get('amount',0) + opening_balance.get('amount',0)))
            counter +=1

        sheet.merge_range(counter,9 ,counter, 11 , "Total" ,header_format)
        if round(total_opening_qty,2)>= 0 :
            sheet.merge_range(counter,13,counter ,15 , '{:,.2f}'.format(abs(total_opening_qty)) ,header_format )
        else:
            sheet.merge_range(counter,13,counter ,15 , "(" + str('{:,.2f}'.format(abs(total_opening_qty))) + ")"  ,header_format )
        
        if round(total_opening_amount,2) >= 0:
            sheet.merge_range(counter,17 ,counter, 18 ,'{:,.2f}'.format(abs(total_opening_amount)) ,header_format )
        else:
            sheet.merge_range(counter,17 ,counter, 18 ,"(" + str('{:,.2f}'.format(abs(total_opening_amount))) + ")"  ,header_format )

        sheet.merge_range(counter,20 ,counter , 21 , '{:,.2f}'.format(abs(total_transfers_in_qty)) ,header_format )
        sheet.merge_range(counter,23 ,counter , 24, '{:,.2f}'.format(abs(total_transfers_in_amount)) ,header_format )

        if round(total_purchases_qty,2) >= 0:
            sheet.merge_range(counter,26 ,counter, 27 ,'{:,.2f}'.format(abs(total_purchases_qty)) ,header_format )
        else:
            sheet.merge_range(counter,26 ,counter, 27 ,"(" + str('{:,.2f}'.format(abs(total_purchases_qty))) + ")" ,header_format )
        
        if round(total_purchases_amount,2) >= 0:
            sheet.merge_range(counter,29 ,counter, 30,'{:,.2f}'.format(abs(total_purchases_amount)) ,header_format )
        else:
            sheet.merge_range(counter,29 ,counter, 30,"(" + str('{:,.2f}'.format(abs(total_purchases_amount))) + ")" ,header_format )

        sheet.merge_range(counter,32 ,counter, 33, "(" + str('{:,.2f}'.format(abs(total_sales_qty))) + ")",header_format )
        sheet.merge_range(counter,35 ,counter , 36,  "(" + str('{:,.2f}'.format(abs(total_sales_amount))) + ")",header_format )

        if round(total_adjustments_qty,2) >= 0:
            sheet.merge_range(counter,38 ,counter , 39, '{:,.2f}'.format(abs(total_adjustments_qty)) ,header_format )
        else:
            sheet.merge_range(counter,38 ,counter , 39, "(" + str('{:,.2f}'.format(abs(total_adjustments_qty))) + ")" ,header_format )
        
        if round(total_adjustments_amount,2) >= 0:
            sheet.merge_range(counter,41,counter, 42, '{:,.2f}'.format(abs(total_adjustments_amount)) ,header_format )
        else:
            sheet.merge_range(counter,41,counter, 42, "(" + str('{:,.2f}'.format(abs(total_adjustments_amount))) + ")" ,header_format )

        sheet.merge_range(counter,44 ,counter , 48 , "(" + str('{:,.2f}'.format(abs(total_transfers_out_qty))) + ")" ,header_format )
        sheet.merge_range(counter,50 ,counter, 52, "(" + str('{:,.2f}'.format(abs(total_transfers_out_amount))) + ")" ,header_format )

        if round(total_closing_balance_qty,2) >= 0:
            sheet.merge_range(counter,54 ,counter ,57,'{:,.2f}'.format(abs(total_closing_balance_qty)) ,header_format )
        else:
            sheet.merge_range(counter,54 ,counter ,57,"(" + str('{:,.2f}'.format(abs(total_closing_balance_qty))) + ")" ,header_format )
        
        if round(total_closing_balance_amount,2) >= 0:
            sheet.merge_range(counter,59,counter, 60, '{:,.2f}'.format(abs(total_closing_balance_amount)) ,header_format )
        else:
            sheet.merge_range(counter,59,counter, 60, "(" + str('{:,.2f}'.format(abs(total_closing_balance_amount))) + ")" ,header_format )

        # Write the summary row
        if self.render_type:
            summary_format = workbook.add_format({'bold': True, 'align': 'center', 'size': 11})

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