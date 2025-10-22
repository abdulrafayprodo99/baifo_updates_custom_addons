from odoo import models,fields,api,SUPERUSER_ID,_
from odoo.exceptions import UserError,ValidationError



class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    description = fields.Char(string="Description", required=False)



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    name = fields.Char(
        
        string='Description', readonly=False)