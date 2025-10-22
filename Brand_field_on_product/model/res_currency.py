from odoo import models,api,fields,_
from odoo.exceptions import UserError

class  ResCurrency(models.Model):
    _inherit = 'res.currency'

    name = fields.Char(string='Currency', size=10, required=True, help="Currency Code (ISO 4217)")