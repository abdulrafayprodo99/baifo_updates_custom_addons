from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    picking_code = fields.Boolean(
        string="Picking Type Code",
        compute='_compute_picking_type_code',
    )
    @api.depends('picking_type_id')
    def _compute_picking_type_code(self):
        for rec in self:
            if rec.picking_type_id.code == 'incoming':
                rec.picking_code = True
            else :
                rec.picking_code = False




