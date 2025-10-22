
from odoo import models, api, fields, _
import datetime
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

import xlsxwriter

from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import base64
import io
try:
    import xlwt
except ImportError:
    xlwt = None
    
    
class SaleProjectionReportWizard(models.TransientModel):
    _name="sale.projection.report.wizard"
    _description='Sale Projection Wizard'

    excel_file = fields.Binary('Excel File', readonly=True)
    file_name = fields.Char('Excel File Name', readonly=True)


    def _get_fiscal_year_selection(self):
        """Generate fiscal year options from 10 years ago to 10 years ahead"""
        current_year = datetime.today().year
        return [(str(year), str(year)) for year in range(current_year - 10, current_year + 11)]

    fiscal_year = fields.Selection(
        selection=lambda self: [(year, str(year)) for year in range(datetime.today().year - 10, datetime.today().year + 11)],  
        string="Fiscal Year",
        default=lambda self: datetime.today().year,  
        required=True
    )


    def check_fiscal_year(self):
        try:
            if not self.fiscal_year.isdigit() or len(self.fiscal_year) != 4:
                raise UserError("Invalid year format. Please enter a 4-digit year (eg. 2025 ).")
            
            self.fiscal_year = int(self.fiscal_year)
        except Exception as e:
            raise UserError(e)

    def calculate_fiscal_details(self,input_year):
        # Fiscal year start is July 1 of the previous year
        fiscal_start = date(input_year - 1, 7, 1)
        # Fiscal year end is June 30 of the input year
        fiscal_end = date(input_year, 6, 30)

        # Calculate quarters
        q1_start = fiscal_start
        q1_end = fiscal_start + relativedelta(months=3) - timedelta(days=1)

        q2_start = q1_end + timedelta(days=1)
        q2_end = q2_start + relativedelta(months=3) - timedelta(days=1)

        q3_start = q2_end + timedelta(days=1)
        q3_end = q3_start + relativedelta(months=3) - timedelta(days=1)

        q4_start = q3_end + timedelta(days=1)
        q4_end = fiscal_end

        # raise UserError(f"{q1_start},{q1_end} =={q2_start},{q2_end} =={q3_start},{q3_end} =={q4_start},{q4_end}")
        # Return the results as a dictionary
        return {
            "start": fiscal_start,
            "end": fiscal_end,
            'q1_s':q1_start,
            'q1_e':q1_end,
            'q2_s':q2_start,
            'q2_e':q2_end,
            'q3_s':q3_start,
            'q3_e':q3_end,
            'q4_s':q4_start,
            'q4_e':q4_end,
        }
 

    def get_invoice_totals_by_sectors(self, start_date, end_date):
        """
        Get the sum of all invoices grouped by customer tags within a specific date range using SQL.

        :param start_date: Start date (string in 'YYYY-MM-DD' format)
        :param end_date: End date (string in 'YYYY-MM-DD' format)
        :return: Dictionary with tag names as keys and invoice totals as values
        """
        query = """
            SELECT 
                category.name AS tag_name,
                SUM(move.amount_untaxed_signed) AS total
            FROM 
                account_move move
            JOIN 
                res_partner partner ON move.partner_id = partner.id
            JOIN 
                res_partner_res_partner_category_rel rel ON partner.id = rel.partner_id
            JOIN 
                res_partner_category category ON rel.category_id = category.id
            WHERE 
                move.move_type = 'out_invoice' AND 
                move.state = 'posted' AND 
                move.date BETWEEN %s AND %s
            GROUP BY 
                category.name
        """
        self.env.cr.execute(query, (start_date, end_date))
        result = self.env.cr.dictfetchall()

        return result

        
    def get_data(self):
        fiscal_year= self.calculate_fiscal_details(int(self.fiscal_year))
        departments= self.env['res.partner.category'].search([])
        department_dict = {
            department.name: {'annual_target': 0,'annual_sales': 0, 'q1_target': 0,'q1_sales': 0,'q2_target': 0,'q2_sales': 0,'q3_target': 0,'q3_sales': 0,'q4_target': 0,'q4_sales': 0,'is_anually': False,'is_quaterly':False}
            for department in departments
        }

        targets= self.env['sales.segment.target'].search([('validate_from','>=',fiscal_year['start']),('validate_to','<=',fiscal_year['end'])])
        for target in targets:
            if department_dict[target.tag.name]['is_anually']==True:
                continue
            if target.validate_from == fiscal_year['start'] and target.validate_to == fiscal_year['end'] and department_dict[target.tag.name]['is_quaterly']==False:
                quarter_target= target.target/4
                department_dict[target.tag.name]['annual_target']= target.target
                department_dict[target.tag.name]['q1_target']= quarter_target
                department_dict[target.tag.name]['q2_target']= quarter_target
                department_dict[target.tag.name]['q3_target']= quarter_target
                department_dict[target.tag.name]['q4_target']= quarter_target

                department_dict[target.tag.name]['is_anually'] = True

            
            elif target.validate_from == fiscal_year['q1_s'] and target.validate_to == fiscal_year['q1_e'] and department_dict[target.tag.name]['q1_target']==0:
                department_dict[target.tag.name]['annual_target'] += target.target
                department_dict[target.tag.name]['q1_target']= target.target

                department_dict[target.tag.name]['is_quaterly'] = True 

            elif target.validate_from == fiscal_year['q2_s'] and target.validate_to == fiscal_year['q2_e'] and department_dict[target.tag.name]['q2_target']==0:
                department_dict[target.tag.name]['annual_target'] += target.target
                department_dict[target.tag.name]['q2_target']= target.target

                department_dict[target.tag.name]['is_quaterly'] = True 

            elif target.validate_from == fiscal_year['q3_s'] and target.validate_to == fiscal_year['q3_e'] and department_dict[target.tag.name]['q3_target']==0:
                department_dict[target.tag.name]['annual_target'] += target.target
                department_dict[target.tag.name]['q3_target']= target.target

                department_dict[target.tag.name]['is_quaterly'] = True 

            elif target.validate_from == fiscal_year['q4_s'] and target.validate_to == fiscal_year['q4_e'] and department_dict[target.tag.name]['q4_target']==0:
                department_dict[target.tag.name]['annual_target'] += target.target
                department_dict[target.tag.name]['q4_target']= target.target

                department_dict[target.tag.name]['is_quaterly'] = True 

        invoice_total_annual= self.get_invoice_totals_by_sectors(fiscal_year['start'],fiscal_year['end'])
        invoice_total_q1= self.get_invoice_totals_by_sectors(fiscal_year['q1_s'],fiscal_year['q1_e'])
        invoice_total_q2= self.get_invoice_totals_by_sectors(fiscal_year['q2_s'],fiscal_year['q2_e'])
        invoice_total_q3= self.get_invoice_totals_by_sectors(fiscal_year['q3_s'],fiscal_year['q3_e'])
        invoice_total_q4= self.get_invoice_totals_by_sectors(fiscal_year['q4_s'],fiscal_year['q4_e'])

        for i in range(len(invoice_total_annual)):

            # raise UserError(str(invoice_total_annual[i]))
            if i < len(invoice_total_annual):
                department_dict[invoice_total_annual[i]['tag_name']['en_US']]['annual_sales']= invoice_total_annual[i]['total']
            if i < len(invoice_total_q1):
                department_dict[invoice_total_q1[i]['tag_name']['en_US']]['q1_sales']= invoice_total_q1[i]['total']
            if i < len(invoice_total_q2):
                department_dict[invoice_total_q2[i]['tag_name']['en_US']]['q2_sales']= invoice_total_q2[i]['total']
            if i < len(invoice_total_q3):
                department_dict[invoice_total_q3[i]['tag_name']['en_US']]['q3_sales']= invoice_total_q3[i]['total']
            if i < len(invoice_total_q4):
                department_dict[invoice_total_q4[i]['tag_name']['en_US']]['q4_sales']= invoice_total_q4[i]['total']
    


        # raise UserError(str(department_dict))


        totals = {
            'annual_target': 0,
            'annual_sales': 0,
            'q1_target': 0,
            'q1_sales': 0,
            'q2_target': 0,
            'q2_sales': 0,
            'q3_target': 0,
            'q3_sales': 0,
            'q4_target': 0,
            'q4_sales': 0,
        }


        for sector, total in department_dict.items():
            for key in totals.keys():
                totals[key] += total[key]

        return department_dict,totals
        

    def _get_report_name(self):
        return "Sale Projection"
    
    def create_sale_projection_pdf(self):
        self.check_fiscal_year()
        # self.get_data()

        return self.env.ref('ol_sale_projection_report.ol_sale_projection_report_action').report_action(self) 
    def calculate_percentage(self, total, target):
        try:
            return round((total / target) * 100, 2)
        except:
            return 0.0

    def print_excel_report(self):
        self.check_fiscal_year()
        
        data, totals =self.get_data()
        if not data:
            raise UserError('No data found')


        excel_encode = io.BytesIO()
  
        filename = "Sale Projection Report - " + str(datetime.now().strftime("%d-%m-%Y"))+".xlsx"
        workbook = xlsxwriter.Workbook(excel_encode)
        sheet = workbook.add_worksheet('Sales Projection Report')
        header = workbook.add_format({'bold': True, 'align':'center','size': 11,'bg_color': '#d9d4d4'})
        right_header = workbook.add_format({ 'align':'right','size': 11,'bg_color': '#d9d4d4'})
        customer_style = workbook.add_format({'bold': True, 'align':'center','size': 11})
        customer_style_without_bold = workbook.add_format({ 'align':'center','size': 11})
        first_row_style= workbook.add_format({'bold': True, 'align':'center','size': 13,'font_color':'blue'})
        header.set_border()
        right_header.set_border()
        normal_text = workbook.add_format({'align':'right','size':11})
        normal_text_with_top = workbook.add_format({'align':'center','size':11,'top': 5})
        

        current_time= datetime.now().strftime('%I:%M %p')
        current_date = datetime.today().strftime('%Y-%m-%d')

        for i in range(0,13):
            sheet.set_column(0,i,15)

        row = 0 
        sheet.write( row , 0, 'SALES TARGET VS ACTUAL SALES')
        row += 1 
        sheet.write( row , 0 , f'UPTO :{current_date}')
        # sheet.write( row , 1, current_date)
        row += 1
        sheet.write(row ,0, 'Sector', header)

        sheet.merge_range(row ,1,row,2,'Annual Comparison' ,header)  
        sheet.merge_range(row,3,row,10,'Quarterly Comparison' ,header) 
        row +=1  
        sheet.write(row ,1, 'Annual Target', header)
        sheet.write(row ,2, 'Annual Sale', header)
        sheet.merge_range(row ,3,row ,4,'Q1' ,header)
        sheet.merge_range(row ,5,row ,6,'Q2' ,header)
        sheet.merge_range(row ,7,row,8,'Q3' ,header)
        sheet.merge_range(row ,9,row,10,'Q4' ,header)
        row+= 1 
        sheet.write(row ,3, 'Projected Sales', header)
        sheet.write(row ,4, 'Actual Sales', header)
        sheet.write(row ,5, 'Projected Sales', header)
        sheet.write(row ,6, 'Actual Sales', header)
        sheet.write(row ,7, 'Projected Sales', header)
        sheet.write(row ,8, 'Actual Sales', header)
        sheet.write(row ,9, 'Projected Sales', header)
        sheet.write(row ,10, 'Actual Sales', header)
        row += 1
        inv_row= row 
        # customers= self.get_customers()

        grand_total_amount=0
        grand_total_quantity=0

        sectors_subtotal = {
            'annual_target': 0,
            'annual_sales': 0,
            'q1_target': 0,
            'q1_sales': 0,
            'q2_target': 0,
            'q2_sales': 0,
            'q3_target': 0,
            'q3_sales': 0,
            'q4_target': 0,
            'q4_sales': 0
        }
        foreign_export_total = None
        for sector, total in data.items():
            if sector != 'Foreign Export':
                sheet.write(inv_row,0,sector,normal_text)
                sheet.write(inv_row,1,f"{total['annual_target']:,.2f}",normal_text)
                sheet.write(inv_row,2,f"{total['annual_sales']:,.2f}",normal_text)
                sheet.write(inv_row,3,f"{total['q1_target']:,.2f}",normal_text)
                sheet.write(inv_row,4,f"{total['q1_sales']:,.2f}",normal_text)
                sheet.write(inv_row,5,f"{total['q2_target']:,.2f}",normal_text)
                sheet.write(inv_row,6,f"{total['q2_sales']:,.2f}",normal_text)
                sheet.write(inv_row,7,f"{total['q3_target']:,.2f}",normal_text)
                sheet.write(inv_row,8,f"{total['q3_sales']:,.2f}",normal_text)
                sheet.write(inv_row,9,f"{total['q4_target']:,.2f}",normal_text)
                sheet.write(inv_row,10,f"{total['q4_sales']:,.2f}",normal_text)
                inv_row += 1
                sectors_subtotal['annual_target'] += total['annual_target']
                sectors_subtotal['annual_sales'] += total['annual_sales']
                sectors_subtotal['q1_target'] += total['q1_target']
                sectors_subtotal['q1_sales'] += total['q1_sales']
                sectors_subtotal['q2_target'] += total['q2_target']
                sectors_subtotal['q2_sales'] += total['q2_sales']
                sectors_subtotal['q3_target'] += total['q3_target']
                sectors_subtotal['q3_sales'] += total['q3_sales']
                sectors_subtotal['q4_target'] += total['q4_target']
                sectors_subtotal['q4_sales'] += total['q4_sales']
            else:   
                foreign_export_total = total

        sheet.write(inv_row,0, 'Subtotal', header)
        sheet.write(inv_row,1,f"{sectors_subtotal['annual_target']:,.2f}",right_header)
        sheet.write(inv_row,2,f"{sectors_subtotal['annual_sales']:,.2f}",right_header)
        sheet.write(inv_row,3,f"{sectors_subtotal['q1_target']:,.2f}",right_header)
        sheet.write(inv_row,4,f"{sectors_subtotal['q1_sales']:,.2f}",right_header)
        sheet.write(inv_row,5,f"{sectors_subtotal['q2_target']:,.2f}",right_header)
        sheet.write(inv_row,6,f"{sectors_subtotal['q2_sales']:,.2f}",right_header)
        sheet.write(inv_row,7,f"{sectors_subtotal['q3_target']:,.2f}",right_header)
        sheet.write(inv_row,8,f"{sectors_subtotal['q3_sales']:,.2f}",right_header)
        sheet.write(inv_row,9,f"{sectors_subtotal['q4_target']:,.2f}",right_header)
        sheet.write(inv_row,10,f"{sectors_subtotal['q4_sales']:,.2f}",right_header)
        inv_row += 1

        if foreign_export_total:
            sheet.write(inv_row, 0, 'Foreign Export', normal_text)
            sheet.write(inv_row, 1, f"{foreign_export_total['annual_target']:,.2f}", normal_text)
            sheet.write(inv_row, 2, f"{foreign_export_total['annual_sales']:,.2f}", normal_text)
            sheet.write(inv_row, 3, f"{foreign_export_total['q1_target']:,.2f}", normal_text)
            sheet.write(inv_row, 4, f"{foreign_export_total['q1_sales']:,.2f}", normal_text)
            sheet.write(inv_row, 5, f"{foreign_export_total['q2_target']:,.2f}", normal_text)
            sheet.write(inv_row, 6, f"{foreign_export_total['q2_sales']:,.2f}", normal_text)
            sheet.write(inv_row, 7, f"{foreign_export_total['q3_target']:,.2f}", normal_text)
            sheet.write(inv_row, 8, f"{foreign_export_total['q3_sales']:,.2f}", normal_text)
            sheet.write(inv_row, 9, f"{foreign_export_total['q4_target']:,.2f}", normal_text)
            sheet.write(inv_row, 10, f"{foreign_export_total['q4_sales']:,.2f}", normal_text)
            inv_row += 1

            sheet.write(inv_row,0, 'Subtotal', header)

            sheet.write(inv_row,1,f"{foreign_export_total['annual_target']:,.2f}",right_header)
            sheet.write(inv_row,2,f"{foreign_export_total['annual_sales']:,.2f}",right_header)
            sheet.write(inv_row,3,f"{foreign_export_total['q1_target']:,.2f}",right_header)
            sheet.write(inv_row,4,f"{foreign_export_total['q1_sales']:,.2f}",right_header)
            sheet.write(inv_row,5,f"{foreign_export_total['q2_target']:,.2f}",right_header)
            sheet.write(inv_row,6,f"{foreign_export_total['q2_sales']:,.2f}",right_header)
            sheet.write(inv_row,7,f"{foreign_export_total['q3_target']:,.2f}",right_header)
            sheet.write(inv_row,8,f"{foreign_export_total['q3_sales']:,.2f}",right_header)
            sheet.write(inv_row,9,f"{foreign_export_total['q4_target']:,.2f}",right_header)
            sheet.write(inv_row,10,f"{foreign_export_total['q4_sales']:,.2f}",right_header)

            inv_row+=1

        
        sheet.write(inv_row,0, 'Grand Total', header)
        sheet.write(inv_row,1,f"{totals['annual_target']:,.2f}",right_header)
        sheet.write(inv_row,2,f"{totals['annual_sales']:,.2f}",right_header)
        sheet.write(inv_row,3,f"{totals['q1_target']:,.2f}",right_header)
        sheet.write(inv_row,4,f"{totals['q1_sales']:,.2f}",right_header)
        sheet.write(inv_row,5,f"{totals['q2_target']:,.2f}",right_header)
        sheet.write(inv_row,6,f"{totals['q2_sales']:,.2f}",right_header)
        sheet.write(inv_row,7,f"{totals['q3_target']:,.2f}",right_header)
        sheet.write(inv_row,8,f"{totals['q3_sales']:,.2f}",right_header)
        sheet.write(inv_row,9,f"{totals['q4_target']:,.2f}",right_header)
        sheet.write(inv_row,10,f"{totals['q4_sales']:,.2f}",right_header)

        inv_row+=1
        sheet.write(inv_row,0, 'Target Achieved %', header)

        sheet.merge_range(inv_row,1,inv_row,2, str(self.calculate_percentage(totals['annual_sales'],totals['annual_target']))+' %',right_header)
        sheet.merge_range(inv_row,3,inv_row,4, str(self.calculate_percentage(totals['q1_sales'],totals['q1_target']))+' %',right_header)
        sheet.merge_range(inv_row,5,inv_row,6, str(self.calculate_percentage(totals['q2_sales'],totals['q2_target']))+' %',right_header)
        sheet.merge_range(inv_row,7,inv_row,8, str(self.calculate_percentage(totals['q3_sales'],totals['q3_target']))+' %',right_header)
        sheet.merge_range(inv_row,9,inv_row,10,str(self.calculate_percentage(totals['q4_sales'],totals['q4_target']))+' %',right_header)



        inv_row+=1

        workbook.close()
        excel_data = excel_encode.getvalue()
        encoded_excel_data = base64.b64encode(excel_data).decode()
        # self.excel_file= encoded_excel_data
        # self.file_name= filename

        export_id = self.env['sale.projection.report.wizard'].create({'fiscal_year':self.fiscal_year,'excel_file':encoded_excel_data, 'file_name': filename})
        res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'sale.projection.report.wizard',
                'type': 'ir.actions.act_window',
                'target':'new'
            }
        return res


   
    
# class customer_invoices_report_excel(models.TransientModel):
#     _name = "customer.statement.report.excel"
#     _description = "Customer Statement Report Excel"
    
#     excel_file = fields.Binary('Customer Statement Report')
#     file_name = fields.Char('Excel File', size=64)