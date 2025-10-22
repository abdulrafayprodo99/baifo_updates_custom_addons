import io
import base64
from odoo import models, fields, api
from odoo.tools.misc import xlsxwriter
import datetime

class BankLetterExcelReportWizard(models.TransientModel):
    _name = 'report.bank_letter.report_bank_letter_excel'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Bank Letter Excel Report'

    def generate_xlsx_report(self, workbook, data, docs):
        def create_format(**kwargs):
            base_format = {
                "font_size": 11,
                "border": 1,
                "valign": "vcenter",
            }
            base_format.update(kwargs)
            return workbook.add_format(base_format)

        formats = {
            "wrap": {"text_wrap": True},
            "bold": {"bold": True},
            "left": {"align": "left", "border": 0,},
            "table_head": {
                "border": 2,
                "bold": True,
                "align": "center",
                "font_size": 13,
            },
            "section_main": {
                "bg_color": "#b3cde3",
                "bold": True,
                "border":0,
            },
            "section": {
                "bg_color": "#eaf4ff",
                "bold": True,
                "border":0,
            },
            "currency": {"num_format": f'#,##0.00', "border": 0},
            "center_percent": {"align": "center", "num_format": "0.00%", "border": 0},
        }

        for key, value in formats.items():
            formats[key] = create_format(**value)

        sheet = workbook.add_worksheet('Inventory Report')
        sheet.hide_gridlines(0)

        sheet.set_column("A:B", 10)
        sheet.set_column("B:C", 15)
        sheet.set_column("C:D", 45)
        sheet.set_column("D:E", 55)
        sheet.set_column("E:F", 30)

        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 2})
        header_left_format = workbook.add_format({'bold': True, 'align': 'left', 'border': 2})
        left_format = workbook.add_format({'align': 'left'})
        right_format = workbook.add_format({'align': 'right'})
        center_format = workbook.add_format({'align': 'center'})
        wrap_format = workbook.add_format({'align': 'left', 'text_wrap': True})
        total_format_1 = workbook.add_format({'bold': True, 'align': 'right'})
        total_format_2 = workbook.add_format({'bold': True, 'align': 'right', 'top': 2, 'bottom': 2})

        sheet.merge_range('A1:C1', f'The Manager,', left_format)
        sheet.merge_range('D1:E1', data['date'], right_format)
        sheet.merge_range('A3:E3', data['bank_name'], left_format)

        row = 4
        for line in data['address']:
            sheet.merge_range(f'A{row}:E{row}', line, left_format)
            row += 1

        row += 1
        sheet.merge_range(f'A{row}:E{row}', f'PAYMENT INSTRUCTION', left_format)

        row += 2
        sheet.merge_range(f'A{row}:E{row}', f'Dear Sir,', left_format)

        row += 2
        sheet.merge_range(
            f'A{row}:E{row+1}',
            f"You are requested to debit our Account No. {data['account_number']} and transfer the salary amounting Rs. {data['total_amount']}/- ({data['total_amount_iw']}) "
            "to the credit of the following individual's Account Numbers of Biafo employees being maintained at your branch:",
            wrap_format,
        )

        row += 3

        headers = ['S.No.', 'Emp Code', 'Name', 'Account Number', 'Amount (Rs.)']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_format)

        row += 1

        for count, payslip in enumerate(data['payslips'], start=1):

            sheet.write(row, 0, count, center_format)
            sheet.write(row, 1, payslip['emp_code'] or '', center_format)
            sheet.write(row, 2, payslip['name'], left_format)
            sheet.write(row, 3, payslip['account'] or '', left_format)
            sheet.write(row, 4, payslip['amount'], right_format)
            row += 1

        sheet.merge_range(row, 0, row, 3, 'TOTAL Rs.', total_format_1)
        sheet.write(row, 4, data['total_amount'], total_format_2)        