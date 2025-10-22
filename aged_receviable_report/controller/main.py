from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from datetime import timedelta
import base64
import logging
from datetime import datetime
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import io
import xlsxwriter

_logger = logging.getLogger(__name__)

class SupplierController(http.Controller):

    @http.route(['/supplier/report'], type='json', auth='public', methods=['POST', 'GET'], csrf=False)
    def trigger_supplier_ledger_report(self, **kwargs):
        def _get_many2many():
            partners = []
            args = kwargs.get('args')
            if args and len(args) > 0 and 'many2many' in args[0] and args[0]['many2many']:
                for id in kwargs.get('args')[0]['many2many']:
                    supplier = request.env['res.partner'].sudo().browse(id)
                    if supplier.exists() and _has_journal_entries_in_date_range(supplier, date1, date2):
                        partners.append(supplier)
            return partners
        
        # def get_data_sequentially():
        #     id1 = int(kwargs.get('args')[0]['sup1'])
        #     id2 = int(kwargs.get('args')[0]['sup2'])
        #     partners = []
        #     while id1 <= id2:
        #         supplier = request.env['res.partner'].sudo().browse(id1)
        #         if supplier.exists() and _has_journal_entries_in_date_range(supplier, date1, date2):
        #             partners.append(supplier)
        #         id1 += 1
        #     return partners

        def _has_journal_entries_in_date_range(partner, start_date, end_date):
            return request.env['account.move'].sudo().search_count([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
                ('journal_id.type', 'in', ['purchase', 'sale', 'bank']),
                ('date', '>=', start_date),
                ('date', '<=', end_date)
            ]) > 0

        date1 = datetime.strptime(kwargs.get('args')[0].get('date1'), '%Y-%m-%d').date()
        date2 = datetime.strptime(kwargs.get('args')[0].get('date2'), '%Y-%m-%d').date()

        # partners = _get_many2many() if len(_get_many2many()) > 0 else get_data_sequentially()
        partners = _get_many2many() 

        grand_totals = {
            'qty': 0,
            'rate': 0,
            'exclude_tax': 0,
            'tax_amount': 0,
            'debit': 0,
            'credit': 0,
            'balance': 0,
        }
        obj = {}

        for partner in partners:
            account_moves = request.env['account.move'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
                # ('journal_id.type', 'in', ['purchase', 'sale', 'bank']),
                ('date', '>=', date1),
                ('date', '<=', date2),
            ]).filtered(lambda journal: journal.journal_id.code == 'JV' or journal.journal_id.type in ['purchase', 'sale', 'bank'])
            
            # journal_entries = 
            payments= account_moves.filtered(lambda m: m.move_type == "entry")
            journal_entries = account_moves.filtered(lambda m: m.move_type in ["out_invoice", "in_invoice"]) 
            
            
            ##### Get Opening balances
            opening_balance_lines_moves=request.env['account.move'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
                # ('journal_id.type', 'in', ['purchase', 'sale', 'bank']),
                ('date','<=',(date1-timedelta(days=1)))
                ]).filtered(lambda x:x.journal_id.type in ['purchase', 'sale', 'bank'] or x.journal_id.code=='JV')
            
            opening_balance_lines=opening_balance_lines_moves.mapped('line_ids').filtered(lambda m:m.account_id.account_type in ['liability_payable','asset_receivable'])
            # raise UserError(date1-timedelta(days=1))
            debit_opening  = sum([line.debit for line in opening_balance_lines])
            credit_opening  = sum([line.credit for line in opening_balance_lines])
            
            opening_balance  = debit_opening-credit_opening
            
            
            #####Get Ledger Lines
            
            move_lines = payments.mapped('line_ids')
            
            moves = request.env['account.move.line']
            for move in move_lines:
                if move.account_id.code in ['320401001', '220101001']:
                    moves += move

            moves += journal_entries.mapped('invoice_line_ids').filtered(lambda l: date1 <= l.move_id.date <= date2)
                
            total_qty = sum(move_line.quantity for move_line in moves if move_line.move_id.move_type in ['in_invoice', 'out_invoice'])
            total_rate = sum([move_line.price_unit for move_line in moves])
            total_exclude_tax = sum([move_line.price_subtotal for move_line in moves])
            total_tax_amount = sum([(move_line.price_total - move_line.price_subtotal) for move_line in moves])
            # if total_credit ==0:
            credit = 0
            debit = 0
            total_credit = 0
            total_debit = 0
            
            balance = opening_balance
            obj[partner.name] = {
                'opening': {
                    'number': partner.x_studio_new_code,
                    'name': partner.name,
                    'opening_balance': opening_balance,
                },
                'data': [],
            }
            moves = sorted(moves,key=lambda x: x.move_id.date)
            for move_line in moves:
                if move_line.move_id.currency_rate:
                    tax_amount = (move_line.move_id.currency_rate*move_line.price_total) - (move_line.move_id.currency_rate * move_line.price_subtotal)
                else:
                    tax_amount = move_line.price_total -  move_line.price_subtotal
                    
                closing_balance = move_line.price_subtotal + move_line.debit - move_line.credit

                if move_line.move_id.move_type == 'in_invoice':  
                    credit_amount = (move_line.move_id.currency_rate*move_line.price_total) if move_line.move_id.currency_rate else move_line.price_total
                    debit_amount = 0.0
                    quantity = move_line.quantity
                elif move_line.move_id.move_type == 'out_invoice':  
                    credit_amount = 0.0
                    debit_amount = (move_line.move_id.currency_rate*move_line.price_total) if move_line.move_id.currency_rate else move_line.price_total
                    quantity = move_line.quantity
                else:  
                    debit_amount =  move_line.debit
                    credit_amount =  move_line.credit
                    quantity = 0
                    
                total_credit+=credit_amount
                total_debit+=debit_amount
                balance += debit_amount - credit_amount
                
                line_data = {
                    'date': move_line.move_id.date.strftime('%d-%m-%y'),
                    'doc_id': move_line.move_id.name,
                    'narration': move_line.move_id.ref if move_line.move_id.ref else None,
                    'product_code': move_line.product_id.code if move_line.product_id.code != False else None,
                    'product_description': move_line.product_id.name if move_line.product_id.code != False else None,
                    'unit': move_line.product_uom_id.name if move_line.product_uom_id else None,
                    'quantity': quantity,
                    'rate': move_line.price_unit, 
                    'value_excluding_sales_tax': (move_line.move_id.currency_rate * move_line.price_subtotal) if move_line.move_id.currency_rate else move_line.price_subtotal,
                    'sales_tax_amount': tax_amount,
                    'debit': debit_amount,
                    'credit': credit_amount,
                    'closing_balance': balance,
                }
                obj[partner.name]['data'].append(line_data)
            
            
            
                obj[partner.name]['total'] = {
                    'total_qty': total_qty,
                    'total_rate': total_rate,
                    'total_exclude_tax': total_exclude_tax,
                    'total_tax_amount': total_tax_amount,
                    'total_debit': total_debit,
                    'total_credit': total_credit,
                    'total_balance': balance,
                }
                
            grand_totals['qty'] += total_qty
            grand_totals['rate'] += total_rate
            grand_totals['exclude_tax'] += total_exclude_tax
            grand_totals['tax_amount'] += total_tax_amount
            grand_totals['debit'] += total_debit
            grand_totals['credit'] += total_credit
            grand_totals['balance'] += balance
            
        obj['grand_total'] = {
            'grand_total_qty2': grand_totals['qty'],
            'grand_total_rate2': grand_totals['rate'],
            'grand_total_exclude_tax2': grand_totals['exclude_tax'],
            'grand_total_tax_amount2': grand_totals['tax_amount'],
            'grand_total_debit2': grand_totals['debit'],
            'grand_total_credit2': grand_totals['credit'],
            'grand_total_balance2': grand_totals['balance'],
        }
        # raise UserError()
        obj = dict(sorted(obj.items(), key=lambda x: x[1].get('opening', {}).get('number', '')))
        return obj
    
    @http.route(['/supplier/report/pdf'], type='json', auth='public', methods=['POST'], csrf=False)
    def generate_pdf_report(self, **kwargs):
        columns = kwargs.get('columns', [])
        values = kwargs.get('values', [])
        header_values = kwargs.get('filter_response', [])
        
        # partner=request.env['res.partner'].sudo().browse()
        # raise UserError(str(header_values))
        
        
        
        report_data = {
            'report_columns': columns,
            'report_header_values': header_values,
            'report_values': values,
        }

        pdf_report = request.env['ir.actions.report'].sudo()._render_qweb_pdf('aged_receviable_report.supplier_report', data=report_data)
        pdf_base64 = base64.b64encode(pdf_report[0])

        return {
            'pdf_base64': pdf_base64.decode('utf-8'),
        }
    

    @http.route(['/supplier/report/xlsx'], type='json', auth='public', methods=['POST'], csrf=False)
    def generate_xlsx_report(self, **kwargs):
        columns = kwargs.get('columns', [])
        values = kwargs.get('values', [])
        # raise UserError(str(values))
        header_values = kwargs.get('filter_response', [])
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        # Define formats
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1, 'align': 'right'})
        center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True})
        bold_format = workbook.add_format({'bold': True})
        border_format = workbook.add_format({'border': 1, 'align': 'left'})
        border_center_format = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
        bold_border_format = workbook.add_format({'bold': True, 'border': 1})

        # Setting up column widths similar to your screenshot
        sheet.set_column('C:C', 12)  # Date
        sheet.set_column('D:D', 15)  # Document ID
        sheet.set_column('E:E', 40)  # Narration
        sheet.set_column('F:F', 20)  # Product Code
        sheet.set_column('G:G', 30)  # Product Description
        sheet.set_column('H:H', 10)  # Unit
        sheet.set_column('I:I', 30)  # Quantity
        sheet.set_column('J:J', 30)  # Rate
        sheet.set_column('K:K', 30)  # Excluding Sale Tax
        sheet.set_column('L:L', 30)  # Sale Tax Amount
        sheet.set_column('M:M', 30)  # Debit
        sheet.set_column('N:N', 30)  # Credit
        sheet.set_column('O:O', 30)  # Balance

        # Header (From Partner: To Partner)
        sheet.merge_range('D1:I1', f"From Partner: {header_values[0]}          To Partner: {header_values[1]}", center_format)
        sheet.merge_range('D2:I2', f"From Date: {header_values[2]}          To Date: {header_values[3]}", center_format)

        row = 2
        col = 0
        
        for col_name in columns:
            if col_name == 'date':
                sheet.write(row, col, "DATE", bold_border_format)
                sheet.set_column(col, col, len("DATE") + 2)
            elif col_name == 'doc':
                sheet.write(row, col, "DOCUMENT ID", bold_border_format)
                sheet.set_column(col, col, len("DOCUMENT ID") + 2)
            elif col_name == 'narration':
                sheet.write(row, col, "NARRATION", bold_border_format)
                sheet.set_column(col, col, len("NARRATION") + 2)
            elif col_name == 'product_code':
                sheet.write(row, col, "PRODUCT CODE", bold_border_format)
                sheet.set_column(col, col, len("PRODUCT CODE") + 2)
            elif col_name == 'product_description':
                sheet.write(row, col, "PRODUCT DESCRIPTION", bold_border_format)
                sheet.set_column(col, col, len("PRODUCT DESCRIPTION") + 2)
            elif col_name == 'unit':
                sheet.write(row, col, "UNIT", bold_border_format)
                sheet.set_column(col, col, len("UNIT") + 2)
            elif col_name == 'quantity':
                sheet.write(row, col, "QUANTITY", bold_border_format)
                sheet.set_column(col, col, len("QUANTITY") + 2)
            elif col_name == 'rate':
                sheet.write(row, col, "RATE", bold_border_format)
                sheet.set_column(col, col, len("RATE") + 2)
            elif col_name == 'excluding_sale_tax':
                sheet.write(row, col, "EXCLUDING SALE TAX", bold_border_format)
                sheet.set_column(col, col, len("EXCLUDING SALE TAX") + 2)
            elif col_name == 'sale_tax_amount':
                sheet.write(row, col, "SALE TAX AMOUNT", bold_border_format)
                sheet.set_column(col, col, len("SALE TAX AMOUNT") + 2)
            elif col_name == 'debit':
                sheet.write(row, col, "DEBIT", bold_border_format)
                sheet.set_column(col, col, len("DEBIT") + 2)
            elif col_name == 'credit':
                sheet.write(row, col, "CREDIT", bold_border_format)
                sheet.set_column(col, col, len("CREDIT") + 2)
            elif col_name == 'balance':
                sheet.write(row, col, "BALANCE", bold_border_format)
                sheet.set_column(col, col, len("BALANCE") + 2)
            col += 1
        # Writing data rows
        col_value = 5
        row_value = 4
        grand_total = values.get('grand_total')

        for key, item in values.items():
            opening_data = values[key].get('opening')
            data = values[key].get('data')
            # raise UserError(str(data))
            total = values[key].get('total')
            
            # Merging rows for opening balances
            if opening_data:
                _logger.info(f"==={row_value}")
                row_value += 1
                # Writing the opening data
                sheet.write(f"A{row_value}", opening_data.get('number', ''), bold_format)
                # Corrected merge_range for name
                sheet.merge_range(f"B{row_value}:D{row_value}", opening_data.get('name', ''), bold_format)
                # Corrected merge_range for opening balance
                sheet.merge_range(f"L{row_value}:M{row_value}", f"Opening Balance {opening_data.get('opening_balance', 0)}", bold_format)
                

            # Writing each data entry with borders
            if data:
                for d in data:
                    sheet.write(row_value,0, d.get('date', ''), border_format)
                    sheet.write(row_value,1, d.get('doc_id', ''), border_format)
                    sheet.write(row_value,2, d.get('narration', ''), border_format)
                    sheet.write(row_value,3, d.get('product_code', ''), border_format)
                    sheet.write(row_value,4, d.get('product_description', ''), border_format)
                    sheet.write(row_value,5, d.get('unit', ''), border_center_format)
                    sheet.write(row_value,6, d.get('quantity', 0), currency_format)
                    sheet.write(row_value,7, d.get('rate', 0), currency_format)
                    sheet.write(row_value, 8, d.get('value_excluding_sales_tax', 0), currency_format)
                    sheet.write(row_value, 9, d.get('sales_tax_amount', 0), currency_format)
                    sheet.write(row_value, 10, d.get('debit', 0), currency_format)
                    sheet.write(row_value, 11, d.get('credit', 0), currency_format)
                    sheet.write(row_value, 12, d.get('closing_balance', 0), currency_format)
                    row_value += 1


                # Adding totals row for each partner (make sure this is done for every partner)
            
            if total:
                sheet.write(row_value,5, "Total", bold_border_format)
                sheet.write(row_value,6, total.get('total_qty', 0), currency_format,)
                sheet.write(row_value,7, total.get('total_rate', 0), currency_format)
                sheet.write(row_value, 8, total.get('total_exclude_tax', 0), currency_format)
                sheet.write(row_value, 9, total.get('total_tax_amount', 0), currency_format)
                sheet.write(row_value, 10, total.get('total_debit', 0), currency_format)
                sheet.write(row_value, 11, total.get('total_credit', 0), currency_format)
                sheet.write(row_value,12 , total.get('total_balance', 0), currency_format)
                row_value += 1  # Move to the next row after printing totals

        # Writing grand totals row for all partners
        if grand_total:
            sheet.write(row_value,5, "Grand Total", bold_border_format)
            sheet.write(row_value,6, grand_total.get('grand_total_qty2', 0), currency_format)
            sheet.write(row_value,7, grand_total.get('grand_total_rate2', 0), currency_format)
            sheet.write(row_value, 8, grand_total.get('grand_total_exclude_tax2', 0), currency_format)
            sheet.write(row_value, 9, grand_total.get('grand_total_tax_amount2', 0), currency_format)
            sheet.write(row_value, 10, grand_total.get('grand_total_debit2', 0), currency_format)
            sheet.write(row_value, 11, grand_total.get('grand_total_credit2', 0), currency_format)
            sheet.write(row_value, 12, grand_total.get('grand_total_balance2', 0), currency_format)

        # Finalizing workbook
        workbook.close()
        output.seek(0)
        xlsx_data = output.read()
        filename = 'supplier_report_{}.xlsx'.format(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        attachment_id = request.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(xlsx_data),
            'res_model': 'ir.action.report',  # This can be any model you associate with the report
            'res_id': False,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        xlsx_report_base64 = base64.b64encode(xlsx_data).decode('utf-8')
        return {
            'xlsx_base64': xlsx_report_base64,
            'attachment_id': attachment_id.id,
        }