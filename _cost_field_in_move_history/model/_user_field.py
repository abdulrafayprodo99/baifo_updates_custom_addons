from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class purchase_class(models.Model):
    _inherit = "purchase.request"
    
    # cost_field = fields.Float(string="Cost", compute="_compute_cost_field", store=True)
    user_id=fields.Many2one("res.users",string="User")

    user_id_readonly =  fields.Boolean(string="User Readonly", compute="_compute_user_id_readonly", store=False)

    @api.depends("user_id")
    def _compute_user_id_readonly(self):
        for rec in self:
            rec.user_id_readonly = self.env.user.login == 'ghufran.ali@biafo.com'



class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit="purchase.request.line.make.purchase.order.item"

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self:
            if self.line_id.product_qty < self.product_qty:
                raise UserError(_("The product quantity cannot be greater than the requested quantity"))