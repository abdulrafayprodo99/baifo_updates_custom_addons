from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime
class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    # def make_purchase_order(self):
    #     for rec in self.item_ids:
    #         match=self.item_ids[0].request_id.line_ids.filtered(lambda line : line.product_id.id == rec.product_id.id)
    #         if match:
    #             # raise UserError(f"{match.quantity_track} and {rec.product_qty}")
    #             if match.product_qty < match.quantity_track +rec.product_qty:
    #                 raise UserError(f"{rec.product_id.name} quantity can't be exceeded more than present on purchase request ")
    #             else:
    #                 match.quantity_track+=rec.product_qty
    #     res = super(PurchaseRequestLineMakePurchaseOrder,self).make_purchase_order()

    #     return res

    # def make_purchase_order(self):
    #     for rec in self.item_ids:
    #         remaining_qty = 0
    #         purchase_order = self.env['purchase.order'].search([('purchase_request_id', '=', rec.request_id.id), ('partner_id','=',self.supplier_id.id)])
    #         for po in purchase_order:
    #             for order_line in po.order_line:
    #                 remaining_qty += order_line.remaining_quantity
    #         if remaining_qty > rec.request_id.line_ids.product_qty:
    #             raise UserError(
    #                 f"The requested quantity ({rec.request_id.line_ids.product_qty}) "
    #                 f"cannot be less than the remaining quantity ({remaining_qty})."
    #             )
    #     return super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
