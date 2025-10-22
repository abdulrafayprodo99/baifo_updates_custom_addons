from odoo import models,fields,api,_
from odoo.exceptions import UserError


class PurchaseRequestLine(models.Model):
    _inherit="purchase.request.line"

    po_ids =  fields.Many2many('purchase.order', string='Purchase Orders')

    