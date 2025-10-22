from odoo import models
from datetime import datetime, timedelta
from . import excel_formatter as ft

class InventoryExcelReport(models.AbstractModel):
    _name = 'report.custom_inventory_report_all.report_inventory_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, docs):
        def create_format(format):
            return workbook.add_format(format)
        
        sheet = workbook.add_worksheet('Inventory Report')
        sheet.hide_gridlines(0)

        sheet.set_column("A:B", 14)
        sheet.set_column("B:C", 22)
        sheet.set_column("C:D", 12)
        sheet.set_column("D:E", 0.3)
        sheet.set_column("E:F", 12)
        sheet.set_column("F:G", 12)
        sheet.set_column("G:H", 12)
        sheet.set_column("H:I", 0.3)
        sheet.set_column("I:J", 12)
        sheet.set_column("J:K", 12)
        sheet.set_column("K:L", 12)
        sheet.set_column("L:M", 0.3)
        sheet.set_column("M:N", 12)
        sheet.set_column("N:O", 12)
        sheet.set_column("O:P", 12)
        sheet.set_column("P:Q", 0.3)
        sheet.set_column("Q:R", 12)
        sheet.set_column("R:S", 12)
        sheet.set_column("S:T", 12)
        # Define formats
        bold_left = create_format(ft.BOLD_LEFT)
        bold_right = create_format(ft.BOLD_RIGHT)
        centered = create_format(ft.CENTER)
        number_format = create_format(ft.NUMBER)
        left_format = create_format(ft.LEFT)
        title_format = create_format(ft.TITLE)
        header_left_format = create_format(ft.TABLE_HEADERS_LEFT)
        header_format = create_format(ft.TABLE_HEADERS)
        total_format = create_format(ft.TOTAL)
        subtitle_format = create_format(ft.SUBTITLE)

        # Add headers
        sheet.merge_range('A1:S1', 'Biafo Industries Limited', title_format)
        sheet.merge_range('A2:S2', 'Inventory List', title_format)

        subtitle = "("
        if data.get('from_date'):
            subtitle += f"From: {data['from_date']}, To: {data['to_date']}, "
        if data.get('from_product'):
            subtitle += f"From: {data['from_product']}, To: {data['to_product']}, "
        subtitle += "Rupees, Stock Items)"

        sheet.merge_range('A3:S3', subtitle, subtitle_format)

        # Adding date and time information
        time = datetime.now() + timedelta(hours=5)
        current_date = time.strftime('%d-%b-%Y')
        current_time = time.strftime('%I:%M %p')
        sheet.merge_range('A4:B4', f'Date: {current_date}', bold_left)
        sheet.merge_range('R4:S4', f'Time: {current_time}', bold_right)

        # Table Headers
        merged_headers = ['Product Code', 'Description', 'Units']
        sheet.merge_range('A6:A7', merged_headers[0], header_left_format)
        sheet.merge_range('B6:B7', merged_headers[1], header_left_format)
        sheet.merge_range('C6:C7', merged_headers[2], header_left_format)
        sheet.merge_range('D6:D7', '', header_format)

        sheet.merge_range('E6:G6', 'Opening', header_format)
        sheet.merge_range('H6:H7', '', header_format)
        sheet.merge_range('I6:K6', 'In', header_format)
        sheet.merge_range('L6:L7', '', header_format)
        sheet.merge_range('M6:O6', 'Out', header_format)
        sheet.merge_range('P6:P7', '', header_format)
        sheet.merge_range('Q6:S6', 'Closing', header_format)


        headers = [            
            'Quantity', 'Rate', 'Amount',
        ]
        x, y, z = 4, 5, 6
        for _ in range(4):
            sheet.write(6, x, headers[0], header_format)
            sheet.write(6, y, headers[1], header_format)
            sheet.write(6, z, headers[2], header_format)
            x += 4
            y += 4
            z += 4
        
        # for row in range(7, 51):
        #     for col in range(19):
        #         if (col+1) % 4 != 0:
        #             sheet.write(row, col, 0, centered)
        row = 7
        total1 = 0
        total2 = 0
        total3 = 0
        total4 = 0
        for product_id in data['data']:
            move = data['data'][product_id]
            sheet.write(row, 0, move['code'], left_format)
            sheet.write(row, 1, move['product_name'], left_format)
            sheet.write(row, 2, move['unit'], left_format)
            sheet.write(row, 4, '{:,.4f}'.format(move['opening_quantity']), number_format)
            sheet.write(row, 5, '{:,.4f}'.format(move['opening_rate']), number_format)
            sheet.write(row, 6, '{:,.4f}'.format(move['opening_amount']), number_format)
            sheet.write(row, 8, '{:,.4f}'.format(move['in_quantity']), number_format)
            sheet.write(row, 9, '{:,.4f}'.format(move['in_rate']), number_format)
            sheet.write(row, 10, '{:,.4f}'.format(move['in_amount']), number_format)
            sheet.write(row, 12, '{:,.4f}'.format(move['out_quantity']), number_format)
            sheet.write(row, 13, '{:,.4f}'.format(move['out_rate']), number_format)
            sheet.write(row, 14, '{:,.4f}'.format(abs(move['out_amount'])), number_format)
            sheet.write(row, 16, '{:,.4f}'.format(move['closing_quantity']), number_format)
            sheet.write(row, 17, '{:,.4f}'.format(move['closing_rate']), number_format)
            sheet.write(row, 18, '{:,.4f}'.format(move['closing_amount']), number_format)
            total1 += move['opening_amount']
            total2 += move['in_amount']
            total3 += move['out_amount']
            total4 += move['closing_amount']
            row += 1

        sheet.merge_range(row, 0, row, 2, 'Total', bold_right)
        sheet.write(row, 6, '{:,.4f}'.format(total1), total_format)
        sheet.write(row, 10, '{:,.4f}'.format(total2), total_format)
        sheet.write(row, 14, '{:,.4f}'.format(abs(total3)), total_format)
        sheet.write(row, 18, '{:,.4f}'.format(total4), total_format)
