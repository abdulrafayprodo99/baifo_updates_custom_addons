from odoo import models, fields
from odoo.http import request
import io
import base64
import xlsxwriter
from odoo.exceptions import UserError

class TaxPaymentReportWizard(models.TransientModel):
    _name = 'tax.payment.report.wizard'
    _description = 'Tax Payment Report Wizard'

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    file = fields.Binary("Excel File", readonly=True)
    filename = fields.Char("Filename", readonly=True)

    def generate_report(self):
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet("Tax Payment Receipt")
        right_align = workbook.add_format({'align': 'right'})
        bold_grey_bg = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})  # Light grey background
        right_align = workbook.add_format({'align': 'right'})

        headers = [
            'Payment','Payment Section', 'TaxPayer NTN', 'TaxPayer CNIC', 'TaxPayer Name',
            'TaxPayer City', 'TaxPayer Address', 'TaxPayer Status',
            'TaxPayer Business Name', 'Taxable Amount', 'Tax Amount'
        ]
            
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold_grey_bg)

        column_widths = [35, 35, 25, 25, 45, 10, 60, 10, 15, 10, 10]
        
        for col, width in enumerate(column_widths):
            sheet.set_column(col, col, width)

        # Domain to fetch records
        domain = [('due_date', '>=', self.date_from), ('due_date', '<=', self.date_to)]
        records = self.env['payment.wht.line'].search(domain)

        for row, rec in enumerate(records, start=1):
            partner = rec.payment_id.partner_id
            sheet.write(row, 0, rec.payment_id.name or '')
            sheet.write(row, 1, rec.tax_id.name or '')
            sheet.write(row, 2, partner.vat or '')
            sheet.write(row, 3, partner.x_studio_cnic_no or '')
            sheet.write(row, 4, partner.name or '')
            sheet.write(row, 5, partner.city or '')
            sheet.write(row, 6, partner.street or '')
            sheet.write(row, 7, partner.company_type or '')
            # sheet.write(row, 7, rec.business_name or '')
            sheet.write(row, 8, rec.total_amount or 0, right_align)
            sheet.write(row, 9, rec.amount_wht or 0, right_align)

        workbook.close()
        buffer.seek(0)
        file_data = buffer.read()
        buffer.close()

        self.write({
            'file': base64.b64encode(file_data),
            'filename': 'tax_payment_receipt.xlsx'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model={self._name}&id={self.id}&field=file&filename_field=filename&download=true",
            'target': 'self',
        }

class PaymentWHTLine(models.Model):

    _inherit = 'payment.wht.line'  # if you're extending an existing model
    file = fields.Binary("Excel File", readonly=True)
    filename = fields.Char("Filename", readonly=True)

    def action_open_tax_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Tax Excel',
            'res_model': 'tax.payment.report.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],  # ✅ This line fixes the error
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_date_from': fields.Date.today(),
                'default_date_to': fields.Date.today(),
            },
        }


    def generate_report(self):
        # Get active_ids from context (multi-record selection)
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['payment.wht.line'].browse(active_ids)

        if not records:
            raise UserError("No records selected.")

        # Use the first record to trigger the download URL
        trigger_record = records[0]

        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        sheet = workbook.add_worksheet("Tax Payment Receipt")
        right_align = workbook.add_format({'align': 'right'})
        bold_grey_bg = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})

        headers = [
            'Payment','Payment Section', 'TaxPayer NTN', 'TaxPayer CNIC', 'TaxPayer Name',
            'TaxPayer City', 'TaxPayer Address', 'TaxPayer Status',
            'TaxPayer Business Name', 'Taxable Amount', 'Tax Amount'
        ]

        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold_grey_bg)

        column_widths = [35, 35, 25, 25, 45, 10, 60, 10, 15, 10, 10]
        for col, width in enumerate(column_widths):
            sheet.set_column(col, col, width)

        for row, rec in enumerate(records, start=1):
            partner = rec.payment_id.partner_id
            sheet.write(row, 0, rec.payment_id.name or '')
            sheet.write(row, 1, rec.tax_id.name or '')
            sheet.write(row, 2, partner.vat or '')
            sheet.write(row, 3, partner.x_studio_cnic_no or '')
            sheet.write(row, 4, partner.name or '')
            sheet.write(row, 5, partner.city or '')
            sheet.write(row, 6, partner.street or '')
            sheet.write(row, 7, partner.company_type or '')
            sheet.write(row, 8, '')
            sheet.write(row, 9, rec.total_amount or 0, right_align)
            sheet.write(row, 10, rec.amount_wht or 0, right_align)

        workbook.close()
        buffer.seek(0)
        file_data = buffer.read()
        buffer.close()

        # Save file only on the first record (for triggering download)
        trigger_record.write({
            'file': base64.b64encode(file_data),
            'filename': 'tax_payment_receipt.xlsx'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model={trigger_record._name}&id={trigger_record.id}&field=file&filename_field=filename&download=true",
            'target': 'self',
        }

