import io
import base64
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError

class OrderPointReportServerAction(models.Model):
    _inherit = 'stock.warehouse.orderpoint'


    @api.model
    def send_safety_stock_report(self):
        orderpoints = self.search([]) 
        
        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Order Points')
        bold_format = workbook.add_format({'bold': True})

        headers = ['Product','UoM' ,'On Hand Qty','Forcasted Qty' ,'Safety Stock Level Qty']

        worksheet.write(0, 0, "Biafo Industries Limited",bold_format)
        worksheet.write(1, 0, "Saftey Stock Report",bold_format)
        worksheet.write_row(2, 0, headers,bold_format)

        row = 3
        for orderpoint in orderpoints:
            product = orderpoint.product_id  
            uom = orderpoint.product_uom_name
            on_hand = orderpoint.onhand  
            forcasted_qty = orderpoint.forecast_quantity
            safety_level = orderpoint.final_safety_stock_level  
            
            if on_hand <safety_level:
                worksheet.write(row, 0, product.name)  
                worksheet.write(row, 1, uom)  
                worksheet.write(row, 2, round(on_hand,2))  
                worksheet.write(row, 3, round(forcasted_qty,2))  
                worksheet.write(row, 4, round(safety_level,2))  
                row += 1

        workbook.close()
        excel_data = output.getvalue()
        excel_base64 = base64.b64encode(excel_data).decode('utf-8')
        recipients = [
            'naveed.afzal@biafo.com', 
            'stores@biafo.com', 
            'shahbab.azam@biafo.com', 
            'import@biafo.com', 
            'purchase@Biafo.com',
            'sajid.hussain@biafo.com', 
            'shaiq.tanveer@biafo.com',
            'shahbab.azam@biafo.com',
        ]
        for recipient in recipients:
            email_values = {
                'subject': 'Safety Stock Level Report – Action Required for Stock Replenishment',
                'body_html': f"""
                    <p>Dear Team,</p>
                    <p>Please find attached the Safety Stock Level Report, in Excel format, for your reference and necessary action.</p>
                    <p>This report highlights the list of Stock Items where the On-hand Quantity has fallen below the defined Safety Stock Levels. Kindly review the attached list and initiate replenishment actions as per your respective responsibilities to maintain adequate stock safety margins and avoid potential stockouts.</p>
                    <p>Should you have any questions or require further clarification, please feel free to contact the undersigned.</p>
                    <p>Best Regards,</p>
                    <p>Odoo</p>
                """,  # Using the part before '@' as the recipient's name
                'email_to': recipient,  # The recipient's email
                'attachment_ids': [(0, 0, {
                    'name': 'safety_stock_level_report.xlsx',
                    'datas': excel_base64,
                    'type': 'binary',
                })],
            }

    # Send email logic here using the email_values for each recipient


            mail = self.env['mail.mail'].create(email_values)
            mail.send()

        return True


    @api.model
    def send_orderpoint_report_excel(self):
        # Get the order points to include in the report
        orderpoints = self.search([])  # Adjust the filter as needed
        
        # Create an in-memory file object
        output = io.BytesIO()

        # Create a workbook and a worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Order Points')
        bold_format = workbook.add_format({'bold': True})

        # Define headers for the Excel report
        headers = ['Product','UoM' ,'On Hand', 'Forcasted Qty','Reorder Level']

        worksheet.write(0, 0, "Biafo Industries Limited",bold_format)
        worksheet.write(1, 0, "Reordering Rules Report",bold_format)
        worksheet.write_row(2, 0, headers,bold_format)

        # Add data for each order point
        row = 3
        for orderpoint in orderpoints:
            product = orderpoint.product_id  # Product field
            on_hand = orderpoint.onhand  # On hand quantity of the product
            reorder_level = orderpoint.reorder_level  # Reorder level
            uom = orderpoint.product_uom_name
            forcasted_qty = orderpoint.forecast_quantity
            
            # reorder_diff = reorder_level - on_hand  # Reorder level minus on hand quantity
            if on_hand <reorder_level:
                worksheet.write(row, 0, product.name)  # Product Name
                worksheet.write(row, 1, uom)  
                worksheet.write(row, 2, round(on_hand,2))  # On Hand Quantity
                worksheet.write(row, 3, round(forcasted_qty,2))  
                worksheet.write(row, 4, round(reorder_level,2))  # Reorder Level
                # worksheet.write(row, 3, reorder_diff)  # Reorder Level - On Hand
                row += 1

        # Close the workbook and write the content to the BytesIO stream
        workbook.close()

        # Get the Excel file content
        excel_data = output.getvalue()

        # Encode the file in base64
        excel_base64 = base64.b64encode(excel_data).decode('utf-8')
        recipients = [
            'naveed.afzal@biafo.com',
            'stores@biafo.com',
            'shahbab.azam@biafo.com',
            'import@biafo.com',
            'purchase@Biafo.com',
            'sajid.hussain@biafo.com',
            'shaiq.tanveer@biafo.com',
            'shahbab.azam@biafo.com',
            'hassan.zahid@odolution.com',
        ]

        for recipient in recipients:
            email_values = {
                'subject': 'Warehouse Re-Order Level Report – Action Required for Stock Replenishment',
                'body_html': f"""
                    <p>Dear Team,</p>
                    <p>Please find attached the Warehouse Re-Order Level Report, in Excel format, for your reference and necessary action.</p>
                    <p>This report highlights the list of Stock Items where the On-hand Quantity has fallen below the defined Re-Order Levels. Kindly review the attached list and initiate replenishment actions as per your respective responsibilities to ensure smooth stock availability.</p>
                    <p>Should you have any questions or require further clarification, please feel free to contact the undersigned.</p>
                    <p>Best Regards,</p>
                    <p>Odoo</p>
                """,  # Using the part before '@' as the recipient's name
                'email_to': recipient,  # The recipient's email
                'attachment_ids': [(0, 0, {
                    'name': 'reorder_level_report.xlsx',
                    'datas': excel_base64,
                    'type': 'binary',
                })],
            }
            mail = self.env['mail.mail'].create(email_values)
            mail.send()

        return True
