from odoo import api, fields, models,SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero, html_escape
from odoo.tools.misc import split_every
from collections import defaultdict, namedtuple

from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_type = fields.Selection([('local', 'Sale Order Local'),('export', 'Sale Order Export'),('service', 'Sale Order Service')], required=True ,string='Sale Order Type')
    rfq_sale_seq = fields.Char(string='Sale Quotation/ Order Sequence' , readonly=True)
    delivery_schedule = fields.One2many('delivery.schedule','header_id',string="Delivery Schedule")
    customer_po_no = fields.Char(string='Customer PO No')
    customer_po_date = fields.Date(string='Customer PO Date')
    delivery_address = fields.Many2one('res.partner', string='Delivery Address' , domain="['&',('parent_name', '=', 'partner_id.name'),('type','=','delivery')]")
    transportation = fields.Selection([('incl', 'Inclusive'),('excl', 'Exclusive')] ,string='Transportation And Escort')
# , required=True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', 'New') == 'New':
            	# raise UserError(str(vals))
                seq_date = None
                if 'date_order' in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                if self.state == 'draft':
                    if vals.get('state', '') == '' or vals.get('state') == 'to approve':
                        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
                    # if self.sale_order_type == 'local':
                if vals['sale_order_type'] == 'local':
                    vals['name'] = self.env['ir.sequence'].next_by_code('rfq.so.state.L', sequence_date=seq_date) or '/'
                    
                if vals['sale_order_type'] == 'export':    
                    vals['name'] = self.env['ir.sequence'].next_by_code('rfq.so.state.E', sequence_date=seq_date) or '/'

                if vals['sale_order_type'] == 'service':    
                    vals['name'] = self.env['ir.sequence'].next_by_code('rfq.so.state.S', sequence_date=seq_date) or '/'
                        # raise UserError(vals['name'])
                # else:
                #     vals['name'] = self.env['ir.sequence'].next_by_code('rfq.so.state.E', sequence_date=seq_date)
                #     raise UserError(vals['state'])
        # raise UserError(str(vals_list))
        return super().create(vals_list)

    def action_confirm(self):
        if self.approval_state_sale == "approve" and self.approval_state in ["approve_ceo","approve_coo"]:
            
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(self.date_order))
            if self.sale_order_type == 'local':
                self['rfq_sale_seq'] = self.name
                self['name'] = (self.env['ir.sequence'].next_by_code('so.state.L' , sequence_date=seq_date) or '/')

            if self.sale_order_type == 'export':
                self['rfq_sale_seq'] = self.name
                self['name'] = self['name'] = self.env['ir.sequence'].next_by_code('so.state.E' , sequence_date=seq_date) or '/'
            
            if self.sale_order_type == 'service':
                self['rfq_sale_seq'] = self.name
                self['name'] = self['name'] = self.env['ir.sequence'].next_by_code('so.state.S' , sequence_date=seq_date) or '/'
            
                    



            if self._get_forbidden_state_confirm() & set(self.mapped('state')):
                raise UserError(_(
                    "It is not allowed to confirm an order in the following states: %s",
                    ", ".join(self._get_forbidden_state_confirm()),
                ))

            self.order_line._validate_analytic_distribution()

            for order in self:
                order.validate_taxes_on_sales_order()
                if order.partner_id in order.message_partner_ids:
                    continue
                order.message_subscribe([order.partner_id.id])
            self.write(self._prepare_confirmation_values())

            # Context key 'default_name' is sometimes propagated up to here.
            # We don't need it and it creates issues in the creation of linked records.
            context = self._context.copy()
            context.pop('default_name', None)
            self.with_context(context)._action_confirm()
            if self.env.user.has_group('sale.group_auto_done_setting'):
                self.action_done()

            return True
        else:
            raise UserError('Approval Required')



class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    list_price = fields.Float(string='List price')
    other_cost = fields.Float(string='Other Cost')
# ,'price_unit'
    @api.onchange('product_id')
    def duplicate_unit_price(self):
        for rec in self:
                rec['list_price'] = rec.price_unit

class DeliverySchedule(models.Model):
    _name = 'delivery.schedule'
    header_id = fields.Many2one('sale.order',string="header id")
    product_id = fields.Many2one('product.product',string="Product")
    consignee_location = fields.Char(string="Consignee Location")
    qty = fields.Char(string="Quantity")
    schedule_date = fields.Date(string="Schedule Date")
    
    
    
    @api.onchange('product_id','qty','consignee_location')
    def returnDomain(self):
        ids = []
        for ol in self.header_id.order_line:
            ids.append(ol.product_id.id)
        
        action = {
            'domain': {
            'product_id': [('id', 'in',ids )]
            }
            }
        # self.returnAction(action)
        return action


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_pull(self, procurements):
        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name, )
                raise ProcurementException([(procurement, msg)])

            if rule.procure_method == 'mts_else_mto':
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}

        # Prepare the move values, adapt the `procure_method` if needed.
        procurements = sorted(procurements, key=lambda proc: float_compare(proc[0].product_qty, 0.0, precision_rounding=proc[0].product_uom.rounding) > 0)
        for procurement, rule in procurements:
            procure_method = rule.procure_method
            if rule.procure_method == 'mts_else_mto':
                qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                if float_compare(qty_needed, 0, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                    procure_method = 'make_to_order'
                    for move in procurement.values.get('group_id', self.env['procurement.group']).stock_move_ids:
                        if move.rule_id == rule and float_compare(move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding) > 0:
                            procure_method = move.procure_method
                            break
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                elif float_compare(qty_needed, forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id],
                                   precision_rounding=procurement.product_id.uom_id.rounding) > 0:
                    procure_method = 'make_to_order'
                else:
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                    procure_method = 'make_to_stock'
            move_values = rule._get_stock_move_values(*procurement)
            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)
        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
            origin = ""
            for i in moves_values:
                if isinstance(i, dict) and i.get('origin'):
                    origin = i['origin']
            if origin:
                moves.with_user(SUPERUSER_ID).sudo().write({'origin': origin})
            # Since action_confirm launch following procurement_group we should activate it.
            moves._action_confirm()
        return True