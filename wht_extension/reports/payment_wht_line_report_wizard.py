from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import io
from num2words import num2words
import base64
# import xlsxwriter
from datetime import date, datetime


class PaymentWhtLineReportWizard(models.TransientModel):
    _name = 'payment.wht.line.report.wizard'
    _description = 'Wizard to generate payment report'

    partner_id = fields.Many2one('res.partner', string="Partner")
    issue_date = fields.Date(string="Issue Date")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    serial_no = fields.Char(string='Serial No')
    duplicate = fields.Boolean(string='Duplicate')
    saved_report_id = fields.Many2one('payment.wht.line.report', string="Select Saved Report")

    @api.onchange('duplicate')
    def _onchange_duplicate(self):
        if self.duplicate:
            self.partner_id = False
            self.issue_date = False
            self.from_date = False
            self.to_date = False
        else:
            self.saved_report_id = False

    @api.onchange('saved_report_id')
    def _onchange_saved_report(self):
        if self.duplicate and self.saved_report_id:
            data = self.saved_report_id.report_data
            self.serial_no = self.saved_report_id.serial_no
            self.partner_id = self.saved_report_id.partner_id.id
            self.issue_date = self.saved_report_id.issue_date
            self.from_date = self.saved_report_id.from_date
            self.to_date = self.saved_report_id.to_date




    def amount_in_words(self, amount):
        try:
            # Convert to float to handle decimal values
            amount = float(amount)
            
            # Split into whole number and decimal part
            whole = int(amount)
            decimal = int(round((amount - whole) * 100))

            # Convert to words
            words = num2words(whole).title() + " Rupees"
            if decimal > 0:
                words += " and " + num2words(decimal).title() + " Paisa"
            words += " Only"
            
            return words
        except Exception as e:
            return f"Error: {e}"


    def prepare_payments_data(self):
        self.ensure_one()
        partner = self.partner_id
        issue_date = self.issue_date
        from_date = self.from_date
        to_date = self.to_date
        serial_no = self.serial_no
        duplicate = self.duplicate

        payments_wht_lines = self.env['payment.wht.line'].search([
            ('payment_id.partner_id', '=', partner.id),
            ('tax_date', '>=', from_date),
            ('tax_date', '<=', to_date),
        ])

        # Summary values
        sum_of_tax_amount = sum(line.amount_wht for line in payments_wht_lines)
        value_amount = sum(line.total_amount for line in payments_wht_lines)

        vendor_name = partner.name
        # address = partner.contact_address or partner.street or ''
        address =partner.street or ''
        # raise UserError(f"address{address}")
        cnic_no = partner.x_studio_cnic_no or '' 
        vendor_ntn = partner.vat or ''
        # vendor_ntn = partner.x_studio_ntn
        under_section=""
        account_of=""
        if payments_wht_lines and payments_wht_lines[0].tax_id:
            under_section = payments_wht_lines[0].tax_id.name
            account_of = payments_wht_lines[0].tax_id.description or ''


        payment_details = []
        for line in payments_wht_lines:
            payment = line.payment_id
            payment_details.append({
                'tax_date': line.tax_date,
                'bank_name': line.bank_name or '', 
                'branch': line.branch or '',     
                'amount_tax': line.amount_wht,
                'cprm_no': line.cprm_no or '',      
            })
        company_info = {
            'name': "BIAFO INDUSTRIES LTD",
            'address': "1st Floor, Biafo House, Plot No. 23, Street 38-40,\nI & T Center, G/10-4, Islamabad, Pakistan.",
            'ntn': "0656570-7",
            'report_date': "13-Aug-2024",
            'signatory_name': "Syed Sajid Hussain Shah",
            'signatory_designation': "Chief Financial Officer",
            'signatory_company': "Biafo Industries Limited",
            'signatory_image': "/your_module_name/static/src/img/signature.png",  
        }
        

        data = {
                'serial_no': serial_no,
                'partner_name': vendor_name,
                'address': address,
                'ntn': vendor_ntn,
                'cnic_no': cnic_no,
                'from_date': from_date,
                'to_date': to_date,
                'issue_date': issue_date,
                'sum_of_tax_amount': sum_of_tax_amount,
                'sum_of_tax_amount_words': self.amount_in_words(sum_of_tax_amount),
                'value_amount': value_amount,
                'value_amount_words': self.amount_in_words(value_amount),
                'under_section': under_section,
                'account_of': account_of,
                'payment_details': payment_details,
                'company_info': company_info,
                'duplicate': duplicate
            }

        return data
        

            

    def action_generate_report(self):
        def serialize_dates(obj):
            if isinstance(obj, dict):
                return {k: serialize_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_dates(i) for i in obj]
            elif isinstance(obj, (date, datetime)):
                return obj.isoformat()
            else:
                return obj

        self.ensure_one()
        if self.duplicate and self.saved_report_id:
            report_data = self.saved_report_id.report_data
        else:
            raw_data = self.prepare_payments_data()
            report_data = serialize_dates(raw_data)  # 👈 Fix applied here

            # Save new record
            self.env['payment.wht.line.report'].create({
                'serial_no': self.serial_no or self._get_next_serial_no(),
                'partner_id': self.partner_id.id,
                'issue_date': self.issue_date,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'report_data': report_data
            })

        return self.env.ref('wht_extension.report_payment_wht_line').report_action(
            self, data={'report_data': report_data, 'duplicate':self.duplicate}
        )







class PaymentWhtLineReport(models.Model):
    _name = 'payment.wht.line.report'
    _description = 'Saved Payment WHT Reports'

    serial_no = fields.Char(string='Serial No', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    issue_date = fields.Date(string="Issue Date")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    report_data = fields.Json(string="Report Data", default={})

    def name_get(self):
        result = []
        for record in self:
            name = record.serial_no or 'Unnamed Report'  # Show serial_no or a default name
            result.append((record.id, name))
        return result






class PaymentWHTLine(models.Model):

    _inherit = 'payment.wht.line'  # if you're extending an existing model

    def action_open_certificate_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Certificate',
            'res_model': 'payment.wht.line.report.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],  # ✅ This line fixes the error
            'view_type': 'form',
            'target': 'new',
            'context': {
                # 'default_date_from': fields.Date.today(),
                # 'default_date_to': fields.Date.today(),
            },
        }