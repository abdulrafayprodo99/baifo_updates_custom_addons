import io
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import xlwt
from odoo import http
from datetime import datetime,timedelta


#               select Distinct pp.default_code as product_code ,pt.name->'en_US' as product_name,pc.name as product_category ,sl.name as location,stl.name as lot_no,sq.quantity as quantity
# from stock_move sm 
# inner join product_product pp on pp.id =sm.product_id 
# inner join product_template pt on pt.id =pp.product_tmpl_id
# inner join product_category pc on pc.id =pt.categ_id
# inner join stock_quant sq on sq.product_id = pp.id
# inner join stock_location sl on sl.id =sq.location_id
# inner join stock_lot stl on stl.id =sq.lot_id
# where sl.usage='internal' 
# and sm.date between %s and %s
# --and pp.default_code='2-1-0-00-038'



class PendingLcController(http.Controller):

    @http.route('/stock_report_datewise/excel', type='http', auth='user')
    def generate_excel_report(self,date_from,date_to):
        query = """
        SELECT distinct 
sm.date AS date,
       pt.name->'en_US' AS product_name,
       sm.reference as ref,
       pp.default_code AS product_code,
       pc.name AS product_category,
sl.complete_name as location,
slt.name lot_id,
(select sq.quantity from stock_quant sq where sq.lot_id = slt.id and sl.id =sq.location_id)as qty,
sm.product_uom_qty as stock_move_qty

FROM stock_move sm
inner JOIN product_product pp ON sm.product_id = pp.id
inner join product_template pt on pt.id =pp.product_tmpl_id
inner JOIN product_category pc ON pt.categ_id = pc.id
inner join stock_location sl on sl.id = sm.location_dest_id
inner join stock_lot slt on slt.name =sm.x_studio_lot_serial_no
WHERE date(sm.date) >= %s
  AND date(sm.date) <= %s
 --and pp.default_code ='2-5-1-02-001'
and sl.usage='internal'
--and sq.quantity>0

              
                            """
        env = http.request.env
        env.cr.execute(query,(date_from,date_to))
        # env.cr.execute(query)
        records = env.cr.dictfetchall()

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Stock Report')
   
        style = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style.alignment = alignment
        sheet.write_merge(0,0,0,5,'Stock Report',style)

        headers = [
            'Date','Reference','Product Code', 'Product Name', 'Product Category', 'Location', 'Lot Number', 'Current Stock Quantity',
            'Stock Move Quantity'
        ]

        for col, header in enumerate(headers):
            sheet.write(2, col, header)
        # row = 1
        # today = datetime.now()
        for row, record in enumerate(records, start=3):
                sheet.write(row, 0, str(record['date']))
                sheet.write(row, 1, record['ref'])
                sheet.write(row, 2, record['product_code'])
                sheet.write(row, 3, record['product_name'])
                sheet.write(row, 4, record['product_category'])
                sheet.write(row, 5, record['location'])
                sheet.write(row, 6, record['lot_id'])
                sheet.write(row, 7, record['qty'])
                sheet.write(row, 8, record['stock_move_qty'])
                
                # row += 1

                
            

        stream = io.BytesIO()
        workbook.save(stream)
        stream.seek(0)

        report_name = 'Stock Report.xls'
        response = http.request.make_response(
            stream.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', http.content_disposition(report_name))
            ]
        )
        response.set_cookie('fileToken', report_name)
        return response
