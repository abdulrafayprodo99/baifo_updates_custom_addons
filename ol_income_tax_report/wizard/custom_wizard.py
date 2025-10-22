
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
# from odoo.exceptions import UserError
from datetime import datetime
import re
import xlsxwriter
from dateutil import rrule
from datetime import datetime
import calendar

_
from odoo.exceptions import UserError


import base64

import io
try:
    import xlwt
except ImportError:
    xlwt = None

class TaxReportWizard(models.TransientModel):
    _name="tax.report.wizard"
    _description='Tax Report Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_ids = fields.Many2many('hr.employee',string='Employee')

    @api.onchange('date_from', 'date_to')
    def check_dates(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_("The 'Date To' must be greater than or equal to the 'Date From'."))
    
    def get_employee_data(self):
        _domain=[]
        if self.date_from and self.date_to:
            _domain.append(('date_from', '>=', self.date_from))
            _domain.append(('date_from', '<=', self.date_to))
            _domain.append(('state', 'in', ['done','paid']))

        if self.employee_ids:
            _domain.append(('employee_id.id', 'in', self.employee_ids.ids))


        payslips_record = self.env['hr.payslip'].search(_domain)
        # raise UserError(payslips_record)

        rows = []
        employee_data = {}

        if payslips_record:
            for rec in payslips_record:
                payment_section = '149/4'  # FIX
                employee_id = rec.employee_id.id  # Use employee_id as the key for grouping
                ntn = rec.employee_id.related_contact_ids[0].vat if rec.employee_id.related_contact_ids and rec.employee_id.related_contact_ids[0].vat else '' 
                # cnic = rec.employee_id.related_contact_ids[0].x_studio_cnic_no if rec.employee_id.related_contact_ids and rec.employee_id.related_contact_ids[0].x_studio_cnic_no else ''
                cnic = rec.employee_id.identification_id if rec.employee_id.identification_id else ''
                tax_payer_name = rec.employee_id.name
                tax_payer_city = rec.employee_id.related_contact_ids[0].city if rec.employee_id.related_contact_ids and rec.employee_id.related_contact_ids[0].city else ''
                # tax_payer_address = f'{rec.employee_id.related_contact_ids[0].street} {rec.employee_id.related_contact_ids[0].country_id.name}'
                if rec.employee_id.related_contact_ids:
                    related_contact = rec.employee_id.related_contact_ids[0]
                    street = related_contact.street if related_contact.street else ""
                    country = related_contact.country_id.name if related_contact.country_id else ""
                    tax_payer_address = f"{street} {country}".strip()
                else:
                    tax_payer_address = ""
                tax_payer_status = 'INDIVIDUAL'  # FIX
                tax_payer_business_name = rec.employee_id.name
                taxable_amount = 0  
                tax_amount = 0

                # Calculate tax_amount for the current record
                for line in rec.line_ids:
                    if line.name == 'Income Tax':
                        tax_amount += abs(line.total)

                # If employee_id is already in the dictionary, add to the tax_amount
                if employee_id in employee_data:
                    employee_data[employee_id]["taxable_amount"] += rec.contract_id.wage
                    employee_data[employee_id]["tax_amount"] += tax_amount
                else:
                    # Create a new entry for this employee
                    employee_data[employee_id] = {
                        "payment_section": payment_section,
                        "ntn": ntn,
                        "cnic": cnic,
                        "tax_payer_name": tax_payer_name,
                        "tax_payer_city": tax_payer_city,
                        "tax_payer_address": tax_payer_address,
                        "tax_payer_status": tax_payer_status,
                        "tax_payer_business_name": tax_payer_business_name,
                        "taxable_amount": rec.contract_id.wage,
                        "tax_amount": tax_amount,
                    }

            # Convert the dictionary back to a list of rows
            for data in employee_data.values():
                row = [
                    data["payment_section"],
                    data["ntn"],
                    data["cnic"],
                    data["tax_payer_name"],
                    data["tax_payer_city"],
                    data["tax_payer_address"],
                    data["tax_payer_status"],
                    data["tax_payer_business_name"],
                    data["taxable_amount"],
                    data["tax_amount"],
                ]
                rows.append(row)

            return rows
        else:
            return False

    
    def action_print_excel_report(self):

        # if self.date_from and self.date_to and self.date_from > self.date_to:
        #     raise ValidationError(_("The 'Date To' must be greater than or equal to the 'Date From'."))
        
        datas=self.get_employee_data()
        if not datas:
            raise UserError("No data found!")

        excel_encode = io.BytesIO()
  
        filename = "Income Tax Report - " + str(datetime.now().strftime("%d-%m-%Y"))+".xlsx"
        workbook = xlsxwriter.Workbook(excel_encode)
        sheet = workbook.add_worksheet('Income Tax Report')
        header = workbook.add_format({'bold': True, 'align':'center','size': 11,})
        heading = workbook.add_format({'bold': True, 'align':'center','size': 24})
        header.set_border()
        normal_text = workbook.add_format({'align':'center','size':11})
        int_normal_text = workbook.add_format({'align':'right','size':11})
        txt_normal_text = workbook.add_format({'align':'left','size':11})
        txt_normal_text = workbook.add_format({'align':'left','size':11,'text_wrap': True})
        for i in range(0,10):
            sheet.set_column(0,i,15)
        
        # months = list(rrule.rrule(rrule.MONTHLY, dtstart=self.date_from, until=self.date_to))

        # month_names = '-'.join(calendar.month_name[month.date().month] for month in months)

        sheet.merge_range('A1:J1','Income Tax Report', heading)
        # sheet.merge_range('G2:H2',"")
        
        headers = ['Payment Section', 'TaxPayer_NTN', 'TaxPayer_CNIC', 'TaxPayer_Name', 'TaxPayer_City', 'TaxPayer_Address', 'TaxPayer_Status', 'TaxPayer_Business_Name','Taxable_Amount','Tax_Amount']
        for col_num, header_name in enumerate(headers):
            sheet.write(1, col_num, header_name, header)
        

        inv_row=2
        serial = 1
        if len(datas)!=0:
            for line in datas:
                sheet.write(inv_row,0,line[0],normal_text)
                sheet.write(inv_row,1,line[1],int_normal_text)
                sheet.write(inv_row,2,line[2],int_normal_text)
                sheet.write(inv_row,3,line[3],txt_normal_text)
                sheet.write(inv_row,4,line[4],txt_normal_text)
                sheet.write(inv_row,5,line[5],txt_normal_text)
                sheet.write(inv_row,6,line[6],txt_normal_text)
                sheet.write(inv_row,7,line[7],txt_normal_text)
                # Formatting the last two values with commas
                formatted_value_8 = "{:,}".format(line[8]) if isinstance(line[8], (int, float)) else line[8]
                formatted_value_9 = "{:,}".format(line[9]) if isinstance(line[9], (int, float)) else line[9]

                sheet.write(inv_row, 8, formatted_value_8, int_normal_text)
                sheet.write(inv_row, 9, formatted_value_9, int_normal_text)
                inv_row+=1
                serial+=1
        else:
            raise UserError('No payslip data found')

        workbook.close()
        excel_data = excel_encode.getvalue()
        encoded_excel_data = base64.b64encode(excel_data).decode()

        export_id = self.env['tax.report.excel'].create({'excel_file':encoded_excel_data, 'file_name': filename})
        res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'tax.report.excel',
                'type': 'ir.actions.act_window',
                'target':'new'
            }
        return res



class tax_report_excel(models.TransientModel):
    _name = "tax.report.excel"
    _description = "Tax Report"
    
    excel_file = fields.Binary('Tax Report')
    file_name = fields.Char('Excel File', size=64)