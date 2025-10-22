from odoo import models, fields
from odoo.exceptions import UserError


# class MaintenanceEquipment(models.Model):
#     _inherit = 'maintenance.equipment'

#     def action_view_stock_pickings(self):
#         # Get all maintenance requests linked to this equipment
#         request_ids = self.env['maintenance.request'].search([('equipment_id', 'in', self.ids)]).ids

#         # Find all pickings with those requests in wr_no
#         pickings = self.env['stock.picking'].search([
#             ('wr_no', 'in', request_ids),
#             ('picking_type_id.name', '=', 'Material Consumption Note - Stores & Spares')  # Filter by OpType name
#         ])

#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Material Consumption Notes',
#             'res_model': 'stock.picking',
#             'view_mode': 'tree,form',
#             'domain': [('id', 'in', pickings.ids)],
#             'context': {'default_equipment_id': self.id},
#             'help': """
#                 <p class="o_view_nocontent_smiling_face">
#                     No pickings found for this equipment.
#                 </p>
#                 <p>
#                     Pickings will appear here once they are associated with maintenance requests linked to this equipment.
#                 </p>
#             """
#         }




class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    equipment_wr_nos_list = fields.Char(
        compute='_compute_equipment_wr_nos_list',
        store=False
    )

    stock_move_line_count = fields.Integer(
        string='Stock Move Line Count',
        compute='_compute_stock_move_line_count',
        store=False
    )

    def _compute_equipment_wr_nos_list(self):
        for rec in self:
            rec.equipment_wr_nos_list = ','.join(rec.maintenance_ids.mapped('wr_no'))

    def _compute_stock_move_line_count(self):
        for rec in self:
            wr_nos = rec.maintenance_ids.mapped('wr_no')
            rec.stock_move_line_count = self.env['stock.move.line'].search_count([
                ('move_id.picking_id.wr_no.wr_no', 'in', wr_nos)
            ])


    def action_view_stock_move_lines(self):

        self.ensure_one()

        wr_nos = self.maintenance_ids.mapped('wr_no')
        if not wr_nos:
            raise UserError("No related maintenance requests found for this equipment.")

        domain = [('move_id.picking_id.wr_no.wr_no', 'in', wr_nos)]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Move Lines',
            'res_model': 'stock.move.line',
            'view_mode': 'kanban,tree,form',
            'domain': domain,
            'context': {},
            'help': 'These are move lines where the picking\'s WR No matches a request WR No from this equipment.',
        }