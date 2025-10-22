# models/quality_button_team.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    product_uom_id=fields.Many2one('uom.uom',related="product_id.uom_id",readonly="1")


    # @api.depends("product_id")
    # def _compute_uom_id(self):
    #     for rec in self:
    #         raise UserError("hello")
    #         rec.product_uom_id=rec.product_id.uom_id



