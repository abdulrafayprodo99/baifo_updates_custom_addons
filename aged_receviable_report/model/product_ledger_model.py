from odoo import fields, api, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

class ProductLedgerWizard(models.TransientModel):
    _name = 'product.ledger.wizard'

    product_ids = fields.Many2many(
        string='Products',
        comodel_name='product.template',
    )
    filter_type = fields.Selection(
        [('by_date', 'By Date'), ('by_product_date', 'By Product and Date')],
        string='Filter Type',
    )

    from_product_id = fields.Selection(
        string='From Product',
        selection='select_data_for_selection'
    )
    to_product_id = fields.Selection(
        string='To Product',
        selection='select_data_for_selection'
    )

    from_date = fields.Date(
        string='From Date'
    )

    to_date = fields.Date(
        string='To Date',
        default=datetime.today()
    )

    @api.onchange('filter_type')
    def _conver_values(self):
        if self.filter_type == 'by_date':
            self.from_product_id = None
            self.to_product_id = None

    def select_data_for_selection(self):
        """Return selection data for products sorted by ID"""
        products = self.env['product.product'].search([])
        product_list=[(prod.id, f"{prod.default_code}-{prod.name}") for prod in products]
        product_list.sort(key=lambda x:x[0])    
        return product_list
    def get_sequential_data(self):
        """Get products between selected product range"""
        start = int(self.from_product_id)
        end = int(self.to_product_id)

        if end < start:
            raise UserError("The 'To Product' should be after the 'From Product'!")

        return self.env['product.product'].search([('id', '>=', start), ('id', '<=', end)])

    def get_report(self):
        till_date=self.from_date - timedelta(days=1)
    # Prepare product domain for filtering products with stock moves in a specific date range
        domain = [('state', '=', 'done')]

        # Apply the date filter if available
        if self.filter_type in ['by_date', 'by_product_date'] and self.from_date and self.to_date:
            domain += [('date', '>=', till_date), ('date', '<=', self.to_date)]

        # Fetch the relevant products based on the filter
        if not self.product_ids and not (self.from_product_id or self.to_product_id):
            products = self.env['product.product'].search([('name', 'in', self.env['stock.move'].search(domain).mapped('product_id.name'))])
        elif self.from_product_id and self.to_product_id:
            products = self.get_sequential_data().filtered(lambda p: p.name in self.env['stock.move'].search(domain).mapped('product_id.name'))
        else:
            products = self.product_ids.filtered(lambda p: p.name in self.env['stock.move'].search(domain).mapped('product_id.name'))

        product_data = {}

        grand_total_in_qty = 0
        grand_total_out_qty = 0
        grand_total_amount_in = 0
        grand_total_amount_out = 0
        grand_total_closing_balance = 0
        grand_total_closing_balance_amount = 0
        grand_total_rate = 0
        
        for product in products:
            # Modify domain to filter stock moves for the current product
            product_domain = [('product_id.name', '=', product.name), ('state', '=', 'done')]
            
            # Apply date filter if available
            if self.filter_type in ['by_date', 'by_product_date'] and self.from_date and self.to_date:
                product_domain += [('date', '>=', till_date), ('date', '<=', self.to_date)]

            stock_moves = self.env['stock.move'].search(product_domain, order="date asc")

            if not stock_moves:
                continue  # Skip products with no stock moves

            opening_balance = 0
            in_qty_total, out_qty_total = 0, 0
            moves_data = []
            total_of_each_product=[]
            
            total_in_qty = 0
            total_out_qty = 0
            total_amount_in = 0
            total_amount_out = 0
            total_closing_balance = 0
            total_closing_balance_amount = 0
            # Process stock moves for the product

            # raise UserError(str(stock_moves.read()))
            
            for move in stock_moves:
                in_qty = 0
                out_qty =0
                if move.location_id.usage == 'production':
                    in_qty = move.product_uom_qty
                elif move.location_id.usage == 'supplier' and move.location_dest_id.usage == 'internal':
                    in_qty = move.product_uom_qty
                elif move.location_id.usage == 'inventory' and move.location_dest_id.usage == 'internal':
                    in_qty = move.product_uom_qty
                # else:
                if move.location_id.usage == 'internal' and move.location_dest_id.usage == 'customer':
                    out_qty = move.product_uom_qty
                elif move.location_id.usage == 'internal' and move.location_dest_id.usage == 'inventory':
                    out_qty = move.product_uom_qty

                opening_balance = in_qty_total - out_qty_total
                closing_balance = opening_balance + in_qty - out_qty

                moves_data.append({
                    'date': move.date,
                    'reference': move.reference,
                    'product_name': move.product_id.name,
                    'location_from': move.location_id.name,
                    'location_to': move.location_dest_id.name,
                    'rate': move.price_unit,
                    'in_quantity': in_qty,
                    'amount_in': in_qty * move.price_unit,
                    'out_quantity': out_qty,
                    'out_amount': out_qty * move.price_unit,
                    'closing_amount': closing_balance,
                    'amount': move.price_unit * closing_balance
                })

                total_in_qty += in_qty
                total_out_qty += out_qty
                total_amount_in += in_qty * move.price_unit
                total_amount_out += out_qty * move.price_unit
                total_closing_balance += closing_balance
                total_closing_balance_amount += (closing_balance * move.price_unit) 
                
                in_qty_total += in_qty
                out_qty_total += out_qty
            
            total_of_each_product = {
                'total_rate': sum([move.price_unit for move in stock_moves]),
                'total_in_quantity': total_in_qty,
                'total_amount_in': total_amount_in,
                'total_out_quantity': total_out_qty,
                'total_out_amount': total_amount_out,
                'total_closing_balance': total_closing_balance,
                'total_closing_balance_amount': total_closing_balance_amount,
            }
            grand_total_in_qty += total_in_qty
            grand_total_out_qty += total_out_qty
            grand_total_amount_in += total_amount_in
            grand_total_amount_out += total_amount_out
            grand_total_closing_balance += total_closing_balance
            grand_total_closing_balance_amount += total_closing_balance_amount
            grand_total_rate += total_of_each_product['total_rate']
                
            product_data[product.id] = {
                "opening": [product.default_code, product.name, opening_balance],
                "moves": moves_data,
                "total_for_each":total_of_each_product
            }

        # Prepare the data for the report
        data = {
            'doc_ids': self.ids,
            'doc_model': 'product.ledger.wizard',
            'grouped_data': product_data,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'from_product': self.from_product_id,
            'to_product': self.to_product_id,
            'grand_total_in_qty': grand_total_in_qty,
            'grand_total_out_qty': grand_total_out_qty,
            'grand_total_amount_in': grand_total_amount_in,
            'grand_total_amount_out': grand_total_amount_out,
            'grand_total_closing_balance': grand_total_closing_balance,
            'grand_total_closing_balance_amount': grand_total_closing_balance_amount,
            'grand_total_rate': grand_total_rate 
        }
        
        # Generate the report
        return self.env.ref('aged_receviable_report.product_ledger_action').report_action(self, data=data)