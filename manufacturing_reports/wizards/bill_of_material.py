from odoo import models, fields, api
from odoo.exceptions import UserError

class BillOfMaterialWizard(models.TransientModel):
    _name = 'bill.of.material.wizard'
    _description = 'Bill of Material Report Wizard'

    product_filter = fields.Selection([('all','All'),('single','Single'),('range','Range')],string="Product",default="all")
    from_product =  fields.Many2one('product.template',string="From")
    to_product = fields.Many2one('product.template',string="To")
    product_id = fields.Many2one('product.template',string="Product")
    product_ids = fields.Many2many("product.template", string="Products")
    product_domain = fields.Many2many("product.template",compute="calculate_products_domain")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    effective_date =  fields.Date(string="Date")

    batches = fields.Selection(
        selection=lambda self: self._get_batch_no_selection(),
        string='Batch No',
    )

    @api.depends('product_filter')
    def calculate_products_domain(self):
        self.product_domain = self.product_domain
        if not self.product_domain:
            product_tmpls = self.env['product.template'].search([])
            final_products=[]
            for product in product_tmpls:
                if self.env['mrp.bom'].search([('product_tmpl_id','=',product.id)],limit=1):
                    final_products.append(product)
            self.product_domain=[(4,pr.id) for pr in final_products]

    @api.model
    def _get_batch_no_selection(self):
        # Fetch unique batch_no values from mrp.bom
        boms = self.env['mrp.bom'].search([('batch_no', '!=', False)])
        unique_batches = {bom.batch_no for bom in boms}  # Using a set to ensure uniqueness
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
        if self.product_filter == 'all':
            domain = []
        elif self.product_filter == 'single' and self.product_ids:
            domain = [('product_tmpl_id','in',self.product_ids.ids)]
        elif self.product_filter == 'range':
            products = self.product_search_by_range()
            domain = [('product_tmpl_id','in',products.ids)]
        if self.batches:
            domain += [('batch_no','=',self.batches)]
        if self.effective_date:
            domain += [('effective_date','<=',self.effective_date)]

        domain += [('state', '=', 'approved')]

        bom_records =  self.env['mrp.bom'].search(domain)
        return bom_records

    def calculate_bom_cost(self,product):
        bom_by_products = self.env['mrp.bom']._bom_find(product)
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        bom_data = self.env['report.mrp.report_bom_structure'].with_context(minimized=True)._get_bom_data(bom_by_products[product], warehouse, product, ignore_stock=True)
        return bom_data['bom_cost']

    # def prepare_bom_data(self):
    #     bom_records = self.filteration()  # Get the filtered BOM records
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

    #     for record in bom_records:
    #         product_template = record.product_tmpl_id
    #         product_uom = record.product_uom_id
    #         category_name = product_template.level_2_cat if product_template and product_template.level_2_cat else ""

    #         # Fetch and sort components based on category
    #         components = []
    #         for line in record.bom_line_ids:
    #             component_product = line.product_id
    #             component_uom = line.product_uom_id
    #             component_category = component_product.level_2_cat if component_product and component_product.level_2_cat else ""

    #             components.append( component_category :[ {
    #                 'product': component_product.default_code if component_product else "N/A",
    #                 'description': component_product.name if component_product else "N/A",
    #                 'product_qty': line.product_qty,
    #                 'standard_rate': line.total_cost,
    #                 'unit': component_uom.name if component_uom else "N/A",
    #                 'effective_date': record.effective_date.strftime('%d/%m/%Y') if record.effective_date else "N/A",
    #                 'category': component_category
    #             }],)

    #         # raise UserError(f'{product_template.read()}{record.product_qty} {product_template.default_purchase_rate}')

    #         # Sorting components: Finished Good → Semi Finished Good → Work In Progress (WIP)
    #         category_priority = {'Finished Goods': 1, 'Semi Finished Goods': 2, 'Work In Process': 3}
    #         components.sort(key=lambda x: category_priority.get(x['category'], 4))  # Default priority 4 for unknown categories

    #         bom_data.append({
    #             'product': product_template.default_code if product_template else "N/A",
    #             'description': product_template.name if product_template else "N/A",
    #             'effective_date': record.effective_date.strftime('%d/%m/%Y') if record.effective_date else "N/A",
    #             'product_qty': record.product_qty,
    #             'unit': product_uom.name if product_uom else "N/A",
    #             'standard_rate': record.product_qty * product_template.default_purchase_rate,
    #             'category': category_name,
    #             'components': components,
    #             'batch_no': record.batch_no,
    #             'status': record.state_display
    #         })

    #         #raise UserError(str(bom_data))



    #     # Add metadata for the report header
    #     header_data = {
    #         'current_date': fields.Datetime.now().strftime('%d-%b-%Y'),
    #         'current_time': fields.Datetime.now().strftime('%I:%M %p'),
    #         'from_date': self.effective_date.strftime('%d-%b-%Y') if self.effective_date else "N/A",
    #         'to_date': self.effective_date.strftime('%d-%b-%Y') if self.effective_date else "N/A",
    #         'product_details': product_details,
    #     }



    #     #raise UserError(str(bom_data))
    #     return {
    #         'header': header_data,
    #         'rows': bom_data
    #     }

    def prepare_bom_data(self):
        bom_records = self.filteration()  # Get the filtered BOM records
        bom_data = []

        # Collect product information based on filter
        product_details = ""
        if self.product_filter == 'single' and self.product_ids:
            product_details = f"{self.product_ids.default_code} ({self.product_ids.name})"
        elif self.product_filter == 'range' and self.from_product and self.to_product:
            product_details = (
                f"{self.from_product.default_code} ({self.from_product.name}) "
                f"to {self.to_product.default_code} ({self.to_product.name})"
            )

        for record in bom_records:
            product_template = record.product_tmpl_id
            product_uom = record.product_uom_id
            category_name = product_template.level_2_cat if product_template and product_template.level_2_cat else ""

            # Fetch and group components by category
            components = {}
            for line in record.bom_line_ids:
                component_product = line.product_id
                component_uom = line.product_uom_id
                component_category = component_product.level_2_cat if component_product and component_product.level_2_cat else "Uncategorized"

                component_data = {
                    'product': component_product.default_code if component_product else "N/A",
                    'description': component_product.name if component_product else "N/A",
                    'product_qty': line.product_qty,
                    'standard_rate': line.default_purchase_rate,
                    'unit': component_uom.name if component_uom else "N/A",
                    'effective_date': record.effective_date.strftime('%d/%m/%Y') if record.effective_date else "N/A",
                    'category': component_category
                }

                # Append component data under the correct category
                if component_category in components:
                    components[component_category].append(component_data)
                else:
                    components[component_category] = [component_data]

            # Convert to a list for proper sorting
            components_list = [{'category': k, 'components': v} for k, v in components.items()]

            # Sorting components: Finished Good → Semi Finished Good → Work In Progress (WIP)
            category_priority = {'Finished Goods': 1, 'Semi Finished Goods': 2, 'Work In Process': 3}
            components_list.sort(key=lambda x: category_priority.get(x['category'], 4))  # Default priority 4 for unknown categories

            # Prepare BOM data entry
            bom_data.append({
                'product': product_template.default_code if product_template else "N/A",
                'description': product_template.name if product_template else "N/A",
                'effective_date': record.effective_date if record.effective_date else "N/A",
                'product_qty': record.product_qty,
                'unit': product_uom.name if product_uom else "N/A",
                'standard_rate': record.standard_rate,
                'category': category_name,
                'components': components_list,
                'batch_no': record.batch_no,
                'status': record.state_display,
                'sequence':record.sequence,
                'bom_version':record.code,
                "bom_version_id":record.bom_version_id,
                'end_date':record.end_date
            })

        # Prepare header metadata for the report
        header_data = {
            'current_date': fields.Datetime.now().strftime('%d-%b-%Y'),
            'current_time': fields.Datetime.now().strftime('%I:%M %p'),
            'from_date': self.effective_date.strftime('%d-%b-%Y') if self.effective_date else "N/A",
            'to_date': self.effective_date.strftime('%d-%b-%Y') if self.effective_date else "N/A",
            'product_details': product_details,
        }
        #raise UserError(str(bom_data))
        return {
            'header': header_data,
            'rows': bom_data
        }



    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}



    def action_print_pdf_report(self):
        """Generate the BOM report."""
        report_data = self.prepare_bom_data()
        return self.env.ref('manufacturing_reports.action_bill_of_material_pdf').report_action(
            self, data={'report_data': report_data}
        )
