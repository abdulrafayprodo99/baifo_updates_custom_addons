from odoo import models, fields, api,_,SUPERUSER_ID
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    currency_rate = fields.Float('Rate', compute='_compute_currency_rate', store=True)
    currency_name = fields.Char(string="Currency Name", related = "currency_id.name")

    @api.depends('currency_id')
    def _compute_currency_rate(self):
        for record in self:
            rate = record.env['res.currency.rate'].search([
                            ('currency_id', '=', record.currency_id.id),
                            ('name', '=', record.date_order),
                        ])
            if rate:
                record.currency_rate = rate.inverse_company_rate
            else:
                record.currency_rate = 0.0


    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        if self.currency_rate and self.currency_name != 'PKR':
            res.update({
                'currency_rate' : self.currency_rate,
            })
        return res

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.currency_rate and self.currency_name != 'PKR':
            res.update({
                'currency_rate' : self.currency_rate,
            })
        return res


    # def _create_picking(self):
    #     # raise UserError("Hamza Khattak")
    #     StockPicking = self.env['stock.picking']
    #     for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
    #         if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
    #             order = order.with_company(order.company_id)
    #             pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
    #             if not pickings:
    #                 res = order._prepare_picking()
    #                 picking = StockPicking.with_user(SUPERUSER_ID).create(res)
    #                 pickings = picking
    #             else:
    #                 picking = pickings[0]
    #             moves = order.order_line._create_stock_moves(picking)
    #             moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
    #             seq = 0
    #             for move in sorted(moves, key=lambda move: move.date):
    #                 seq += 5
    #                 move.sequence = seq
    #             # raise UserError(str(moves.name))
    #             moves._action_assign()
    #             # Get following pickings (created by push rules) to confirm them as well.
    #             forward_pickings = self.env['stock.picking']._get_impacted_pickings(moves)
    #             # raise UserError(str(forward_pickings.name))
    #             (pickings | forward_pickings).action_confirm()
    #             picking.message_post_with_view('mail.message_origin_link',
    #                 values={'self': picking, 'origin': order},
    #                 subtype_id=self.env.ref('mail.mt_note').id)
    #     return True