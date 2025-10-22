from odoo import models, fields, api,_
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from . import xlsxwriter
import base64
from io import BytesIO
import json
from odoo.exceptions import UserError
import io
from datetime import datetime , timedelta
from dateutil.relativedelta import relativedelta
try:
    import xlwt
except ImportError:
    xlwt = None
import calendar


class AttendanceReport(models.TransientModel):

    _name = 'attendance.report.wizard'
    
    _description = 'Attendance Report Wizard'

    date_filter =  fields.Selection([('range','Range')],string="Date")

    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
  
    def get_working_days(self, start_date, end_date):
        current_date = start_date
        working_days = 0
        
        while current_date <= end_date:
                # Check if it's a working day (not Saturday or Sunday)
                if current_date.weekday() not in [5, 6]:  # 5 = Saturday, 6 = Sunday
                        working_days += 1

                current_date += timedelta(days=1)
        
        return working_days
    
    def action_print_excel_report(self):
        
        date_from = self.from_date
        date_to = self.to_date

        date_from_obj = fields.Datetime.from_string(date_from)
        date_to_obj = fields.Datetime.from_string(date_to)


        total_days_in_month = (date_to_obj - date_from_obj).days + 1 
        working_days_in_month = self.get_working_days(date_from_obj, date_to_obj)

        excel_encode = io.BytesIO()
        filename = "Attendance Report - " + str(datetime.now().strftime("%d-%m-%Y")) + ".xlsx"
        workbook = xlsxwriter.Workbook(excel_encode)
        sheet = workbook.add_worksheet('Attendance reports')
        header = workbook.add_format({'bold': True, 'align': 'center', 'size': 12 ,'font_name': 'Times New Roman'})
        header.set_border()
        summary_format = workbook.add_format({'bold': True, 'align': 'center', 'align': 'center', 'valign': 'vcenter',  'size': 8 , 'font_name': 'Arial' , 'border': 1,})
        normal_format = workbook.add_format({'align': 'center', 'size': 10 , 'font_name': 'Arial'}) 
        norm_format = workbook.add_format({ 'align': 'centre','bold': True ,'size': 10,'font_name':'Arial' })
        column_widths = { 0 : 5.36, 
                 1: 10.18, 2: 31.18, 3: 40.91, 4: 12.91, 5: 12.91, 6 : 36.64,
            }   

        for col, width in column_widths.items():
                
                sheet.set_column(col, col, width)
        sheet.set_row(3, 21)
        sheet.set_row(4, 10.50)
        sheet.merge_range('A4:A5', 'S.NO', summary_format )
        sheet.merge_range('B4:B5', 'CODE', summary_format )
        sheet.merge_range('C4:C5', 'NAME', summary_format )
        sheet.merge_range('D4:D5', 'DESIGNATION', summary_format )
        sheet.merge_range('E4:E5', 'ATTENDANCE', summary_format )
        sheet.merge_range('F4:F5', 'DEDUCTION', summary_format )
        sheet.merge_range('G4:G5', 'REMARKS', summary_format )

        
        departments = self.env['hr.department'].search([], order='parent_id asc , name asc')
        row = 5
        
        for department in departments:
             employees = self.env['hr.employee'].search([('department_id' , '=', department.id)])
             for index, employee in enumerate(employees):  
                if index == 0:
                     sheet.write(row , 2 , department.parent_id.name, norm_format)
                     row += 1 
                     sheet.write(row, 2, department.name, norm_format) 
                     row += 1 

                else:
                     sheet.write(row, 2, "", normal_format)      
                sheet.write(row, 0, index + 1, normal_format)
                sheet.write(row, 1, employee.employee_id or "", normal_format)
                sheet.write(row, 2, employee.name or "", normal_format)
                sheet.write(row, 3, employee.job_id.name if employee.job_id else "", normal_format)
                attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', date_from_obj),
                ('check_out', '<=', date_to_obj)
                ])

                # raise UserError(str(attendances.read()))
                present_days = set()
                for attendance in attendances:
                        check_in_date = fields.Datetime.from_string(attendance.check_in).date()
                        if check_in_date.weekday() not in [5, 6]:  
                                present_days.add(check_in_date)
                present_days_count = len(present_days)
                if present_days_count == working_days_in_month:
                        total_attendance = total_days_in_month
                else:
                        if present_days_count > 0:
                                total_attendance = present_days_count + (total_days_in_month - working_days_in_month)
                                
                        else:
                              total_attendance = 0
                sheet.write(row, 4, total_attendance, normal_format) 
                sheet.write(row, 5, "-", normal_format)  
                sheet.write(row, 6, "-", normal_format)  # Remarks column (can be adjusted)
                row += 1 


        workbook.close()
        excel_data = excel_encode.getvalue()
        encoded_excel_data = base64.b64encode(excel_data).decode()

        export_id = self.env['customer.invoices.report.excel'].create({'excel_file': encoded_excel_data, 'file_name': filename})
        res = {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'customer.invoices.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
        return res






