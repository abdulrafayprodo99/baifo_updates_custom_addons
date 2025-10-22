from odoo import _, api, fields, models
from odoo.exceptions import UserError
import base64



class StockReportWizard(models.TransientModel):
    _name = 'stock.report.datewise'
    _description = 'Stock Report Date Wise'
    date_from = fields.Date( string="Date From")
    date_to = fields.Date( string="Date To")
    
    
    def generate_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url' :'/stock_report_datewise/excel?date_from={}&date_to={}'.format(self.date_from,self.date_to),
            'target': 'self',
        }
    


