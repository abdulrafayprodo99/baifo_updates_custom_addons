from odoo import models,fields,api,_,Command
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import datetime
class PurchaseOrderLine(models.Model):
    _inherit="purchase.order.line"

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        aml_currency = move and move.currency_id or self.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            'display_type': self.display_type or 'product',
            'name': '%s: %s' % (self.order_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'price_unit': self.currency_id._convert(self.price_unit, aml_currency, self.company_id, date, round=False),
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'purchase_line_id': self.id,
        }
        if self.analytic_distribution and not self.display_type:
            res['analytic_distribution'] = self.analytic_distribution

        if self.order_id and self.order_id.currency_id and self.order_id.currency_id.name != 'PKR':
            res['currency_rate'] = self.order_id.currency_rate
        return res


    
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res

        price_unit = self._get_stock_move_price_unit()
        qty = self._get_qty_procurement()

        move_dests = self.move_dest_ids
        if not move_dests:
            move_dests = self.move_ids.move_dest_ids.filtered(lambda m: m.state != 'cancel' and not m.location_dest_id.usage == 'supplier')

        if not move_dests:
            qty_to_attach = 0
            qty_to_push = self.product_qty - qty
        else:
            move_dests_initial_demand = self.product_id.uom_id._compute_quantity(
                sum(move_dests.filtered(lambda m: m.state != 'cancel' and not m.location_dest_id.usage == 'supplier').mapped('product_qty')),
                self.product_uom, rounding_method='HALF-UP')
            qty_to_attach = move_dests_initial_demand - qty
            qty_to_push = self.product_qty - move_dests_initial_demand

        if float_compare(qty_to_attach, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(qty_to_attach, self.product_id.uom_id)
            res.append(self._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom))
        if not float_is_zero(qty_to_push, precision_rounding=self.product_uom.rounding):
            product_uom_qty, product_uom = self.product_uom._adjust_uom_quantities(qty_to_push, self.product_id.uom_id)
            extra_move_vals = self._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
            extra_move_vals['move_dest_ids'] = False  # don't attach
            res.append(extra_move_vals)
        return res

    def _create_stock_moves(self, picking):
        values = []
        for line in self.filtered(lambda l: not l.display_type):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
            line.move_dest_ids.created_purchase_line_id = False
        return self.env['stock.move'].create(values)

    def _get_stock_move_price_unit(self):
        self.ensure_one()
        order = self.order_id
        price_unit = self.price_unit
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        if self.taxes_id:
            qty = self.product_qty or 1
            price_unit = self.taxes_id.with_context(round=False).compute_all(
                price_unit, currency=self.order_id.currency_id, quantity=qty, product=self.product_id, partner=self.order_id.partner_id
            )['total_void']
            price_unit = price_unit / qty
        if self.product_uom.id != self.product_id.uom_id.id:
            price_unit *= self.product_uom.factor / self.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            if order.currency_rate != 0.0:
                price_unit = price_unit * order.currency_rate
            else:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(), round=False)
            
        return float_round(price_unit, precision_digits=price_unit_prec)