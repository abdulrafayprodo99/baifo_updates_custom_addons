from odoo import models, fields, api, _ # type: ignore
from datetime import datetime, timedelta
import io
import base64
import xlsxwriter # type: ignore
import json
from odoo.exceptions import UserError, ValidationError # type: ignore

class StandardRateReportWizard(models.TransientModel):
    _name = 'bom.comparison.report.wizard'
    _description = 'BOM Comparison Report Wizard'

    product_filter = fields.Selection([('all','All'),('single','Single'),('range','Range')],string="Product",default="all")
    from_product =  fields.Many2one('product.template',string="From")
    to_product = fields.Many2one('product.template',string="To")
    product_id = fields.Many2one('product.template',string="Product")
    product_ids = fields.Many2many("product.template", string="Products")
    product_domain = fields.Many2many("product.template",compute="calculate_products_domain")


    

    batches = fields.Selection(
        selection=lambda self: self._get_batch_no_selection(),
        string='Fiscal Year',
    )

    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")


    reference = fields.Many2many(
        'mrp.production',
        string="Document No.",
        domain="[('product_id.product_tmpl_id', 'in', product_ids)]"
    )
    lot_sequence_id = fields.Many2many(
        'stock.lot',
        string="Lot/ Serial Number",
        domain="[('product_id.product_tmpl_id', 'in', product_ids)]"
    )



    @api.depends('product_filter')
    def calculate_products_domain(self):
        product_tmpls = self.env['product.template'].search([])
        final_products = set()  # Use a set to prevent duplicates
        for product in product_tmpls:
            if self.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)], limit=1):
                final_products.add(product.id)
        self.product_domain = [(4, pr_id) for pr_id in final_products]

    # @api.model
    # def _get_batch_no_selection(self):
    #     # Fetch unique batch_no values from mrp.bom
    #     boms = self.env['mrp.bom'].search([('batch_no', '!=', False)])
    #     return [(str(bom.batch_no), str(bom.batch_no)) for bom in boms]

    @api.model
    def _get_batch_no_selection(self):
        # Fetch unique batch_no values from mrp.bom
        boms = self.env['mrp.bom'].search([('batch_no', '!=', False)])

        unique_batches = list(set(bom.batch_no for bom in boms))
        # raise UserError(str(unique_batches))
        return [(str(batch), str(batch)) for batch in unique_batches]


        
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
                all_products= rec.env['product.template'].search([])

                products_in_order = all_products.filtered(lambda x: x.default_code and int(''.join((x.default_code).split('-'))) >= start and int(''.join((x.default_code).split('-'))) <= end)
                    
            return products_in_order
        
    def filteration(self):
        domain = [('state', '=', 'approved')]
        
        if self.product_filter == 'single' and self.product_ids:
            domain.append(('product_tmpl_id', 'in', self.product_ids.ids))
        elif self.product_filter == 'range':
            products = self.product_search_by_range()
            domain.append(('product_tmpl_id', 'in', products.ids))
        
        if self.batches:
            domain.append(('batch_no', '=', self.batches))
        
        bom_records = self.env['mrp.bom'].search(domain)
        mos = self.env['mrp.production'].search([('bom_id', 'in', bom_records.ids)])

        
        if self.from_date and self.to_date:
            mos = mos.filtered(lambda mo: self.from_date <= mo.date_planned_start.date() <= self.to_date)
        
        if self.reference:
            mos = mos.filtered(lambda mo: mo.id in self.reference.ids)
        
        if self.lot_sequence_id:
            mos = mos.filtered(lambda mo: mo.lot_producing_id.id in self.lot_sequence_id.ids)
        
        return mos
    # OKASHA
    def calculate_bom_cost(self,mo,val_layers):
        bom_lines=mo.bom_id.bom_line_ids
        components = {}
        products=val_layers.mapped(lambda layer : layer.product_id)
        for product in products:
            bom_line=bom_lines.filtered(lambda line : line.product_id.id ==product.id)
            if bom_line:
                key=product.default_code or product.name or "N/A"
                components[key]={
                        'component_product': product.default_code or "N/A",
                        'component_description': product.name or "N/A",
                        'component_qty': bom_line.product_qty,
                        'component_amount': bom_line.default_purchase_rate,
                        'uom': product.uom_id.name or "N/A"
                    }
                
        return{
            'standard_qty':mo.bom_id.product_qty,
            'standard_amount':mo.bom_id.standard_rate,
            'components':components
        }
    # OKASHA
    
            
        
        




    def calculate_bom_cost_old(self, product):
        # raise UserError(f"{product.read()} and {product}")
        # Fetch BOM by product
        bom_by_products = self.env['mrp.bom']._bom_find(product)
        x=[i for i in bom_by_products.items()]

        # raise UserError([f"{i}-----" for i in bom_by_products.items()])
        # raise UserError(f"{bom_by_products.items()} ad----{product}")
        
        # Get the company ID from the context or default to the current company
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        
        # Get the default warehouse for the company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        
        # Get the BOM data (with context minimized to prevent excessive data fetching)
        bom_data = self.env['report.mrp.report_bom_structure'].with_context(minimized=True)._get_bom_data(bom_by_products[product], warehouse, product, ignore_stock=True)
        # raise UserError(f"{bom_data}")
        # Calculate standard quantity, standard amount, and components' data
        standard_qty = bom_data.get('quantity', 0)  # Standard quantity defined in BOM
        unit_cost = bom_data['bom_cost'] / standard_qty if standard_qty else 0  # Unit cost per product
        # Calculate standard amount (unit cost * standard quantity)
        # raise UserError(f'{bom_data.get("components")} -----{[i.read() for i in x[0]]} nad {list(bom_by_products.items())[0]}')
        standard_amount = unit_cost * standard_qty

        # Collect components' quantities and amounts using a dictionary
        components = {}
        for component in bom_data.get('components', []):  # Assuming 'components' holds the components data
            component_product = component.get('product')
            # raise UserError(f"{component_product} and {bom_data.get('components')}")
            component_qty = component.get('quantity', 0)
            # Check if the component product is available
            if component_product:
                component_cost = component.get('bom_cost', 0)  # Default to 0 if no cost is provided
                
                # Calculate component amount (quantity * cost)
                component_amount = component_qty * component_cost
                
                # Use component product code or name as the key in the dictionary
                component_key = component_product.default_code or component_product.name or "N/A"
                components[component_key] = {
                    'component_product': component_product.default_code or "N/A",
                    'component_description': component_product.name or "N/A",
                    'component_qty': component_qty,
                    'component_amount': component_amount,
                    'uom': component.get('uom_name', 'N/A')
                }
            else:
                # If no product, add a placeholder to the dictionary
                components["N/A"] = {
                    'component_product': "N/A",
                    'component_description': "No product",
                    'component_qty': component_qty,
                    'component_amount': 0,
                    'uom': "N/A"
                }
        raise UserError(f"{components}")

        return {
            'standard_qty': standard_qty,
            'standard_amount': standard_amount,
            'components': components
        }



    # def prepare_bom_data(self):
    #     # Get the filtered BOM records
    #     mos = self.filteration()
    #     bom_data = []

    #     # Collect product information based on filter
    #     product_details = ""
    #     if self.product_filter == 'single' and self.product_ids:
    #         product_details = f"{self.product_ids.default_code} ({self.product_ids.name})"
    #     elif self.product_filter == 'range' and self.from_product and self.to_product:
    #         product_details = (
    #             f"{self.from_product.default_code} ({self.from_product.name}) "
    #             f"to {self.to_product.default_code} ({self.to_product.name})"
    #         )

    #     # Initialize a dictionary to store total quantities and amounts per product
    #     product_summary = {}

    #     # Initialize a dictionary to track components' cumulative values across all MOs for each product
    #     product_components = {}

    #     for mo in mos:
    #         # Fetch product and quantity details for the main product
    #         product_template = mo.product_id.product_tmpl_id
    #         product_code = product_template.default_code if product_template else "N/A"
    #         product_name = product_template.name if product_template else "N/A"

    #         # Get standard BOM data using the calculate_bom_cost function
    #         bom_cost_data = self.calculate_bom_cost(product_template.product_variant_id)

    #         # Fetch valuation data for the main product
    #         valuation_layer = self.env['stock.valuation.layer'].search(
    #             [('reference', '=', mo.name)], 
    #             order='id asc', 
    #             limit=1
    #         )
    #         actual_amount = valuation_layer.value if valuation_layer else 0

    #         # Update the product summary with total quantity and amount for the main product
    #         if product_code not in product_summary:
    #             product_summary[product_code] = {
    #                 'description': product_name,
    #                 'total_qty': 0,
    #                 'total_amount': 0.0,
    #                 'actual_components': {},  # Dictionary to store cumulative components' data
    #                 'standard_qty': bom_cost_data['standard_qty'],  # Standard quantity
    #                 'standard_amount': bom_cost_data['standard_amount'],  # Standard amount
    #                 'standard_components': bom_cost_data['components'],  # Standard components data
    #             }

    #         product_summary[product_code]['total_qty'] += mo.product_qty
    #         product_summary[product_code]['total_amount'] += actual_amount

    #         # Fetch the components for the current MO (excluding the first valuation layer, which is the main product)
    #         valuation_layers = self.env['stock.valuation.layer'].search(
    #             [('reference', '=', mo.name)], 
    #             order='id asc'
    #         )

    #         for val_layer in valuation_layers[1:]:  # Exclude the first one (main product)
    #             component_product = val_layer.product_id
    #             component_qty = val_layer.quantity
    #             component_value = val_layer.value

    #             component_key = component_product.default_code or "N/A"

    #             # Accumulate component value across all MOs for the same product
    #             if component_key not in product_components:
    #                 product_components[component_key] = {
    #                     'component_product': component_product.default_code or "N/A",
    #                     'component_description': component_product.name or "N/A",
    #                     'component_qty': 0,
    #                     'component_value': 0.0,
    #                     'uom': "N/A",  # Assuming UOM is the same for all MOs, can modify if needed
    #                 }

    #             product_components[component_key]['component_qty'] += component_qty
    #             product_components[component_key]['component_value'] += component_value

    #     # Integrate the accumulated component values into the final BOM data
    #     for product_code, summary in product_summary.items():
    #         # Add actual components with their cumulative values across all MOs
    #         actual_components = []
    #         for component_key, component_data in product_components.items():
    #             standard_qty = summary['standard_components'].get(component_key, {}).get('component_qty', 0)
    #             standard_amount = summary['standard_components'].get(component_key, {}).get('component_amount', 0)
                
    #             # Handle zero division
    #             if standard_qty == 0:
    #                 standard_amount_actual = 0  # Default to 0 if the denominator is zero
    #             else:
    #                 standard_amount_actual = (standard_amount / standard_qty) * component_data['component_qty']
                
    #             actual_components.append({
    #                 'product_code': component_data['component_product'],
    #                 'description': component_data['component_description'],
    #                 'actual': {
    #                     'quantity': component_data['component_qty'],
    #                     'amount': component_data['component_value']
    #                 },
    #                 'standard': {
    #                     'quantity': component_data['component_qty'],
    #                     'amount': standard_amount_actual
    #                 },
    #                 'variance': {
    #                     'quantity': abs(component_data['component_qty']) - abs(component_data['component_qty']),
    #                     'amount': abs(component_data['component_value']) - abs(standard_amount_actual)
    #                 }
    #             })

    #         # Handle zero division for standard_amount_actual_comp
    #         if summary['standard_qty'] == 0:
    #             standard_amount_actual_comp = 0  # Default to 0 if the denominator is zero
    #         else:
    #             standard_amount_actual_comp = (summary['standard_amount'] / summary['standard_qty']) * summary['total_qty']

    #         bom_data.append({
    #             'product_code': product_code,  # Product code
    #             'bom': "BOM-Placeholder",  # Placeholder for BOM code
    #             'description': summary['description'],  # Product description
    #             'production': [{
    #                 'product_code': product_code,
    #                 'description': summary['description'],
    #                 'actual': {
    #                     'quantity': summary['total_qty'],
    #                     'amount': summary['total_amount']
    #                 },
    #                 'standard': {
    #                     'quantity': summary['total_qty'],
    #                     'amount': standard_amount_actual_comp
    #                 },
    #                 'variance': {
    #                     'quantity': abs(summary['total_qty']) - abs(summary['total_qty']),
    #                     'amount': abs(summary['total_amount']) - abs(standard_amount_actual_comp)
    #                 }
    #             }],
    #             'consumption': actual_components
    #         })


    #     # Calculate totals
    #     total_actual_qty = sum(item['production'][0]['actual']['quantity'] for item in bom_data)
    #     total_actual_amount = sum(item['production'][0]['actual']['amount'] for item in bom_data)
    #     total_standard_qty = sum(item['production'][0]['standard']['quantity'] for item in bom_data)
    #     total_standard_amount = sum(item['production'][0]['standard']['amount'] for item in bom_data)



    #     # Add metadata for the report header
    #     current_datetime = fields.Datetime.now()

    #     header_data = {
    #         'title': "Biafo Industries Limited BOM Comparison Summary Report",
    #         'date': current_datetime.strftime('%d-%b-%Y'),
    #         'time': current_datetime.strftime('%I:%M %p'),
    #         'period': f"{self.from_date.strftime('%d-%b-%Y') if self.from_date else 'N/A'} To {self.to_date.strftime('%d-%b-%Y') if self.to_date else 'N/A'}",
    #     }

    #     return {
    #         'report': {
    #             'title': header_data['title'],
    #             'date': header_data['date'],
    #             'time': header_data['time'],
    #             'period': header_data['period'],
    #             'products': bom_data,
    #             'totals': {
    #                 'actual': {
    #                     'quantity': total_actual_qty,
    #                     'amount': total_actual_amount
    #                 },
    #                 'standard': {
    #                     'quantity': total_standard_qty,
    #                     'amount': total_standard_amount
    #                 },
    #                 'variance': {
    #                     'quantity': abs(total_actual_qty) - abs(total_standard_qty),
    #                     'amount': abs(total_actual_amount) - abs(total_standard_amount)
    #                 }
    #             }
    #         }
    #     }



    def prepare_bom_data(self):
        mos = self.filteration()

        bom_data = []
        product_details = ""

        if self.product_filter == 'single' and self.product_ids:
            product_details = f"{self.product_ids.default_code} ({self.product_ids.name})"
        elif self.product_filter == 'range' and self.from_product and self.to_product:
            product_details = (
                f"{self.from_product.default_code} ({self.from_product.name}) "
                f"to {self.to_product.default_code} ({self.to_product.name})"
            )

        product_summary = {}
        product_components = {}

        for mo in mos:
            # raise UserError(f"{mo.product_id} and {mo.product_id.product_tmpl_id} and {mo.product_id.product_tmpl_id.product_variant_id}")
            product_template = mo.product_id.product_tmpl_id
            product_code = product_template.default_code if product_template else "N/A"
            product_name = product_template.name if product_template else "N/A"
            # raise UserError(f"{product_template} and {product_template.read()}")
            # raise UserError(f"{product_template} and {product_template.read()} {product_template.variant_id}")
            valuation_layers = self.env['stock.valuation.layer'].search(
                [('reference', '=', mo.name)], order='id asc'
            )

            # bom_cost_data = self.calculate_bom_cost_old(product_template.product_variant_id) #OLD CODE ()
            bom_cost_data = self.calculate_bom_cost(mo,valuation_layers)
            valuation_layer = self.env['stock.valuation.layer'].search(
                [('reference', '=', mo.name)], order='id asc', limit=1
            )
            finished_good=valuation_layers.filtered(lambda layer : layer.product_id.id == mo.product_id.id)
            actual_amount=finished_good.value
            # actual_amount = valuation_layer.value if valuation_layer else 0

            if product_code not in product_summary:
                product_summary[product_code] = {
                    'description': product_name,
                    'total_qty': 0,
                    'total_amount': 0.0,
                    'actual_components': {},
                    'standard_qty': bom_cost_data['standard_qty'],
                    'standard_amount': bom_cost_data['standard_amount'],
                    'standard_components': bom_cost_data['components'],
                }

            product_summary[product_code]['total_qty'] += mo.product_qty
            # product_summary[product_code]['total_amount'] += actual_amount
            product_summary[product_code]['total_amount'] += actual_amount

            # raise UserError(f"{product_summary}")
            # raise UserError(f"{[i.product_id.name for i in valuation_layers[1:]]} and {[i.product_id.name for i in valuation_layers]}")
            

            for val_layer in valuation_layers:
                if val_layer.product_id.id !=mo.product_id.id:
                    component_product = val_layer.product_id
                    component_qty = val_layer.quantity
                    component_value = val_layer.value
                    component_key = component_product.default_code or "N/A"

                    if component_key not in product_components:
                        product_components[component_key] = {
                            'component_product': component_product.default_code or "N/A",
                            'component_description': component_product.name or "N/A",
                            'component_qty': 0,
                            'component_value': 0.0,
                            'uom': "N/A",
                        }

                    product_components[component_key]['component_qty'] += component_qty
                    product_components[component_key]['component_value'] += component_value
    

        # raise UserError(f"{product_summary} and {product_components}")

        for product_code, summary in product_summary.items():
            actual_components = []
            for component_key, component_data in product_components.items():
                standard_qty = summary['standard_components'].get(component_key, {}).get('component_qty', 0)
                standard_amount = summary['standard_components'].get(component_key, {}).get('component_amount', 0)
                # standard_amount_actual = (standard_amount / standard_qty) * component_data['component_qty'] if standard_qty else 0
                standard_amount_actual = standard_amount * standard_qty/summary['standard_qty']*summary['total_qty']
                # standard_qty_check = summary['standard_components'].get(component_key, {}).get('standard_qty', 0)
                # raise UserError(f"{standard_qty} and { component_data['component_qty']} ")
                # raise UserError(f"{standard_qty/summary['standard_qty']*summary['total_qty']} and {standard_amount}  {component_key}")
            


                actual_components.append({
                    'product_code': component_data['component_product'],
                    'description': component_data['component_description'],
                    'actual': {
                        'quantity': component_data['component_qty'],
                        'amount': component_data['component_value']
                    },
                    'standard': {
                        #OKASHA
                        # 'quantity': component_data['component_qty'],
                        'quantity': standard_qty/summary['standard_qty']*summary['total_qty'],
                        #OKASHA
                        'amount': standard_amount * standard_qty/summary['standard_qty']*summary['total_qty']
                    },
                    'variance': {
                        # 'quantity': abs(component_data['component_qty']) - abs(component_data['component_qty']),
                        # 'quantity': abs(component_data['component_qty']) - abs( standard_qty/summary['standard_qty']*summary['total_qty']),
                        'quantity': abs(standard_qty/summary['standard_qty']*summary['total_qty']) - abs( component_data['component_qty']),
                        # 'amount': abs(component_data['component_value']) - abs(standard_amount_actual)
                        'amount': abs(standard_amount_actual) - abs(component_data['component_value'])
                    }
                })
            
            # Sorting the consumption components
            actual_components.sort(key=lambda x: ("[SFG]" not in x['description'], "[Packing]" in x['description']))
            standard_amount_actual_comp = (summary['standard_amount'] / summary['standard_qty']) * summary['total_qty'] if summary['standard_qty'] else 0


            bom_data.append({
                'product_code': product_code,
                'bom': "BOM-Placeholder",
                'description': summary['description'],
                'production': [{
                    'product_code': product_code,
                    'description': summary['description'],
                    'actual': {
                        'quantity': summary['total_qty'],
                        'amount': summary['total_amount']
                    },
                    'standard': {
                        'quantity': summary['total_qty'],
                        # 'quantity': summary['component_qty'],
                        # 'amount': standard_amount_actual_comp
                        'amount': summary['total_qty']*summary['standard_amount']
                    },
                    'variance': {
                        'quantity': abs(summary['total_qty']) - abs(summary['total_qty']),
                        # 'amount': abs(summary['total_amount']) - abs(standard_amount_actual_comp),
                        'amount': abs(summary['total_qty']*summary['standard_amount']) - abs(summary['total_amount'])
                    }
                }],
                'consumption': actual_components
            })
            # raise UserError(f"{actual_components} and {summary.keys()}")

        # raise UserError(f"{bom_data} and {product_summary} and {product_components}")

        total_actual_qty = sum(item['production'][0]['actual']['quantity'] for item in bom_data)
        total_actual_amount = sum(item['production'][0]['actual']['amount'] for item in bom_data)
        total_standard_qty = sum(item['production'][0]['standard']['quantity'] for item in bom_data)
        total_standard_amount = sum(item['production'][0]['standard']['amount'] for item in bom_data)

        current_datetime = fields.Datetime.now()

        header_data = {
            'title': "Biafo Industries Limited BOM Comparison Summary Report",
            'date': current_datetime.strftime('%d-%b-%Y'),
            'time': current_datetime.strftime('%I:%M %p'),
            'period': f"From {self.from_date.strftime('%d-%b-%Y') if self.from_date else 'N/A'} To {self.to_date.strftime('%d-%b-%Y') if self.to_date else 'N/A'}",
        }

        if self.product_ids:
            products = ', '.join(f"[{p.default_code}] {p.name}" for p in self.product_ids if p.default_code)
            product_desc = f"For {products}"
        elif self.from_product and self.to_product:
            from_text = f"[{self.from_product.default_code}] {self.from_product.name}" if self.from_product.default_code else self.from_product.name
            to_text = f"[{self.to_product.default_code}] {self.to_product.name}" if self.to_product.default_code else self.to_product.name
            product_desc = f"From {from_text} To {to_text}"
        else:
            product_desc = ''

        return {
            'report': {
                'title': header_data['title'],
                'date': header_data['date'],
                'time': header_data['time'],
                'product_desc' :product_desc,
                'period': header_data['period'],
                'products': bom_data,
                'totals': {
                    'actual': {'quantity': total_actual_qty, 'amount': total_actual_amount},
                    'standard': {'quantity': total_standard_qty, 'amount': total_standard_amount},
                    'variance': {
                        # 'quantity': abs(total_actual_qty) - abs(total_standard_qty),
                        'quantity': abs(total_standard_qty) - abs(total_actual_qty),
                        # 'amount': abs(total_actual_amount) - abs(total_standard_amount),
                        'amount': abs(total_standard_amount) - abs(total_actual_amount),
                    }
                }
            }
        }





    def action_print_excel_report(self):
        report_data = self.prepare_bom_data()  # Prepare data for BOM comparison
        data = report_data.get("report")
        
        # Create an in-memory buffer
        buffer = io.BytesIO()

        # Create a workbook and add a worksheet
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # Define formatting
        title_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        data_format = workbook.add_format({'border': 1, 'align': 'center'})

        # Write Title and Header Information
        worksheet.merge_range('A1:H1', 'Biafo Industries Limited BOM Comparison Summary Report', title_format)
        worksheet.write('H2', f"Date: {data.get('date')}", data_format)
        worksheet.write('H3', f"Time: {data.get('time')}", data_format)
        worksheet.write('A3', f"Period: {data.get('period')}", data_format)

        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)

        # Write headers for Production and Consumption
        worksheet.write('A5', 'Product Code', header_format)
        worksheet.write('B5', 'Description', header_format)
        worksheet.write('C5', 'Actual Quantity', header_format)
        worksheet.write('D5', 'Actual Amount', header_format)
        worksheet.write('E5', 'Standard Quantity', header_format)
        worksheet.write('F5', 'Standard Amount', header_format)
        worksheet.write('G5', 'Variance Quantity', header_format)
        worksheet.write('H5', 'Variance Amount', header_format)

        row = 5  # Start row for data

        # Write product data
        for product in data.get('products', []):
            # Write Product Details
            worksheet.merge_range(row, 0, row, 7, f"Product: {product['description']} ({product['product_code']}) - {product['bom']}", header_format)
            row += 1

            # Write Production Data
            worksheet.write(row, 0, 'Production', header_format)
            for prod in product.get('production', []):
                row += 1
                worksheet.write(row, 0, prod['product_code'], data_format)
                worksheet.write(row, 1, prod['description'], data_format)
                worksheet.write(row, 2, prod['actual']['quantity'], data_format)
                worksheet.write(row, 3, prod['actual']['amount'], data_format)
                worksheet.write(row, 4, prod['standard']['quantity'], data_format)
                worksheet.write(row, 5, prod['standard']['amount'], data_format)
                worksheet.write(row, 6, prod['variance']['quantity'], data_format)
                worksheet.write(row, 7, prod['variance']['amount'], data_format)

            # Write Consumption Data
            row += 1
            worksheet.write(row, 0, 'Consumption', header_format)
            for cons in product.get('consumption', []):
                row += 1
                worksheet.write(row, 0, cons['product_code'], data_format)
                worksheet.write(row, 1, cons['description'], data_format)
                worksheet.write(row, 2, cons['actual']['quantity'], data_format)
                worksheet.write(row, 3, cons['actual']['amount'], data_format)
                worksheet.write(row, 4, cons['standard']['quantity'], data_format)
                worksheet.write(row, 5, cons['standard']['amount'], data_format)
                worksheet.write(row, 6, cons['variance']['quantity'], data_format)
                worksheet.write(row, 7, cons['variance']['amount'], data_format)
            row += 2

        # Close the workbook to finalize the data
        workbook.close()

        # Save the buffer content as binary data
        buffer.seek(0)
        excel_data = buffer.getvalue()
        buffer.close()

        # Save as attachment and return download link
        attachment = self.env['ir.attachment'].create({
            'name': 'bom_comparison_report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(excel_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }




    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_print_pdf_report(self):
        report_data = self.prepare_bom_data()
        # raise UserError(f"{report_data}")

        data = report_data.get("report")
        return self.env.ref('ol_bom_comparison_report.action_bom_comparison_pdf').report_action(
            self, data={'report_data': data}
        )
    