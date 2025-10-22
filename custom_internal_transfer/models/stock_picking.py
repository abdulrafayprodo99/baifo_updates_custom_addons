from odoo import models, fields, api
from odoo.exceptions import UserError

#custom_internal_transfer

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operation_type_condition = fields.Boolean(string='Operation Type', compute='_compute_operation_type_condition')
    reciept_condition = fields.Boolean(string='Receipt', compute='_compute_reciept_condition')
    def get_analytic_distribution(self):
        if not self.purchase_id or not self.purchase_id.order_line:
            return False
            # raise UserError("Purchase order or order lines are not defined.")

        analytic_distribution_names = []
        for line in self.purchase_id.order_line:
            if not line.analytic_distribution:
                continue
            
            analytic_accounts = self.env['account.analytic.account'].search([('id', 'in', list(line.analytic_distribution.keys()))])
            for analytic_account in analytic_accounts:
                analytic_distribution_names.append(analytic_account.name)
        
        return analytic_distribution_names


    def _compute_reciept_condition(self):
        if self.picking_type_id.code == 'incoming':
            self.reciept_condition = True
        else:
            self.reciept_condition = False

    def _compute_operation_type_condition(self):
        if self.picking_type_id.code == 'internal': 
            self.operation_type_condition = True
        else:
            self.operation_type_condition = False

    def report_filter(self):

        for stock_picking in self:
            # Initialize an empty dictionary to hold the product data
            product_dict = {}
            
            # Example of iterating over move_line_nosuggest_ids (replace this with your actual iteration)
            for move_line in stock_picking.move_line_nosuggest_ids:
                products_id = move_line.product_id.id
                product_id = move_line.product_id
                prod_code = product_id.default_code
                prod_name = product_id.name
                prod_desc = move_line.description
                prod_specification = move_line.x_studio_specification
                unit = move_line.product_uom_id.name
                no_of_ctn = move_line.no_of_ctn
                qty_of_ctn = move_line.qty_in_ctn 
                qty_done = move_line.qty_done # Assuming this is the field that gives the quantity per carton
            
                # Check if the product already exists in the dictionary
                if products_id not in product_dict:
                    # If product is not in the dictionary, create an entry with the basic details
                    product_dict[products_id] = {
                        'prod_code': prod_code,
                        'prod_name': prod_name,
                        'prod_desc': prod_desc,
                        'prod_specification': prod_specification,
                        'unit': unit,
                        'quant': 0,  # Initialize quant to 0
                        'no_of_packages': 0  # Initialize no_of_packages to 0
                    }
            
                # Update quant and no_of_packages
                product_dict[products_id]['quant'] += qty_done
                product_dict[products_id]['no_of_packages'] += no_of_ctn

            return product_dict
  