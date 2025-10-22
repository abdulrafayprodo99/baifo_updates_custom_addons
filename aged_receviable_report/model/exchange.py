
from odoo import fields, api, models 
class expense(models.Model):
    _inherit='account.move'
    
    reference_name=fields.Char(string="Reference to", )
    
    @api.change9