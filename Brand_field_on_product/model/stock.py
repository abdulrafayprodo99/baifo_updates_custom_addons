# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class stock_move(models.Model):
    _inherit = 'stock.move'

    # reference=fields.Char('Reference',compute='_compute_reference')

                
    # @api.depends('origin')
    # def _compute_reference(self):
    #     for rec in self:
    #         rec.reference=rec.origin            
    
    def action_show_details_modified(self):
        self.ensure_one()
        action = super().action_show_details()
        if self.raw_material_production_id:
            action['views'] = [(self.env.ref('mrp.view_stock_move_operations_raw').id, 'form')]
            action['context']['show_destination_location'] = False
            action['context']['force_manual_consumption'] = True
            action['context']['active_mo_id'] = self.raw_material_production_id.id
        elif self.production_id:
            action['views'] = [(self.env.ref('mrp.view_stock_move_operations_finished').id, 'form')]
            action['context']['show_source_location'] = False
            action['context']['show_reserved_quantity'] = False
            
        return action

    def write(self, vals):
        super(stock_move,self).write(vals)
        for rec in self:
            if not rec.origin and rec.group_id:
                rec.origin = rec.group_id.name

        return True