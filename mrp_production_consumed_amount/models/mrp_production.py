from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    total_quantity_done = fields.Float(
        string='Total Quantity Done',
        compute='_compute_total_quantity_done',
        # store=True
    )

    planned_date_start = fields.Datetime(
        string="Scheduled Start Date",
        related='date_planned_start',
        store=True
    )
    
    @api.depends('move_finished_ids.quantity_done', 'move_finished_ids.product_id.default_code')
    def _compute_total_quantity_done(self):
        lits = []
        for production in self:

            # raise UserError(str(production.move_raw_ids))
            
            # Filter out moves whose products have a default_code starting with '9'
            filtered_moves = production.move_raw_ids.filtered(
                lambda move: not move.product_id.default_code.startswith('9')
            )
            # raise UserError(str(filtered_moves.read()))
            # Calculate the sum of quantity_done
            production.total_quantity_done = sum(filtered_moves.mapped('quantity_done'))
            # raise UserError(production.total_quantity_done)
