from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    name = fields.Char(string="Name")
    designation = fields.Char(string="Designation")
    cnic_no = fields.Char(string="CNIC No")
    date = fields.Date(string="Date")

    @api.onchange('picking_type_id')
    def _onchange_picking_type(self):
        if self.picking_type_id.code == 'outgoing':  # 'outgoing' is for delivery
            self.show_custom_fields = True
        else:
            self.show_custom_fields = False

    show_custom_fields = fields.Boolean(string="Show Custom Fields", compute="_compute_show_custom_fields", store=True)

    @api.depends('picking_type_id')
    def _compute_show_custom_fields(self):
        for picking in self:
            picking.show_custom_fields = picking.picking_type_id.code == 'outgoing'
