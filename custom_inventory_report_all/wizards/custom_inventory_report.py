from odoo import fields, models, api, _
import base64
from io import BytesIO
import json
from odoo.exceptions import UserError


class CustomInventoryReport(models.TransientModel):
    _name = "custom.inventory.report.all"
    
    report_type = fields.Selection([("all","All"),("closing_balance"," Closing Balances")],string="Report",default="all")

    # products section
    product_filter = fields.Selection([("all","All"),("single","Single"),("range","Range")],string="Product",default="all")
    from_product =  fields.Many2one("product.product",string="From")
    to_product = fields.Many2one("product.product",string="To")
    product_id = fields.Many2one("product.product",string="Product")
    product_ids = fields.Many2many("product.product", string="Products")

    # Dates Section
    date_filter =  fields.Selection([("range","Range")],string="Date",default="range")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")

    #Location Section
    location_filter = fields.Selection([("all","All"),("single","Single")],string="Location",default="all")
    location = fields.Many2many("stock.location",string="Location")  

    stock_file_data = fields.Binary("Inventory Age Report File")
    company_ids = fields.Many2many("res.company", string="Companies")

    # Category Filter
    category_filter = fields.Selection([("all","All"),("single","Single")],string="Category",default="all")
    product_category_ids = fields.Many2many("product.category", string="Product Categories")

    # With amount without amount
    with_amount = fields.Selection([("amount_true","With Amount"),("amount_false","Without Amount")],string="Select Type",default="amount_true")
    with_qty =fields.Selection([("qty_true","Including Zero Quantity"),("qty_false","Without Zero Qty")],string="Select Quantity",default="qty_true")

    def get_in_moves(self, moves):
        return moves.filtered(
            lambda move: move.location_usage not in ("internal", "transit") and 
                          move.location_dest_usage in ("internal", "transit")
        )        
    
    def get_out_moves(self, moves):
        return moves.filtered(
            lambda move: move.location_usage in ("internal", "transit") and 
                          move.location_dest_usage not in ("internal", "transit")
        )

    def get_in_valuations(self, valuations):
        return valuations.filtered(lambda layer: layer.quantity >= 0)
    
    def get_out_valuations(self, valuations):
        return valuations.filtered(lambda layer: layer.quantity < 0)

    def calculate_opening_data(self, opening_map, opening_in_map, opening_out_map):
        product_ids = set(opening_in_map.keys()).union(set(opening_out_map.keys()))
        for product_id in product_ids:            
            in_qty = opening_in_map.get(product_id, {}).get("quantity", 0)
            out_qty = opening_out_map.get(product_id, {}).get("quantity", 0)

            in_amount = opening_in_map.get(product_id, {}).get("value", 0)
            out_amount = opening_out_map.get(product_id, {}).get("value", 0)
            opening_qty = in_qty - out_qty
            opening_amount = in_amount + out_amount
            opening_rate = opening_amount / opening_qty if opening_qty != 0 else 0

            product_rec_obj = self.env["product.product"].browse(product_id)
            product_name = product_rec_obj.name
            product_type = product_rec_obj.type
            opening_map[product_id] = {
                "product_name": product_name,
                "product_type": product_type,
                "opening_quantity": opening_qty,
                "opening_amount": opening_amount,
                "opening_rate": opening_rate,
            }   

    def calculate_in_out_data(self, result_map, in_map, out_map):
        product_ids = set(result_map.keys()).union(set(in_map.keys())).union(set(out_map.keys()))
        
        for product_id in product_ids:
            in_qty = in_map.get(product_id, {}).get("quantity", 0)
            in_amount = in_map.get(product_id, {}).get("value", 0)
            in_rate = in_amount / in_qty if in_qty != 0 else 0

            out_qty = out_map.get(product_id, {}).get("quantity", 0)
            out_amount = out_map.get(product_id, {}).get("value", 0)
            out_rate = out_amount / out_qty if out_qty != 0 else 0

            product = self.env["product.product"].browse(product_id)
            product_name = product.name
            product_code = product.default_code
            product_type = product.type,
            product_standard_price = product.standard_price
            unit = product.uom_id.name

            if product_id in result_map:
                opening_qty = result_map[product_id].get("opening_quantity", 0)
                opening_amount = result_map[product_id].get("opening_amount", 0)
                opening_rate = result_map[product_id].get("opening_rate", 0)
            else:
                opening_qty = 0
                opening_amount = 0
                opening_rate = 0
            
            closing_qty = opening_qty + in_qty - out_qty
            closing_amt = opening_amount + in_amount + out_amount
            closing_rate = closing_amt / closing_qty if closing_qty != 0 else 0

            result_map[product_id] = {
                "product_name": product_name,
                "product_type": product_type,
                "code": product_code,
                "unit": unit,
                "opening_quantity": opening_qty,
                "opening_amount": opening_amount,
                "opening_rate": abs(opening_rate),
                "in_quantity": in_qty,
                "in_amount": in_amount,
                "in_rate": abs(in_rate),
                "out_quantity": abs(out_qty),
                "out_amount": out_amount,
                "out_rate": abs(out_rate),
                "closing_quantity": closing_qty,
                "closing_amount": closing_amt,
                "closing_rate": closing_rate,
                "product_standard_price": product_standard_price
            }

    def filter_in_moves_by_location(self, moves):
        if self.location:
            in_moves = moves.filtered(lambda move: move.location_dest_id == self.location)
            return in_moves
        return moves
    
    def filter_out_moves_by_location(self, moves):
        if self.location:
            out_moves = moves.filtered(lambda move: move.location_id == self.location)
            return out_moves
        return moves
    
    def filter_in_valuations_by_location(self, moves, valuations):
        if self.location:
            references = moves.mapped('reference')
            in_valuations = valuations.filtered(lambda valuation: valuation.reference in references)
            return in_valuations
        return valuations
    
    def filter_out_valuations_by_location(self, moves, valuations):
        if self.location:
            references = moves.mapped('reference')
            out_valuations = valuations.filtered(lambda valuation: valuation.reference in references)
            return out_valuations
        return valuations

    def group_by_product(self, moves, valuations):
        grouped_data = {}

        for move in moves:
            product_id = move.product_id.id
            product_name = move.product_id.name
            product_type = move.product_id.type
            quantity = move.product_uom_qty

            if product_id not in grouped_data:
                grouped_data[product_id] = {
                    "product_name": product_name,
                    "product_type": product_type,
                    "quantity": 0,
                    "value": 0 
                }

            grouped_data[product_id]["quantity"] += quantity

        for valuation in valuations:
            product_id = valuation.product_id.id
            value = valuation.value

            if product_id in grouped_data:
                grouped_data[product_id]["value"] += value
            else:
                grouped_data[product_id] = {
                    "product_name": valuation.product_id.name,
                    "product_type": valuation.product_id.type,
                    "quantity": 0,
                    "value": value
                }

        return grouped_data

    def get_filtered_products(self):
        if self.product_filter == "single" and self.product_ids:
            return self.product_ids.ids
        
        elif self.product_filter == "range":
            if self.from_product and self.to_product:
                from_code = int("".join(self.from_product.default_code.split("-")))
                to_code = int("".join(self.to_product.default_code.split("-")))
                start_code, end_code = sorted([from_code, to_code])
                products = self.env["product.product"].search([])
                filtered_products = products.filtered(
                    lambda p: p.default_code and start_code <= int("".join(p.default_code.split("-"))) <= end_code
                )
                return filtered_products.ids
        else:
            return None

    def get_stock_moves(self):
        """Apply various filters on stock moves based on product, category, and state."""
        domain = [("state", "=", "done")]
        product_ids = self.get_filtered_products()
        if product_ids:
            domain += [("product_id", "in", product_ids)]

        stock_moves = self.env["stock.move"].search(domain)

        if self.category_filter == "single" and self.product_category_ids:
            stock_moves = stock_moves.filtered(lambda move: move.product_id.categ_id in self.product_category_ids)

        return stock_moves

    def get_stock_valuations(self):
        """Apply various filters on stock valuations based on product and category."""
        domain = [("product_id.type","=","product")]
        product_ids = self.get_filtered_products()
        if product_ids:
            domain += [("product_id", "in", product_ids)]

        stock_valuations = self.env["stock.valuation.layer"].search(domain)
        
        if self.category_filter == "single" and self.product_category_ids:
            stock_valuations = stock_valuations.filtered(lambda layer: layer.product_id.categ_id in self.product_category_ids)

        return stock_valuations

    def remove_zero_quantity_products(self, data):
        """
        Removes products from the dataset where all quantity values are 0 
        or where closing quantity is 0.
        
        Parameters:
            data (dict): The dataset containing product information.
        
        Returns:
            dict: Filtered dataset with valid products.
        """
        filtered_data = {
            key: value for key, value in data.items()
            if not (
                value.get('opening_quantity', 0) == 0 and
                value.get('in_quantity', 0) == 0 and
                value.get('out_quantity', 0) == 0 and
                value.get('closing_quantity', 0) == 0
            ) and value.get('closing_quantity', 0) != 0
        }
        return filtered_data

    
    def remove_zero_amount_products(self, data):
        """
        Removes products from the dataset where all amount values are 0.
        
        Parameters:
            data (dict): The dataset containing product information.
        
        Returns:
            dict: Filtered dataset with non-zero amount products.
        """
        filtered_data = {
            key: value for key, value in data.items()
            if not (
                value.get('opening_amount', 0) == 0 and
                value.get('in_amount', 0) == 0 and
                value.get('out_amount', 0) == 0 and
                value.get('closing_amount', 0) == 0
            )
        }
        return filtered_data



    def get_report_data(self):
        stock_moves = self.get_stock_moves()
        stock_valuations = self.get_stock_valuations()
        data = {}

        # OPENING
        if self.date_filter == "range" and self.to_date >= self.from_date:
            opening_moves = stock_moves.filtered(lambda move: move.date.date() < self.from_date) 
            opening_valuations = stock_valuations.filtered(lambda valuation: valuation.create_date.date() < self.from_date) 

            if self.location_filter == "single":
                opening_in_moves = self.filter_in_moves_by_location(opening_moves)
                opening_out_moves = self.filter_out_moves_by_location(opening_moves)
                opening_in_valuations = self.filter_in_valuations_by_location(opening_in_moves, opening_valuations)
                opening_out_valuations = self.filter_out_valuations_by_location(opening_out_moves, opening_valuations)
                opening_in_valuations = self.get_in_valuations(opening_in_valuations)
                opening_out_valuations = self.get_out_valuations(opening_out_valuations)
            else:
                opening_in_moves = self.get_in_moves(opening_moves)
                opening_out_moves = self.get_out_moves(opening_moves)
                opening_in_valuations = self.get_in_valuations(opening_valuations)
                opening_out_valuations = self.get_out_valuations(opening_valuations)                

            opening_in_map = self.group_by_product(opening_in_moves, opening_in_valuations)
            opening_out_map = self.group_by_product(opening_out_moves, opening_out_valuations)

            self.calculate_opening_data(data, opening_in_map, opening_out_map)
        
        # IN
        if self.date_filter == "range" and self.to_date >= self.from_date:
            moves = stock_moves.filtered(lambda move: move.date.date() >= self.from_date and move.date.date() <= self.to_date) 
            valuations = stock_valuations.filtered(lambda valuation: valuation.create_date.date() >= self.from_date and valuation.create_date.date() <= self.to_date) 

            if self.location_filter == "single":
                in_moves = self.filter_in_moves_by_location(moves)
                out_moves = self.filter_out_moves_by_location(moves)
                in_valuations = self.filter_in_valuations_by_location(in_moves, valuations)
                out_valuations = self.filter_out_valuations_by_location(out_moves, valuations)
                in_valuations = self.get_in_valuations(in_valuations)
                out_valuations = self.get_out_valuations(out_valuations)
            else:
                in_moves = self.get_in_moves(moves)
                out_moves = self.get_out_moves(moves)
                in_valuations = self.get_in_valuations(valuations)
                out_valuations = self.get_out_valuations(valuations)

            in_map = self.group_by_product(in_moves, in_valuations)
            out_map = self.group_by_product(out_moves, out_valuations)

            self.calculate_in_out_data(data, in_map, out_map)
            
        if self.location_filter == 'single':
            # raise UserError(str(data))
            for i, j in data.items():
                j['opening_amount'] = j['opening_quantity'] * j['product_standard_price']
                j['opening_rate'] = j['opening_amount'] / j['opening_quantity'] if j['opening_quantity']>0 else 0
                
                j['in_amount'] = j['in_quantity'] * j['product_standard_price']
                j['in_rate'] = j['in_amount'] / j['in_quantity'] if j['in_quantity']>0 else 0
                
                j['out_amount'] = j['out_quantity'] * j['product_standard_price']
                j['out_rate'] = j['out_amount'] / j['out_quantity'] if j['out_quantity']>0 else 0
                
                j['closing_amount'] = j['closing_quantity'] * j['product_standard_price']
                j['closing_rate'] = j['closing_amount'] / j['closing_quantity'] if j['closing_quantity']>0 else 0
        # raise UserError(str(data))


        if self.with_qty == "qty_false":
            data = self.remove_zero_quantity_products(data)

        if self.with_amount == "amount_false":
            data = self.remove_zero_amount_products(data)
            
        report_data = {
            "active_model": "stock.move",
            "layout_wizard": self.id,
            "context": self.env.context,
            "products": list(data.keys()),
            "data": data,
        }

        if self.date_filter == "range":
            report_data["from_date"] = self.from_date.strftime("%d-%b-%Y")
            report_data["to_date"]   = self.to_date.strftime("%d-%b-%Y")

        if self.product_filter == "range":
            report_data["from_product"] = self.from_product.display_name
            report_data["to_product"] = self.to_product.display_name               

        return report_data
                        

    def download_report_pdf(self):
        self.ensure_one()
        data = self.get_report_data()        
        if "context" in data and isinstance(data["context"], dict):
            data["context"] = json.dumps(data["context"])
        xml_id = "custom_inventory_report_all.report_inventory_report_all_btn"        
        report_action = self.env.ref(xml_id).report_action(None, data=data, config=False)
        # report_action.update({"close_on_report_download": True})
        return report_action
    
    def download_report_excel(self):
        self.ensure_one()
        data = self.get_report_data()
        if "context" in data and isinstance(data["context"], dict):
            data["context"] = json.dumps(data["context"])        
        xml_id = "custom_inventory_report_all.action_inventory_excel_report"
        report_action = self.env.ref(xml_id).report_action(None, data=data, config=False)
        # report_action.update({"close_on_report_download": True})
        return report_action