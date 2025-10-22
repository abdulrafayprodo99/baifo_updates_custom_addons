from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime



class SaleXlsxReport(models.AbstractModel):
    _name = 'report.aged_receviable_report.action_aged_receivable'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        report_data = data
        grouped_data = report_data.get('grouped_data', {})
        today = datetime.today().strftime('%d-%b-%Y')  
        title = f"Aged Analysis As at {today}"

        # Formats
        title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
        header_format = workbook.add_format({'bold': True, 'border': 1, 'align': 'center'})
        cell_format = workbook.add_format({'border': 1, 'align': 'center'})
        

        # Create Sheet
        sheet = workbook.add_worksheet('Receivable Report')
        sheet.merge_range('A1:Q1', title, title_format)

        # Headers Row 2: Merge "Overdue"
        sheet.merge_range('I2:O2', 'Overdue', header_format)

        # Row 3: Column Headers
        headers = [
            'Narration', 'Partner Name', 'Doc No', 'Date',
             'Credit Days',
            'Overdue Days', 'Exact Days', 'Net Due Amount',
            '1-15 Days', '16-30 Days', '31-45 Days',
            '46-60 Days', '61-75 Days', '75+ Days','Totals'
        ]

        for col, header in enumerate(headers):
            sheet.set_column(col, col, 15)
            sheet.write(2, col, header, header_format)

        row = 3  # Start writing data from row 4

        for partner_id, partner_data in grouped_data.items():
            for bill in partner_data['bills']:
                # Write values for each column
                sheet.write(row, 0, bill.get('narration', ''), cell_format)
                sheet.write(row, 1, bill.get('partner_name', ''), cell_format)
                sheet.write(row, 2, bill.get('name', ''), cell_format)
                sheet.write(row, 3, bill.get('date', ''), cell_format)
                # sheet.write(row, 4, bill.get('due_date', ''), cell_format)
                # sheet.write(row, 5, bill.get('currency_name', ''), cell_format)
                # sheet.write(row, 6, bill.get('currency_rate', ''), cell_format)
                sheet.write(row, 4, bill.get('credit', ''), cell_format)
                sheet.write(row, 5, bill.get('over_due_days', ''), cell_format)
                sheet.write(row, 6, bill.get('exact', ''), cell_format)
                sheet.write(row, 7, bill.get('amount_due', ''), cell_format)
                sheet.write(row, 8, sum(bill.get('total_15', [])), cell_format)
                sheet.write(row, 9, sum(bill.get('total_31', [])), cell_format)
                sheet.write(row, 10, sum(bill.get('total_46', [])), cell_format)
                sheet.write(row, 11, sum(bill.get('total_61', [])), cell_format)
                sheet.write(row, 12, sum(bill.get('total_75', [])), cell_format)
                sheet.write(row, 13, sum(bill.get('total_75_plus', [])), cell_format)
                sheet.write(row, 14, sum(bill.get('total_15', []) + bill.get('total_31', []) + bill.get('total_46', []) + bill.get('total_61', []) + bill.get('total_75', []) + bill.get('total_75_plus', [])))

                row += 1