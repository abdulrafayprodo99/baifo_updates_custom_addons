from odoo import models,fields,api,SUPERUSER_ID,_
from odoo.exceptions import UserError,ValidationError


# class StockMove(models.Model):
#     _inherit = "stock.move"

#     specification =  fields.Text(string="Specification")


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_id = fields.Many2one(
        'stock.lot', 'Lot/Serial Number',
        check_company=True
    )
    # @api.constrains('qty_done')
    # def _check_done_quantity(self):
    #     for record in self:
    #         if record.move_id.product_uom_qty > 0 and record.qty_done > record.move_id.product_uom_qty and (record.picking_id.picking_type_code in ['incoming', 'outgoing']):
    #             raise ValidationError(
    #                 _("The done quantity cannot be greater than the demand quantity. Demand: %s, Done: %s") % (record.move_id.product_uom_qty, record.qty_done)
    #             )

    @api.onchange('product_id', 'location_id', 'company_id')
    def _onchange_lot_domain(self):
        if self.product_id and self.location_id and self.company_id:
            quants = self.env['stock.quant'].search([
                ('location_id', '=', self.location_id.id),
                ('quantity', '>', 0),  # Ensure available quantity
                ('on_hand', '=', True)
            ])
            lot_ids = quants.mapped('lot_id').ids
        else:
            lot_ids = []

        return {
            'domain': {
                'lot_id': [
                    ('id', 'in', lot_ids),
                    ('product_id', '=', self.product_id.id if self.product_id else False),
                    ('company_id', '=', self.company_id.id if self.company_id else False),
                    # ('product_qty','>',0)
                ]
            }
        }




class MrpProduction(models.Model):
    _inherit = "mrp.production"

    lot_producing_id = fields.Many2one(
        'stock.lot', 'Lot/Serial Number', check_company=True)

    @api.onchange('product_id', 'company_id')
    def _onchange_lot_domain(self):
        lot_ids = []
        if self.product_id and self.company_id:
            quants = self.env['stock.quant'].search([
                ('quantity', '>', 0),  # Ensure available quantity
                ('lot_id', '!=', False)  # Ensure it has a lot assigned
            ])
            lot_ids = quants.mapped('lot_id').ids  # Extract lot IDs

        return {
            'domain': {
                'lot_producing_id': [  # Corrected field name
                    ('id', 'in', lot_ids),
                    ('product_id', '=', self.product_id.id) if self.product_id else (),
                    ('company_id', '=', self.company_id.id) if self.company_id else (),
                ]
            }
        }

    

    # specification =  fields.Text(string="Specification",related="move_id.specification")    



    