from odoo import models, fields, api, _,Command
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import float_is_zero, float_repr, float_round, float_compare
from odoo.exceptions import ValidationError
from collections import defaultdict

class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_in_svl_custom(self, forced_quantity=None,**kwargs):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """

        svl_vals_list = self._get_in_svl_vals_custom(forced_quantity,out_valuations=kwargs.get('out_valuations',None))
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
    def get_price_unit_acc_date(self):
        # raise UserError(str(self.read()))
        if self.raw_material_production_id:
            return  self.env['stock.valuation.layer'].search([('product_id','=',self.product_id.id),('create_date','<=',self.raw_material_production_id.date_planned_start),('unit_cost','!=',0)],order="create_date desc",limit=1).unit_cost
        elif self.picking_id:
            return  self.env['stock.valuation.layer'].search([('product_id','=',self.product_id.id),('create_date','<=',self.picking_id.date_done),('unit_cost','!=',0)],order="create_date desc",limit=1).unit_cost

    def _create_out_svl_custom(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        # raise UserError(str(self.env.context))
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_out_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                continue
            svl_vals = move.product_id._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)

            company_id = self.env.context.get('force_company', self.env.company.id)
            company = self.env['res.company'].browse(company_id)
            currency = company.currency_id
            cost = abs(move.get_price_unit_acc_date())
            svl_vals.update({
                'unit_cost':cost,
                'value':currency.round(svl_vals.get('quantity',0) * cost) 
            })
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % (move.picking_id.name or move.name)
            svl_vals['description'] += svl_vals.pop('rounding_adjustment', '')
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
    
    def _get_in_svl_vals_custom(self, forced_quantity,**kwargs):
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_in_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            unit_cost = move.product_id.standard_price
            if move.product_id.cost_method != 'standard':
                unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
            if move.picking_id:
                price_unit  =  move.env['purchase.order'].search([('name','=',move.picking_id.origin)]).mapped('order_line').filtered(lambda x:x.product_id.id == move.product_id.id ).price_unit
            elif move.production_id:
                # total_value = sum(m.get_price_unit_acc_date() * m.product_uom_qty for m in move.production_id.move_raw_ids)
                total_value = abs(sum(map(lambda x:x.value , kwargs.get('out_valuations',[]))))
                price_unit = abs(total_value / move.production_id.product_qty) if move.production_id.product_qty else 0
            else:
                price_unit = unit_cost
            if price_unit == 0:
                price_unit = move.product_id.standard_price
            svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity,abs(price_unit))
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % (move.picking_id.name or move.name)
            svl_vals_list.append(svl_vals)
        return svl_vals_list
    
    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self._should_ignore_pol_price():
            return super(StockMove, self)._get_price_unit()
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        line = self.purchase_line_id
        order = line.order_id
        received_qty = line.qty_received
        if self.state == 'done':
            received_qty -= self.product_uom._compute_quantity(self.quantity_done, line.product_uom, rounding_method='HALF-UP')
        if float_compare(line.qty_invoiced, received_qty, precision_rounding=line.product_uom.rounding) > 0:
            move_layer = line.move_ids.sudo().stock_valuation_layer_ids
            invoiced_layer = line.sudo().invoice_lines.stock_valuation_layer_ids
            # value on valuation layer is in company's currency, while value on invoice line is in order's currency
            receipt_value = 0
            if move_layer:
                receipt_value += sum(move_layer.mapped(lambda l: l.currency_id._convert(
                    l.value, order.currency_id, order.company_id, l.create_date, round=False)))
            if invoiced_layer:
                receipt_value += sum(invoiced_layer.mapped(lambda l: l.currency_id._convert(
                    l.value, order.currency_id, order.company_id, l.create_date, round=False)))
            invoiced_value = 0
            invoiced_qty = 0
            for invoice_line in line.sudo().invoice_lines:
                if invoice_line.tax_ids:
                    invoiced_value += invoice_line.tax_ids.with_context(round=False).compute_all(
                        invoice_line.price_unit, currency=invoice_line.currency_id, quantity=invoice_line.quantity)['total_void']
                else:
                    invoiced_value += invoice_line.price_unit * invoice_line.quantity
                invoiced_qty += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity, line.product_id.uom_id)
            # TODO currency check
            remaining_value = invoiced_value - receipt_value
            # TODO qty_received in product uom
            remaining_qty = invoiced_qty - line.product_uom._compute_quantity(received_qty, line.product_id.uom_id)
            price_unit = float_round(remaining_value / remaining_qty, precision_digits=price_unit_prec)
            # raise UserError(f"123 {price_unit}")
        else:
            price_unit = line._get_gross_price_unit()
        if self.picking_id and self.picking_id.currency_name and self.picking_id.currency_name  != 'PKR':
                price_unit =   price_unit * self.picking_id.currency_rate

        elif order.currency_id != order.company_id.currency_id:

            # The date must be today, and not the date of the move since the move move is still
            # in assigned state. However, the move date is the scheduled date until move is
            # done, then date of actual move processing. See:
            # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
            price_unit = order.currency_id._convert(
                price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
        
        
        return price_unit

class ProductProduct(models.Model):
    _inherit="product.product"


    def _prepare_out_svl_vals_custom(self, quantity, company):
        """Prepare the values for a stock valuation layer created by a delivery.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        self.ensure_one()
        company_id = self.env.context.get('force_company', self.env.company.id)
        company = self.env['res.company'].browse(company_id)
        currency = company.currency_id
        # Quantity is negative for out valuation layers.
        quantity = -1 * quantity
        vals = {
            'product_id': self.id,
            'value': currency.round(quantity * self.standard_price),
            'unit_cost': self.standard_price,
            'quantity': quantity,
        }
        fifo_vals = self._run_fifo(abs(quantity), company)
        vals['remaining_qty'] = fifo_vals.get('remaining_qty')
        # In case of AVCO, fix rounding issue of standard price when needed.
        if self.product_tmpl_id.cost_method == 'average' and not float_is_zero(self.quantity_svl, precision_rounding=self.uom_id.rounding):
            rounding_error = currency.round(
                (self.standard_price * self.quantity_svl - self.value_svl) * abs(quantity / self.quantity_svl)
            )
            if rounding_error:
                # If it is bigger than the (smallest number of the currency * quantity) / 2,
                # then it isn't a rounding error but a stock valuation error, we shouldn't fix it under the hood ...
                if abs(rounding_error) <= max((abs(quantity) * currency.rounding) / 2, currency.rounding):
                    vals['value'] += rounding_error
                    vals['rounding_adjustment'] = '\nRounding Adjustment: %s%s %s' % (
                        '+' if rounding_error > 0 else '',
                        float_repr(rounding_error, precision_digits=currency.decimal_places),
                        currency.symbol
                    )
        if self.product_tmpl_id.cost_method == 'fifo':
            vals.update(fifo_vals)
        return vals


    # def _change_standard_price(self, new_price):
    #     return