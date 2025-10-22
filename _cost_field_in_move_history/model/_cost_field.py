from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WriteName(models.Model):
    _inherit = "stock.move.line"
    
    cost_field = fields.Float(string="Cost", compute="_compute_cost_field", store=True)

    @api.depends('product_id.standard_price', 'location_id.usage', 'location_dest_id.usage')
    def _compute_cost_field(self):
        for record in self:
            if record.location_id.usage == 'internal' and record.location_dest_id.usage == 'internal':
                record.cost_field = record.product_id.standard_price
            else:
                record.cost_field = 0.0  # or set to None if you prefer
