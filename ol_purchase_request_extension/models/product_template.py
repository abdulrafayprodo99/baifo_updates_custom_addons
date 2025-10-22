from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    readonly_check=fields.Boolean('Read Only Check',compute="_compute_readonly_check")

    def _compute_readonly_check(self):
        for rec in self:
            rec.readonly_check=True if rec.approval_state=='approve' else False
    
