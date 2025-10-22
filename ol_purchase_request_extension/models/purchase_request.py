from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime
class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    quantity_track = fields.Integer("Quantity Track")

    
class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    readonly_check=fields.Boolean('Read Only Check',compute="_compute_readonly_check")

    def _compute_readonly_check(self):
        for rec in self:
            rec.readonly_check=True if rec.headoffice_state=='approve' else False


    @api.constrains('approval_state')
    def validation_check(self):
        for rec in self:
            if rec.approval_state=='store_supervisors':
                lines=rec.line_ids.filtered(lambda line : line.price_unit ==0)
                if lines:
                    raise UserError("Can't Proceed without Estimated Cost of lines")
            elif rec.approval_state=='approve':
                product_ids = []
                for line in rec.line_ids:
                    if line.product_id.id in product_ids:
                        raise UserError("No more than 1 line is allowed in Purchase Request")
        return True