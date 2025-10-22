from odoo import models, fields, api

from odoo.exceptions import UserError

from datetime import datetime
class StockSalePositionWizard(models.TransientModel):
    _name = 'stock.sale.position.wizard.custom'
    _description = 'Stock Safe Position Wizard Custom'


    report_type = fields.Selection([('all','All'),('closing_balance',' Closing Balances')],string="Report",default="all")
    # products section
    product_filter = fields.Selection([('all','All'),('single','Single'),('range','Range')],string="Product",default="range")
    from_product =  fields.Many2one('product.product',string="From")
    to_product = fields.Many2one('product.product',string="To")
    product_id = fields.Many2one('product.product',string="Product")
    product_ids = fields.Many2many("product.product", string="Products")
    # Dates Section
    date_filter =  fields.Selection([('all','All'),('range','Range')],string="Date",default="range")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    #Location Section
    location_filter = fields.Selection([('all','All'),('single','Single')],string="Location",default="all")
    location = fields.Many2many('stock.location',string="Location")
    
    stock_file_data = fields.Binary('Inventory Age Report File')
    company_ids = fields.Many2many("res.company", string="Companies")

    # Category Filter
    # category_filter = fields.Selection([('all','All'),('single','Single')],string="Category",default="all")
    # product_category_ids = fields.Many2many("product.category", string="Product Categories")
    product_category = fields.Selection(
        selection='_get_product_categories',
        string="Product Category",
        default='all'
    )

    @api.onchange('product_category')
    def _onchange_product_category(self):
        if self.product_category and self.product_category != 'all':
            domain = [('level_2_cat', '=', self.product_category)]
            return {
                'domain': {
                    'from_product': domain,
                    'to_product': domain,
                }
            }
        else:
            # Return empty domain to allow all products
            return {
                'domain': {
                    'from_product': [],
                    'to_product': [],
                }
            }


    # With amount without amount
    render_type = fields.Selection([('qty','Quantity'),('amount','Amount'),('both','Both')],string="Select Type",default="both")
    # with_qty =fields.Selection([('qty_true','Including Zero Quantity'),('qty_false','Without Zero Qty')],string="Select Quantity",default="qty_true")


    @api.model
    def _get_product_categories(self):
        selected = ['Finished Goods', 'Semi Finished Goods', 'Work In Process']

        # Using read_group to fetch unique categories more efficiently
        categories = self.env['product.product'].read_group(
            domain=[('level_2_cat', '!=', False)],
            fields=['level_2_cat'],
            groupby=['level_2_cat']
        )
        
        # Filter categories based on the selected list
        filtered_categories = [
            (cat['level_2_cat'], cat['level_2_cat'])
            for cat in categories
            if cat['level_2_cat'] in selected
        ]

        # Adding 'all' option at the beginning
        category_list = [('all', 'All')] + filtered_categories

        return category_list

    def product_search_by_range(self):
        for rec in self:
            products_in_order = []
            if rec.from_product and rec.to_product:
                from_product = int(''.join((rec.from_product.default_code).split('-')))
                to_product = int(''.join((rec.to_product.default_code).split('-')))
                if from_product < to_product:
                    start = from_product
                    end = to_product
                else :
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
            
        # if self.category_filter == 'single' and self.product_category_ids:
        #     stock_moves = stock_moves.filtered(lambda x : x.product_id.categ_id in self.product_category_ids)
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
        sales_out = stock_moves.filtered(lambda x: x.location_dest_usage in ["customer","inventory"] and x.location_dest_id.name not in ['Stock adjustment','Inventory adjustment'])
        
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
            in_moves = in_moves.filtered(lambda x: self.from_date <= x.date.date() <= self.to_date)
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
            out_moves = out_moves.filtered(lambda x: self.from_date <= x.date.date() <= self.to_date)
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
            
            transfers_out[f"{move.product_id.default_code}"]["qty"]=transfers_out[f"{move.product_id.default_code}"]["qty"] + move.product_uom_qty if self.location_filter == 'all' else move.qty_done
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

    def calculate_consumption(self,stock_moves):
        consumption_balance = {}
        purchase_balance={}

        consumption = stock_moves.filtered(lambda x: x.location_dest_id.name == "Production")
        purchase = stock_moves.filtered(lambda x: x.location_id.name == "Vendors")
        if self.from_date and self.to_date:
            consumption = consumption.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
            if consumption:
                for move in consumption:
                    product_code = f"{move.product_id.default_code}"
                    valuation_values = self.Valuation_values_gen_closing(move)
                    total_valuation = sum(valuation_values)  # Sum all valuation values for the move

                    if product_code not in consumption_balance:
                        consumption_balance[product_code] = {
                            "code": move.product_id.default_code,
                            "name": move.product_id.name,
                            "uom": move.product_uom.name,
                            "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                            "standard_price":move.product_id.standard_price,
                            "amount": total_valuation,
                        }
                    else:
                        consumption_balance[product_code]["qty"] += move.product_uom_qty if self.location_filter == 'all' else move.qty_done
                        consumption_balance[product_code]["amount"] += total_valuation
            if purchase:
                for move in purchase:
                    product_code = f"{move.product_id.default_code}"
                    valuation_values = self.Valuation_values_gen_closing(move)
                    total_valuation = sum(valuation_values)  # Sum all valuation values for the move

                    if product_code not in purchase_balance:
                        purchase_balance[product_code] = {
                            "code": move.product_id.default_code,
                            "name": move.product_id.name,
                            "uom": move.product_uom.name,
                            "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                            "standard_price":move.product_id.standard_price,
                            "amount": total_valuation,
                        }
                    else:
                        purchase_balance[product_code]["qty"] += move.product_uom_qty if self.location_filter == 'all' else move.qty_done
                        purchase_balance[product_code]["amount"] += total_valuation
        return consumption_balance,purchase_balance

    
    def calculate_production(self, stock_moves):
        production_moves = stock_moves.filtered(lambda x: x.production_id)
        if self.from_date and self.to_date:
            production_moves = production_moves.filtered(lambda x: self.from_date <= x.move_date.date() <= self.to_date)
        production_data = {}

        for move in production_moves:
            product_code = f"{move.product_id.default_code}"
            if product_code not in production_data:
                production_data[product_code] = {
                    "code": move.product_id.default_code,
                    "name": move.product_id.name,
                    "uom": move.product_uom.name,
                    "qty": move.product_uom_qty if self.location_filter == 'all' else move.qty_done,
                    "amount": 0  # Assuming amount is not relevant for production
                }
            else:
                production_data[product_code]["qty"] += move.product_uom_qty if self.location_filter == 'all' else move.qty_done

        return production_data
    
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
        production    = list(self.calculate_production(stock_moves).values())
        closing_balances = list(self.calculate_closing(stock_moves).values())
        consumption,purchase   = self.calculate_consumption(stock_moves)
        consumption=list(consumption.values())
        purchase=list(purchase.values())
        
        for i in range(max(len(opening_balances),len(transfers_in),len(transfers_out),len(purchases),len(sales),len(adjustments),len(consumption))):
            if len(production) > i:
                current_value = production[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code": current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_standard_price": current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_description": current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_unit": current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None,
                    "production": {
                        "qty": current_value.get('qty'),
                        "amount": current_value.get('amount')
                    },
                })
            production_qty = sum(move.product_uom_qty for move in stock_moves if move.production_id)

            # Add the production data to the final result
            production_data = {
                "production": {
                    "qty": production_qty,
                    "amount": 0  # Assuming amount is not relevant for production_qty
                }
            }

            # Add the production data to all products in the final_data
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
            if len(consumption)>i:
                current_value = consumption[i]
                if not current_value.get('code'):
                    continue
                if current_value.get('code') not in final_data.keys():
                    final_data[current_value.get('code')] = {}
                final_data[current_value.get('code')].update({
                    "product_code":current_value.get('code') or final_data[current_value.get('code')].get('product_code') or None,
                    "product_description":current_value.get('name') or final_data[current_value.get('code')].get('product_description') or None,
                    "product_standard_price":current_value.get('standard_price') or final_data[current_value.get('code')].get('product_standard_price') or None,
                    "product_unit":current_value.get('uom') or final_data[current_value.get('code')].get('product_unit') or None ,
                    "consumption":{
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
        # raise UserError(str(final_data))
        return list(final_data.values())


    def generate_report(self):
        report_data = self._prepare_report_data()
        
        return self.env.ref('stock_sale_position_report.action_stock_sale_position_pdf_custom').report_action(
            self, data={'report_data': report_data,
                        "to_date":self.to_date,
                        "from_date":self.from_date,
                        }
        )