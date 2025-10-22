from odoo import models, fields, api, _ # type: ignore
from datetime import datetime, timedelta
import io
import base64
import xlsxwriter # type: ignore
import json
from odoo.exceptions import UserError, ValidationError # type: ignore

class StandardRateReportWizard(models.TransientModel):
    _name = 'standard.rate.report.wizard'
    _description = 'Standard Rate Report Wizard'

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



    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_print_excel_report(self):
        # Prepare the report data
        report_data = self.prepare_bom_data()

        # Create an in-memory buffer for the Excel file
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet("Standard Rates Report")

        # Formatting
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        
        # Adjust column width
        worksheet.set_column('A:A', 20)  # Product column width
        worksheet.set_column('B:B', 30)  # Description column width
        worksheet.set_column('C:C', 15)  # Effective Date column width
        worksheet.set_column('D:D', 10)  # Unit column width
        worksheet.set_column('E:E', 15)  # Standard Rate column width

        # Adjust row height for headers and content rows
        worksheet.set_row(0, 25)  # First header row
        worksheet.set_row(1, 40)  # Second header row
        worksheet.set_row(4, 20)  # Row with Date and Time headers
        for row_num in range(5, len(report_data['rows']) + 6):
            worksheet.set_row(row_num, 20)  # Content rows

        # Add headers
        worksheet.merge_range('A1:E1', 'BIAFO INDUSTRIES LIMITED', header_format)
        worksheet.merge_range(
            'A2:E2',
            f"Standard Rates Report (BOM)\n(From Date: {report_data['header']['from_date']} To: {report_data['header']['to_date']}, Product Details: {report_data['header']['product_details']})",
            header_format
        )
        worksheet.write('A4', 'Date:', header_format)
        worksheet.write('B4', report_data['header']['current_date'], cell_format)
        worksheet.write('C4', 'Time:', header_format)
        worksheet.write('D4', report_data['header']['current_time'], cell_format)

        # Add table headers
        table_headers = ['Product', 'Description', 'Effective Date', 'Unit', 'Standard Rate']
        for col_num, header in enumerate(table_headers):
            worksheet.write(5, col_num, header, header_format)

        # Add table rows
        for row_num, row_data in enumerate(report_data['rows'], start=6):
            worksheet.write(row_num, 0, row_data['product'], cell_format)
            worksheet.write(row_num, 1, row_data['description'], cell_format)
            worksheet.write(row_num, 2, row_data['effective_date'], cell_format)
            worksheet.write(row_num, 3, row_data['unit'], cell_format)
            worksheet.write(row_num, 4, row_data['standard_rate'], cell_format)

        # Close the workbook
        workbook.close()

        # Save the buffer content as a binary field
        buffer.seek(0)
        excel_data = buffer.getvalue()
        buffer.close()

        # Save as attachment and return download link
        attachment = self.env['ir.attachment'].create({
            'name': 'Standard_Rates_Report.xlsx',
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


    def action_print_pdf_report(self):
        # Prepare data for the report
        report_data = self.prepare_bom_data()



        # raise UserError(str(report_data))

        # Trigger the report action with additional data
        return self.env.ref('ol_standard_rate_report.action_standard_rate_pdf').report_action(
            self, data={'report_data': report_data}
        )



    
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
            category_name = product_template.categ_id.name if product_template and product_template.categ_id else ""

            # Fetch and sort components based on category
            components = []
            total_component_cost = 0
            for line in record.bom_line_ids:
                component_product = line.product_id
                component_uom = line.product_uom_id
                component_category = component_product.categ_id.name if component_product and component_product.categ_id else ""


                component_cost = line.total_cost  # Extract total cost of the component
                total_component_cost += component_cost  # Sum total cost of components

                components.append({
                    'product': component_product.default_code if component_product else "N/A",
                    'description': component_product.name if component_product else "N/A",
                    'product_qty': line.product_qty,
                    'standard_rate': line.total_cost,
                    'unit': component_uom.name if component_uom else "N/A",
                    'effective_date': record.effective_date.strftime('%d/%m/%Y') if record.effective_date else "N/A",
                    'category': component_category
                })


            # raise UserError(f'{product_template.read()}{record.product_qty} {product_template.default_purchase_rate}')

            # Sorting components: Finished Good → Semi Finished Good → Work In Progress (WIP)
            category_priority = {'Finished Good': 1, 'Semi Finished Good': 2, 'Work In Progress': 3}
            components.sort(key=lambda x: category_priority.get(x['category'], 4))  # Default priority 4 for unknown categories

            bom_data.append({
                'product': product_template.default_code if product_template else "N/A",
                'description': product_template.name if product_template else "N/A",
                'effective_date': record.effective_date.strftime('%d/%m/%Y') if record.effective_date else "N/A",
                'product_qty': record.product_qty,
                'unit': product_uom.name if product_uom else "N/A",
                'standard_rate': (total_component_cost/record.product_qty),
                'category': category_name,
                # 'components': components
            })

        # Add metadata for the report header
        header_data = {
            'current_date': fields.Datetime.now().strftime('%d-%b-%Y'),
            'current_time': fields.Datetime.now().strftime('%I:%M %p'),
            'from_date': self.effective_date.strftime('%d-%b-%Y') if self.effective_date else "N/A",
            'to_date': self.effective_date.strftime('%d-%b-%Y') if self.effective_date else "N/A",
            'product_details': product_details,
        }

        return {
            'header': header_data,
            'rows': bom_data
        }



