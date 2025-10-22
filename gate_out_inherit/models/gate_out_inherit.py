from odoo import models, fields, api
from odoo.exceptions import UserError

#gate out inherit

class GateOutModule(models.Model):
    _inherit = "gate.out"  # Inherit from the gate.out model

    sale_id = fields.Many2one('stock.picking', string='Delivery Order No')
    @api.onchange('sale_id')
    def _onchange_all_so_line(self):
        order_line = []
        self.line_id = False  # Reset the gate.customer.line lines
        
        for record in self:
            if record.sale_id:
                # Fetch the corresponding delivery order record
                delivery_order = self.env['stock.picking'].search([('id', '=', record.sale_id.id)])
                
                if delivery_order:
                    # Populate vehicle number and seal number from the delivery order
                    record.vehicle_number = delivery_order.explosive_carrier_no 
                    record.seal_no = delivery_order.seal_no
                    record.partner_id = delivery_order.x_studio_vendor
                    
                    # Loop through each move line in the delivery order and add it to gate.customer.line
                    for move_line in delivery_order.move_line_ids_without_package:
                        order_line.append((0, 0, {
                            'product_id': move_line.product_id.id,
                            'product_uom_id': move_line.product_uom_id.id,
                            'no_of_packages': move_line.no_of_packages,
                            'qty': move_line.qty_done,
                        }))
                    
                    record.line_id = order_line  # Assign the populated lines to gate.customer.line


    def get_grouped_product_quantities(self):
        product_quantities = {}
        for rec in self:
            if rec.customer_type == 'other':
                
                for line in rec.line_ids: 
                    product_name = line.product 
                    if product_name not in product_quantities:
                        product_quantities[product_name] = {
                            'product': line.product,
                            'product_uom': line.product_uom,
                            'qty': line.qty,
                            'no_of_packages': int(str(line.no_of_packages).split('x')[0].strip()) if line.no_of_packages else 0,
                        }
                    else:
                        product_quantities[product_name]['qty'] += line.qty
                        product_quantities[product_name]['no_of_packages'] += int(str(line.no_of_packages).split('x')[0].strip()) if line.no_of_packages else 0

            elif rec.customer_type == 'customer':
                for line in rec.line_id: 
                    # product_name = line.product_id.display_name

                    product_name = line.product_id.name 
                    if product_name not in product_quantities:
                        product_quantities[product_name] = {
                            # 'product': line.product_id.display_name,
                            'product': line.product_id.name,
                            'product_code': line.product_id.default_code if hasattr(line.product_id, 'default_code') else '',
                            'product_uom': line.product_uom_id.name,
                            'qty': line.qty,
                            'no_of_packages': int(str(line.no_of_packages).split('x')[0].strip()) if line.no_of_packages else 0,
                        }
                    else:
                        product_quantities[product_name]['qty'] += line.qty
                        product_quantities[product_name]['no_of_packages'] += int(str(line.no_of_packages).split('x')[0].strip()) if line.no_of_packages else 0
            elif rec.customer_type == 'gate_in':
                for line in rec.line_id: 
                    product_name = line.product_id.name  
                    # product_name = line.product_id.display_name
                    if product_name not in product_quantities:
                        product_quantities[product_name] = {
                            'product': line.product_id.name,
                            'product_code': line.product_id.default_code if hasattr(line.product_id, 'default_code') else '',
                            # 'product': line.product_id.display_name,
                            'product_uom': line.product_uom_id.name,
                            'qty': line.qty,
                            'no_of_packages': int(str(line.no_of_packages).split('x')[0].strip()) if line.no_of_packages else 0,

                        }
                    else:
                        product_quantities[product_name]['qty'] += line.qty
                        product_quantities[product_name]['no_of_packages'] += int(str(line.no_of_packages).split('x')[0].strip()) if line.no_of_packages else 0
            else:
                pass  
        return product_quantities.values()