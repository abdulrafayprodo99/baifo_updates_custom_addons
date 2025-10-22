from odoo import models, _

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns()
            new_picking = self.env['stock.picking'].browse(new_picking_id)

            # Set gate_in_id if return to vendor
            if wizard.picking_id.picking_type_id.code == 'incoming':
                new_picking.gate_in_id = wizard.picking_id.gate_in_id.id

            # Set gate_out_id if return to customer
            elif wizard.picking_id.picking_type_id.code == 'outgoing':
                new_picking.gate_out_id = wizard.picking_id.gate_out_id.id

        ctx = dict(self.env.context)
        ctx.update({
            'default_partner_id': self.picking_id.partner_id.id,
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_planning_issues': False,
            'search_default_available': False,
        })

        return {
            'name': _('Returned Picking'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
