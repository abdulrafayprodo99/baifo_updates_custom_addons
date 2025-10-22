from odoo import models,fields,api,_
from odoo.exceptions import UserError


class PurchaseRequestLine(models.Model):
    _inherit="purchase.request.line"

    available_qty = fields.Float(string='Qty On Hand', related="product_id.qty_available", readonly=True, store=True)

    