from odoo import models,api,fields,_
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit="stock.picking"

    wr_no =  fields.Many2one("maintenance.request",string="W.R No")
    # fields_separated = fields.Char(
    #     string="Fields Comma Separated",
    #     related='picking_type_id.field_custom',
    #     readonly=True,
    #     store=False,
    # )