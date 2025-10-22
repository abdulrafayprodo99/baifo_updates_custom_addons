from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    gate_in_id = fields.Many2many('gate.in', string="Gate In")
    gate_out_id = fields.Many2many('gate.out', string="Gate Out")

    picking_type_code = fields.Selection(
        selection=[
            ('incoming', 'Receipt'),
            ('outgoing', 'Delivery'),
            ('internal', 'Internal Transfer'),
            ('mrp_operation', 'Manufacturing')
        ],
        string="Operation Type Code",
        compute="_compute_picking_type_code",
        store=True
    )

    @api.depends('picking_type_id.code')
    def _compute_picking_type_code(self):
        for rec in self:
            rec.picking_type_code = rec.picking_type_id.code
