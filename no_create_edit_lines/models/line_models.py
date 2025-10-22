from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    show_mark_as_todo = fields.Boolean(
        compute='_compute_show_mark_as_todo',
        help='Technical field used to compute whether the button "Mark as Todo" should be displayed.'
    )

    show_check_availability = fields.Boolean(
        compute='_compute_show_check_availability',
        help='Technical field used to compute whether the button "Check Availability" should be displayed.')

    @api.depends('state')
    def _compute_show_mark_as_todo(self):
        for move in self:
            # Add your logic here to determine when the button should be shown
            move.show_mark_as_todo = move.state == 'draft'

    @api.depends('state', 'product_id')
    def _compute_show_check_availability(self):
        for move in self:
            # Add your logic to determine if the "Check Availability" button should be shown
            move.show_check_availability = move.state == 'confirmed' and move.product_id.type == 'product'

