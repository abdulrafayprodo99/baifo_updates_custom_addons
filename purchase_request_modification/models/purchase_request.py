from odoo import models,fields,api
from odoo.exceptions import UserError

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.specifications = self.product_id.product_tmpl_id.product_specification


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    purchase_order_created = fields.Boolean(
        string='Purchase Order Created', 
        compute='_compute_purchase_order_created', 
        store=True
    )
    @api.depends('line_ids.purchase_lines')  
    def _compute_purchase_order_created(self):
        for record in self:
            if record.line_ids.purchase_lines:
                record.purchase_order_created = True
            else:
                record.purchase_order_created = False