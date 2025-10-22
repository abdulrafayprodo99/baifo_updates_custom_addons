from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _inherit = "purchase.request.line"

    po_unit_price = fields.Float(
        string="PO Unit Price",
        compute="_compute_po_unit_price",
        store=True
    )
    
    @api.depends('purchase_order_id', 'product_id')
    def _compute_po_unit_price(self):
        for line in self:
            if line.purchase_order_id and line.product_id:
                po_lines = line.purchase_order_id.order_line.filtered(
                    lambda l: l.product_id == line.product_id
                )
                
                if po_lines:
                    if len(po_lines) == 1:
                        line.po_unit_price = po_lines.price_unit
                    else:
                        line.po_unit_price = po_lines[0].price_unit
                else:
                    line.po_unit_price = 0.0
            else:
                line.po_unit_price = 0.0
