from odoo import fields, api, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    from . import xlsxwriter
from . import excel_formatter
from io import BytesIO
import base64

_logger = logging.getLogger(__name__)


class ProductLedgerWizard(models.TransientModel):
    _name = 'product.ledger.report.wizard'

    product_filter = fields.Selection([('all', 'All'), ('manual', 'Single'), ('range', 'Range')], string="Product", default="all")
    date_filter = fields.Selection([('all', 'All'), ('range', 'Range')], string="Date", default="all")
    location_filter = fields.Selection([('all', 'All'), ('manual', 'Single')], string="Location", default="all")
    category_filter = fields.Selection([('all', 'All'), ('manual', 'Single')], string="Category", default="all")

    location_ids = fields.Many2many('stock.location', string="Location")

    product_ids = fields.Many2many(
        string='Products',
        comodel_name='product.product',
    )

    category_ids = fields.Many2many(
        string="Categories",
        comodel_name='product.category'
    )

    from_product = fields.Many2one('product.product', string="From Product")
    to_product = fields.Many2one('product.product', string="To Product")

    from_date = fields.Date(
        string='From Date'
    )

    to_date = fields.Date(
        string='To Date',
        default=datetime.today()
    )
    
    report_file = fields.Binary('Product Ledger Report File')

    
    def get_file_name(self):
        filename = "product_ledger_report.xlsx"
        return filename

    def create_excel_workbook(self, file_pointer):
        workbook = xlsxwriter.Workbook(file_pointer)
        return workbook

    def create_excel_worksheet(self, workbook, sheet_name):
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.set_default_row(22)
        return worksheet

    def set_column_width(self, workbook, worksheet):
        worksheet.set_column(0, 1, 25)
        worksheet.set_column(2, 8, 14)

    def set_format(self, workbook, wb_format):
        wb_new_format = workbook.add_format(wb_format)
        wb_new_format.set_border()
        return wb_new_format

    def set_report_title(self, workbook, worksheet, from_date, to_date, from_product, to_product):
        wb_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_CENTER)
        sm_format = self.set_format(workbook, excel_formatter.FONT_SMALL_BOLD_CENTER)
        worksheet.merge_range(0, 0, 0, 8, "Biafo Industries Limited", wb_format) 
        worksheet.merge_range(1, 0, 1, 8, "Product Ledger Report", sm_format)
        worksheet.merge_range(2, 0, 2, 8, f"(From date: {from_date}, To date: {to_date}, From product:{from_product}, To Product: {to_product})", sm_format)
        
    def download_report(self):
        file_name = self.get_file_name()
        file_pointer = BytesIO()
        report_data = self.get_report(is_excel=True)
        workbook = self.create_excel_workbook(file_pointer)
        sheet_name = "product ledger"
        worksheet = self.create_excel_worksheet(workbook, sheet_name)
        row_no = 5
        self.write_report_data_header(workbook, worksheet, row_no, report_data)
        row_no += 1
        for product_id, product_dict in report_data.get('grouped_data').items():
            _logger.info(product_id)
            worksheet, row_no = self.write_data_to_worksheet(workbook, worksheet, product_dict, row=row_no)
            row_no += 1
        row_no += 1
        worksheet = self.write_report_data_footer(workbook, worksheet, row_no, report_data)

        # workbook.save(file_name)
        workbook.close()
        file_pointer.seek(0)
        file_data = base64.b64encode(file_pointer.read())
        self.write({'report_file': file_data})
        file_pointer.close()

        return {
            'name': f'{file_name}',
            'type': 'ir.actions.act_url',
            'url': '/web/binary/setu_air_download_document?model=product.ledger.report.wizard&field=report_file&id=%s&filename=%s'%(self.id, file_name),
            'target': 'self',
        }

    def write_report_data_header(self, workbook, worksheet, row, report_data):
        self.set_report_title(workbook, worksheet, report_data.get('from_date'), report_data.get('to_date'), report_data.get('start_ref'), report_data.get('end_ref'))
        self.set_column_width(workbook, worksheet)
        wb_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_CENTER)
        wb_format.set_text_wrap()
    
        normal_left_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_LEFT)
        normal_right_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_RIGHT)

        worksheet.write(row, 0, 'Date', normal_left_format)
        worksheet.write(row, 1, 'Doc No.', normal_left_format)
        worksheet.write(row, 2, 'From', normal_left_format)
        worksheet.write(row, 3, 'To', normal_left_format)
        
        worksheet.merge_range(row-1, 4, row-1, 6, "In", wb_format) 
        worksheet.write(row, 4, 'Rate', normal_right_format)
        worksheet.write(row, 5, 'Quantity', normal_right_format)
        worksheet.write(row, 6, "Amount", normal_right_format)
        
        worksheet.merge_range(row-1, 7, row-1, 9, "Out", wb_format) 
        worksheet.write(row, 7, 'Rate', normal_right_format)
        worksheet.write(row, 8, 'Quantity', normal_right_format)
        worksheet.write(row, 9, "Amount", normal_right_format)
        
        worksheet.merge_range(row-1, 10, row-1, 12, "Closing", wb_format) 
        worksheet.write(row, 10, 'Rate', normal_right_format)
        worksheet.write(row, 11, 'Quantity', normal_right_format)
        worksheet.write(row, 12, "Amount", normal_right_format)

        return worksheet
    
    def write_report_data_footer(self, workbook, worksheet, row, data):
        bold_normal_right_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_RIGHT)
        bold_normal_left_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_LEFT)
        # grand total
        grand_total_row = data.get('grand_total')
        worksheet.write(row, 3, "Grand Total:", bold_normal_left_format)
        worksheet.write(row, 6, self.format_to_4_decimal_places(grand_total_row.get('total_in_amount')), bold_normal_right_format)
        worksheet.write(row, 9, self.format_to_4_decimal_places(grand_total_row.get('total_out_amount')), bold_normal_right_format)
        worksheet.write(row, 12, self.format_to_4_decimal_places(grand_total_row.get('total_closing_amount')), bold_normal_right_format)
        return worksheet

    def format_to_4_decimal_places(self, number):
        return f"{number:,.4f}"

    def write_data_to_worksheet(self, workbook, worksheet, data, row):
        bold_normal_right_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_RIGHT)
        bold_normal_left_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_BOLD_LEFT)
        normal_left_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_NORMAL_LEFT)
        normal_left_format_with_date = self.set_format(workbook, excel_formatter.FONT_MEDIUM_NORMAL_LEFT_WITH_DATE)
        normal_right_format = self.set_format(workbook, excel_formatter.FONT_MEDIUM_NORMAL_RIGHT)

        # opening row
        opening_row = data.get('opening')
        worksheet.write(row, 0, opening_row[0], bold_normal_left_format)
        worksheet.write(row, 1, opening_row[1], bold_normal_left_format)
        worksheet.write(row, 2, data.get('uom'), bold_normal_left_format)
        worksheet.write(row, 9, "Opening:", bold_normal_left_format)
        worksheet.write(row, 10, self.format_to_4_decimal_places(opening_row[2]), bold_normal_right_format)
        worksheet.write(row, 11, self.format_to_4_decimal_places(opening_row[3]), bold_normal_right_format)
        worksheet.write(row, 12, self.format_to_4_decimal_places(opening_row[4]), bold_normal_right_format)
        row += 1
        moves = data.get('moves')
        for move in moves:
            worksheet.write(row, 0, move.get('date'), normal_left_format_with_date)
            if move.get('reference'):
                worksheet.write(row, 1, move.get('reference'), normal_left_format)
            worksheet.write(row, 2, move.get('location_from'), normal_left_format)
            worksheet.write(row, 3, move.get('location_to') , normal_left_format)
            
            if move.get('in_quantity') > 0:
                worksheet.write(row, 4, self.format_to_4_decimal_places(move.get('rate')), normal_right_format)
            else:
                worksheet.write(row, 4, self.format_to_4_decimal_places(0), normal_right_format)
            worksheet.write(row, 5, self.format_to_4_decimal_places(move.get('in_quantity')), normal_right_format)
            worksheet.write(row, 6, self.format_to_4_decimal_places(move.get('amount_in')), normal_right_format)
            
            if move.get('out_quantity') > 0:
                worksheet.write(row, 7, self.format_to_4_decimal_places(move.get('rate')), normal_right_format)
            else:
                worksheet.write(row, 7, self.format_to_4_decimal_places(0), normal_right_format)
                
            worksheet.write(row, 8, self.format_to_4_decimal_places(move.get('out_quantity')), normal_right_format)
            worksheet.write(row, 9, self.format_to_4_decimal_places(move.get('out_amount')), normal_right_format)
            
            worksheet.write(row, 10, self.format_to_4_decimal_places(move.get('closing_rate')), normal_right_format)
            worksheet.write(row, 11, self.format_to_4_decimal_places(move.get('closing_qty')), normal_right_format)
            worksheet.write(row, 12, self.format_to_4_decimal_places(move.get('closing_amount')), normal_right_format)
            row += 1
        # moves total
        total_row = data.get('total')
        worksheet.write(row, 3, "Total:", bold_normal_left_format)
        worksheet.write(row, 4, self.format_to_4_decimal_places(total_row.get('total_in_rate')), bold_normal_right_format)
        worksheet.write(row, 5, self.format_to_4_decimal_places(total_row.get('total_in_qty')), bold_normal_right_format)
        worksheet.write(row, 6, self.format_to_4_decimal_places(total_row.get('total_in_amount')), bold_normal_right_format)
        worksheet.write(row, 7, self.format_to_4_decimal_places(total_row.get('total_out_rate')), bold_normal_right_format)
        worksheet.write(row, 8, self.format_to_4_decimal_places(total_row.get('total_out_qty')), bold_normal_right_format)
        worksheet.write(row, 9, self.format_to_4_decimal_places(total_row.get('total_out_amount')), bold_normal_right_format)
        worksheet.write(row, 10, self.format_to_4_decimal_places(total_row.get('total_closing_rate')), bold_normal_right_format)
        worksheet.write(row, 11, self.format_to_4_decimal_places(total_row.get('total_closing_qty')), bold_normal_right_format)
        worksheet.write(row, 12, self.format_to_4_decimal_places(total_row.get('total_closing_amount')), bold_normal_right_format)
                
       
        return worksheet, row


    def Valuation_values_gen(self, move):
        if self.location_filter == 'all':
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id and ((x.account_move_id and x.account_move_id.date <= self.from_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.from_date  )) or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) )
        else:
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id),('product_id.detailed_type','=','product')])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.move_id.id and ((x.account_move_id and x.account_move_id.date <= self.from_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.from_date ))   or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.move_id.id or move.reference in x.stock_valuation_layer_id.reference)) )
        Valuation_values = valuations.mapped("value")

        return Valuation_values

    def Valuation_values_gen_closing(self, move):
        if self.location_filter == 'all':
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id)
            ])
            # valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id and ((x.account_move_id and x.account_move_id.date <= self.to_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) )
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.id 
            and((x.account_move_id and x.account_move_id.date <= self.to_date) 
            or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) 
            or (not x.stock_move_id and move.reference in x.description and not x.reference)
            or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.id or move.reference in x.stock_valuation_layer_id.reference)) 
            )
            # if move.product_id.name=="Bi-Nel MS 3.5 Mtr":
            #     raise UserError(f"{valuations.read()}")
        else:
            
            valuations = self.env['stock.valuation.layer'].search([('product_id','=',move.product_id.id)])
            valuations  = valuations.filtered(lambda x :  x.stock_move_id.id == move.move_id.id and ((x.account_move_id and x.account_move_id.date <= self.to_date) or (not x.account_move_id and x.stock_move_id and x.stock_move_id.move_date.date() <= self.to_date )) or (not x.stock_move_id and move.reference in x.description and not x.reference) or (not x.reference and x.stock_valuation_layer_id and (x.stock_valuation_layer_id.stock_move_id.id == move.move_id.id or move.reference in x.stock_valuation_layer_id.reference)) )
        Valuation_values = valuations.mapped("value")
        return Valuation_values

    def get_report(self, is_excel=False):
        if self.from_date:
            till_date = self.from_date - timedelta(days=1)
            if self.from_date < datetime(2024,7,1).date():
                self.from_date = datetime(2024,7,1).date()
        else:
            # till_date = datetime.now().date() - timedelta(days=1)
            till_date = datetime(2024,7,1).date() - timedelta(days=1)
        
        domain = [('state', '=', 'done')]
        date_filter = 'date'
        if self.location_filter == 'all':
            date_filter = 'move_date'
            
        opening_domain = [('state', '=', 'done'), (date_filter, '<=', till_date)]
        if self.date_filter == 'range' and self.from_date and self.to_date:
            # domain += [('stock_valuation_layer_ids.create_date', '>=', self.from_date), ('stock_valuation_layer_ids.create_date', '<=', self.to_date)]
            domain += [(date_filter, '>=', self.from_date), (date_filter, '<=', self.to_date)]
        else:
            # domain += [('stock_valuation_layer_ids.create_date', '>=', datetime(2024,7,1).date())]
            domain += [(date_filter, '>=', datetime(2024,7,1).date())]
        if self.category_filter == 'manual' and self.category_ids:
            category_domain = [('categ_id', 'in', self.category_ids.ids)]
        else:
            category_domain = []

        if self.product_filter == 'manual':
            category_domain += [('id', 'in', self.product_ids.ids)]
            products = self.env['product.product'].search(category_domain)
            domain += [('product_id.id', 'in', self.product_ids.ids)]
            opening_domain += [('product_id.id', 'in', self.product_ids.ids)]
        elif self.product_filter == 'all':
            products = self.env['product.product'].search(category_domain)
        else:
            start_ref = self.from_product.default_code
            end_ref = self.to_product.default_code
            products = self.env['product.product'].search([('default_code', '>=', start_ref), ('default_code', '<=', end_ref)])
            domain += [('product_id.id', 'in', products.ids)]
            opening_domain += [('product_id.id', 'in', products.ids)]

        def get_nested_attr(obj, attr_path):
            attrs = attr_path.split(".")  
            for attr in attrs:
                obj = getattr(obj, attr)
            return obj

        products = products.sorted(key=lambda product: product.default_code or "", reverse=False)
        start_ref = products[0].default_code if len(products) > 0 else ""
        end_ref = products[-1].default_code if len(products) > 0 else ""
        qty_var = "product_uom_qty"
        price_var = "price_unit"
        if self.location_filter == 'all':
            stock_moves = self.env['stock.move'].search(domain)
            stock_moves_opening = self.env['stock.move'].search(opening_domain)
        elif self.location_filter == 'manual' and self.location_ids:
            domain += [('move_id','!=',False)]
            opening_domain += [('move_id','!=',False)]
            stock_moves = self.env['stock.move.line'].search(domain)
            stock_moves_opening = self.env['stock.move.line'].search(opening_domain)
            qty_var = "qty_done"
            price_var = "move_id.price_unit"

        
        product_data = {}
        for product in products:
            product_stock_moves = stock_moves.filtered(lambda move: move.product_id.id == product.id).sorted(key=lambda product_move:getattr(product_move,date_filter), reverse=False)
                # key=lambda product_move: product_move.stock_valuation_layer_ids[0].create_date if product_move.stock_valuation_layer_ids else product_move.date, reverse=False)
            _logger.info(f"Stock move for product {product.id}: {product_stock_moves}")
            # if not product_stock_moves:
            #     continue  # Skip products with no stock moves
            if self.location_filter == 'manual' and self.location_ids:
                out_moves = product_stock_moves.filtered(
                    lambda x: x.location_id.id in self.location_ids.ids)
                in_moves = product_stock_moves.filtered(
                    lambda x: x.location_dest_id.id in self.location_ids.ids)
            else:
                out_moves = product_stock_moves.filtered(
                    lambda x: (
                        (x.location_id.usage in ['internal', 'transit'] and x.location_dest_id.usage not in ['internal', 'transit']) 
                        or ('RTN-VEN' in (x.reference or ''))
    )
)
                in_moves = product_stock_moves.filtered(
                    lambda x: x.location_id.usage not in ['internal', 'transit'] and x.location_dest_id.usage in [
                        'internal', 'transit'])
            # Combine in_moves and out_moves, ensuring in_moves are processed first on the same date
            all_moves = in_moves + out_moves
            # all_moves = sorted(all_moves, key=lambda move: (move.stock_valuation_layer_ids[0].create_date if move.stock_valuation_layer_ids else move.date , move.location_id.usage == 'internal'))
            all_moves = sorted(all_moves, key=lambda move: (getattr(move,date_filter) , move.location_id.usage == 'internal'))
            
            # opening moves
            opening_stock_moves = stock_moves_opening.filtered(lambda move: move.product_id.id == product.id)


            if self.location_filter == 'manual' and self.location_ids:
                opening_out_moves = opening_stock_moves.filtered(
                    lambda x: x.location_id.id in self.location_ids.ids)
                opening_in_moves = opening_stock_moves.filtered(
                    lambda x: x.location_dest_id.id in self.location_ids.ids)
            else:
                opening_out_moves = opening_stock_moves.filtered(
                    lambda x: x.location_id.usage in ['internal', 'transit'] and x.location_dest_id.usage not in [
                        'internal', 'transit'] or 'RTN-VEN' in (x.reference or ''))
                opening_in_moves = opening_stock_moves.filtered(
                    lambda x: x.location_id.usage not in ['internal', 'transit'] and x.location_dest_id.usage in [
                        'internal', 'transit'])
            
            
            opening_qty = sum(opening_in_moves.mapped(qty_var)) - sum(
                opening_out_moves.mapped(qty_var))
            valuation = sum(map(lambda move: sum(self.Valuation_values_gen(move)),opening_out_moves)) + sum(map(lambda move: sum(self.Valuation_values_gen(move)),opening_in_moves))

            rate = round(abs(valuation / opening_qty), 4) if abs(opening_qty) > 0 else 0
            moves_data = []

            total_in_qty = 0
            total_in_rate = 0
            total_in_amount = 0

            total_out_qty = 0
            total_out_rate = 0
            total_out_amount = 0

            total_closing_qty = 0
            total_closing_rate = 0
            total_closing_amount = 0

            for move in all_moves:
                # out moves condition
                if self.location_filter == 'manual' and self.location_ids:
                    out_cond = move.location_id.id in self.location_ids.ids
                else:
                    out_cond = move.location_id.usage in ['internal', 'transit'] and move.location_dest_id.usage not in [
                    'internal', 'transit'] or 'RTN-VEN' in (move.reference or '')
                # in moves condition
                if self.location_filter == 'manual' and self.location_ids:
                    in_cond = move.location_dest_id.id in self.location_ids.ids
                else:
                    in_cond = move.location_id.usage not in ['internal', 'transit'] and move.location_dest_id.usage in [
                    'internal', 'transit']
                if out_cond:
                    valuation_out = abs(sum(self.Valuation_values_gen_closing(move)))
                    
                    if len(moves_data) == 0:
                        closing_qty = opening_qty - getattr(move, qty_var)
                        closing_amount = valuation - valuation_out
                        closing_rate = abs(closing_amount / closing_qty) if abs(closing_qty) > 0 else 0
                    else:
                        prior_move = moves_data[-1]
                        closing_qty = prior_move['closing_qty'] - getattr(move,qty_var)
                        closing_amount = prior_move['closing_amount'] - valuation_out
                        closing_rate = abs(closing_amount / closing_qty) if abs(closing_qty) > 0 else 0

                    total_closing_qty = closing_qty
                    total_closing_rate = closing_rate
                    total_closing_amount = closing_amount

                    total_out_qty += getattr(move,qty_var)
                    total_out_amount += valuation_out
                    total_out_rate += abs(total_out_amount /  total_out_qty) if abs(total_out_qty) > 0 else 0
                    

                    moves_data.append({
                        # 'date': move.stock_valuation_layer_ids[0].create_date if move.stock_valuation_layer_ids else move.date,         #Aneeq 43,526
                        'date': getattr(move,date_filter),         #Aneeq 43,526
                        'reference': move.reference,
                        'product_name': move.product_id.name,
                        'product_type': move.product_id.type,
                        'product_category': move.product_id.categ_id.name,
                        'location_from': move.location_id.name,
                        'location_to': move.location_dest_id.name,
                        'rate': valuation_out / getattr(move,qty_var) if getattr(move,qty_var) else 0 ,
                        'in_quantity': 0,
                        'amount_in': 0,
                        'out_quantity': round(getattr(move,qty_var), 4),
                        'out_amount': valuation_out,
                        'closing_qty': round(closing_qty, 4),
                        'closing_rate': closing_rate,
                        'closing_amount': round(closing_amount, 4),
                    })
                
                elif in_cond:
                    valuation_in = abs(sum(self.Valuation_values_gen_closing(move)))
                    if len(moves_data) == 0:
                        closing_qty = opening_qty + getattr(move,qty_var)
                        closing_amount = valuation + valuation_in
                        closing_rate = abs(closing_amount / closing_qty) if abs(closing_qty) > 0 else 0
                    else:
                        prior_move = moves_data[-1]
                        closing_qty = prior_move['closing_qty'] + getattr(move,qty_var)
                        closing_amount = prior_move['closing_amount'] + valuation_in
                        closing_rate = abs(closing_amount / closing_qty) if abs(closing_qty) > 0 else 0

                    moves_data.append({
                        # 'date': move.stock_valuation_layer_ids[0].create_date if move.stock_valuation_layer_ids else move.date,
                        'date':getattr(move,date_filter),
                        'reference': move.reference,
                        'product_name': move.product_id.name,
                        'product_type': move.product_id.type,
                        'product_category': move.product_id.categ_id.name,
                        'location_from': move.location_id.name,
                        'location_to': move.location_dest_id.name,
                        'rate': valuation_in / getattr(move,qty_var) if getattr(move,qty_var) else 0,
                        'in_quantity': round(getattr(move,qty_var), 4),
                        'amount_in': valuation_in,
                        'out_quantity': 0,
                        'out_amount': 0,
                        'closing_qty': round(closing_qty, 4),
                        'closing_rate': closing_rate,
                        'closing_amount': round(closing_amount, 4),
                    })
                    # if move.product_id.name=='Bi-Nel MS 3.5 Mtr':
                    #     raise UserError(f"elif {valuation_in} {getattr(move,qty_var)}")
            
            # moves_data = sorted(moves_data, key=lambda x: x['date'])
            for move in moves_data:
                move['date'] = move['date'].date() if isinstance(move['date'],datetime) else move['date']
            # if len(moves_data) == 0:
            #     continue
            final_moves_data = {}
            for move in moves_data:
                total_closing_qty = move.get('closing_qty', 0)
                total_closing_amount = move.get('closing_amount', 0)
                total_closing_rate = move.get('closing_rate', 0)

                total_in_qty += move.get('in_quantity', 0)
                total_in_amount += move.get('amount_in', 0)
                total_in_rate += (total_in_amount / total_in_qty) if abs(total_in_qty) > 0 else 0
                key_par = f'{move.get("date")}_{move.get("reference")}'
                if key_par not in final_moves_data.keys():
                    final_moves_data[key_par] = move
                    continue
                final_moves_data[key_par]['in_quantity'] += move.get('in_quantity', 0)
                final_moves_data[key_par]['out_quantity'] += move.get('out_quantity', 0)
                final_moves_data[key_par]['amount_in'] += move.get('amount_in', 0)
                final_moves_data[key_par]['out_amount'] += move.get('out_amount', 0)
                final_moves_data[key_par]['closing_qty'] = move.get('closing_qty', 0)
                final_moves_data[key_par]['closing_rate'] = move.get('closing_rate', 0)
                final_moves_data[key_par]['closing_amount'] = move.get('closing_amount', 0)
                final_moves_data[key_par]['rate'] = (final_moves_data[key_par]['amount_in'] + final_moves_data[key_par]['out_amount']) / (final_moves_data[key_par]['in_quantity'] + final_moves_data[key_par]['out_quantity'])  if (final_moves_data[key_par]['in_quantity'] + final_moves_data[key_par]['out_quantity']) > 0 else 0
            moves_data = list(final_moves_data.values())
            moves_data = sorted(moves_data, key=lambda x: x['date'])
            if len(moves_data) == 0 and opening_qty == 0 and valuation == 0:
                continue
            product_data[product.id] = {
                "uom": product.uom_id.name,
                "opening": [product.default_code, product.name, rate, opening_qty, valuation],
                "moves": moves_data,
                "total": {
                    'total_in_qty': round(total_in_qty, 4),
                    'total_in_amount': round(total_in_amount, 4),
                    'total_in_rate': total_in_rate / len(in_moves) if len(in_moves) > 0 else 0,
                    'total_out_qty': round(total_out_qty, 4),
                    'total_out_amount': round(total_out_amount, 4),
                    'total_out_rate': total_out_rate / len(out_moves) if len(out_moves) > 0 else 0,
                    'total_closing_qty': total_closing_qty if total_closing_qty > 0 else opening_qty,
                    'total_closing_amount': total_closing_amount if total_closing_amount >= 0 else valuation,
                    'total_closing_rate': total_closing_rate if total_closing_rate > 0 else round(valuation/opening_qty,2) if opening_qty > 0 and valuation > 0  else 0,
                }
            }
            # raise UserError(f"{total_closing_amount if total_closing_amount > 0 else valuation} {total_closing_amount} {total_closing_amount>0}")
        # raise UserError(f"{product_data}")
        grand_total = {key: 0 for key in [
            'total_in_qty', 'total_in_amount', 'total_in_rate',
            'total_out_qty', 'total_out_amount', 'total_out_rate',
            'total_closing_qty', 'total_closing_amount', 'total_closing_rate'
        ]}
        # p1=product_data

        for data in product_data.values():
            for key in grand_total:
                grand_total[key] += data['total'][key]

        data = {
            'doc_ids': self.ids,
            'doc_model': 'product.ledger.report.wizard',
            'grouped_data': product_data,
            'grand_total': grand_total,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'start_ref': start_ref,
            'end_ref': end_ref,
        }
        # raise UserError(str(data))

        if not is_excel:
            return self.env.ref('product_ledger_report.product_ledger_action').report_action(self, data=data)
        else:
            return data
