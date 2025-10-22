from odoo import models,fields,api,SUPERUSER_ID,_
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'



    qty_balance = fields.Float(string="Balance", compute="_compute_balance")

    remaining_quantity = fields.Float(string="remaining Quantity",compute="remaining_qty")
    
    @api.depends('product_qty','qty_received')
    def remaining_qty(self):
        for i in self:
            i['remaining_quantity'] = i.product_qty - i.qty_received

    def _compute_balance(self):
        for rec in self:
            rec.qty_balance = (rec.qty_received - rec.qty_invoiced) * rec.price_unit
            


#     def _create_stock_moves(self, picking):
#         values = []
#         for line in self.filtered(lambda l: not l.display_type):
#             for val in line._prepare_stock_moves(picking):
#                 values.append(val)
#             line.move_dest_ids.created_purchase_line_id = False
#         moves = self.env['stock.move'].create(values)
#         # counter = 0
#         # for move in moves:
#         #     move.write({
#         #         'x_studio_specification':values[counter]['x_studio_specification'] if len(values) > counter else False,
#         #     })
#         #     counter += 1
#         return moves
#     def _prepare_stock_moves(self, picking):
#         """ Prepare the stock moves data for one order line. This function returns a list of
#         dictionary ready to be used in stock.move's create()
#         """
#         self.ensure_one()
#         res = []
#         if self.product_id.type not in ['product', 'consu']:
#             return res

#         price_unit = self._get_stock_move_price_unit()
#         qty = self._get_qty_procurement()

#         move_dests = self.move_dest_ids
#         if not move_dests:
#             move_dests = self.move_ids.move_dest_ids.filtered(lambda m: m.state != 'cancel' and not m.location_dest_id.usage == 'supplier')

#         if not move_dests:
#             qty_to_attach = 0
#             qty_to_push = self.product_qty - qty
#         else:
#             move_dests_initial_demand = self.product_id.uom_id._compute_quantity(
#                 sum(move_dests.filtered(lambda m: m.state != 'cancel' and not m.location_dest_id.usage == 'supplier').mapped('product_qty')),
#                 self.product_uom, rounding_method='HALF-UP')
#             qty_to_attach = move_dests_initial_demand - qty
#             qty_to_push = self.product_qty - move_dests_initial_demand

#         if float_compare(qty_to_attach, 0.0, precision_rounding=self.product_uom.rounding) > 0:
#             product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(qty_to_attach, self.product_id.uom_id)
#             res.append(self._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom))
        
#         if not float_is_zero(qty_to_push, precision_rounding=self.product_uom.rounding):
#             product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(qty_to_push, self.product_id.uom_id)
#             extra_move_vals = self._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
#             extra_move_vals['move_dest_ids'] = False  # don't attach
#             res.append(extra_move_vals)

#         return res

#     def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
#         self.ensure_one()
#         self._check_orderpoint_picking_type()
#         product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
#         date_planned = self.date_planned or self.order_id.date_planned
#         return {
#             # truncate to 2000 to avoid triggering index limit error
#             # TODO: remove index in master?
            
#             'name': (self.product_id.display_name or '')[:2000],
#             'product_id': self.product_id.id,
#             'date': date_planned,
#             'date_deadline': date_planned,
#             'location_id': self.order_id.partner_id.property_stock_supplier.id,
#             'location_dest_id': (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
#             'picking_id': picking.id,
#             'partner_id': self.order_id.dest_address_id.id,
#             'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
#             'state': 'draft',
#             'purchase_line_id': self.id,
#             'company_id': self.order_id.company_id.id,
#             'price_unit': price_unit,
#             'picking_type_id': self.order_id.picking_type_id.id,
#             'group_id': self.order_id.group_id.id,
#             'origin': self.order_id.name,
#             'description_picking': product.description_pickingin or self.name,
#             'propagate_cancel': self.propagate_cancel,
#             'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
#             'product_uom_qty': product_uom_qty,
#             'product_uom': product_uom.id,
#             'product_packaging_id': self.product_packaging_id.id,
#             'sequence': self.sequence,
#             'specification':self.specification
#         }


# class PurchaseOrder(models.Model):
#     _inherit="purchase.order"

#     def _create_picking(self):
#         # raise UserError("Hamza Khattak")
#         StockPicking = self.env['stock.picking']
#         for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
#             if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
#                 order = order.with_company(order.company_id)
#                 pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
#                 if not pickings:
#                     res = order._prepare_picking()
#                     picking = StockPicking.with_user(SUPERUSER_ID).create(res)
#                     pickings = picking
#                 else:
#                     picking = pickings[0]
#                 moves = order.order_line._create_stock_moves(picking)
#                 moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
#                 seq = 0
#                 for move in sorted(moves, key=lambda move: move.date):
#                     seq += 5
#                     move.sequence = seq
#                 # raise UserError(str(moves.name))
#                 moves._action_assign()
#                 # Get following pickings (created by push rules) to confirm them as well.
#                 forward_pickings = self.env['stock.picking']._get_impacted_pickings(moves)
#                 # raise UserError(str(forward_pickings.name))
#                 (pickings | forward_pickings).action_confirm()
#                 picking.message_post_with_view('mail.message_origin_link',
#                     values={'self': picking, 'origin': order},
#                     subtype_id=self.env.ref('mail.mt_note').id)
#         return True