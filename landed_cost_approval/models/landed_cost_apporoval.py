from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_is_zero
from collections import defaultdict

class LandedCostApproval(models.Model):
    _name = 'landed.cost.apporoval'
    _description = 'Landed Cost Approval'

    name = fields.Char(string='Name')
    po_no = fields.Many2one('purchase.order', string='Purchase Order')
    # grn_no = fields.Many2one('stock.picking', string='GRN No#',domain="[('picking_type_id','=',10)]")
    # iqc_no = fields.Many2one('stock.picking', string='IQC No#',domain="[('picking_type_id','=',37)]")
    grn_no = fields.Many2one('stock.picking', string='GRN No#')
    iqc_no = fields.Many2one('stock.picking', string='IQC No#')
    landed_cost_attachd = fields.Many2many('account.move', string='Landed Cost Bills',domain="[('move_type','=','in_invoice')]")
    landed_cost_approval = fields.Boolean('Is Landed Cost Approved')

    # Noman
    landed_cost_expense = fields.Many2many('expense.module', string= 'Landed Cost Expense')

class stock_picking_type(models.Model):
    _inherit = 'stock.picking.type'
    is_landed_cost_type = fields.Boolean(string="Is Landed Cost Check Location")

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    create_landed_cost = fields.Boolean(string="Create Landed Cost")
    
    import_grn_ref = fields.Char('Import GRN Ref' , readonly=True)
    
    def button_validate(self):
        #Check if landed cost created and marked true for IQC operation type or landed cost operation marked true
        if self.picking_type_id.is_landed_cost_type == True:
            if not self.import_grn_ref:
                raise UserError('Please Fill Import GRN Refrence')
        if self.picking_type_id.is_landed_cost_type == True:
            grn = self.env['stock.picking'].search([('name','=',self.import_grn_ref)])
            landed_cost = self.env['landed.cost.apporoval'].search([('grn_no','=',grn.id)])
            
            if landed_cost or not landed_cost:

                # if landed_cost.approval_state != 'approve':
                #     raise UserError("a Can't validate this IQC, Landed Cost not updated yet")
                # else:
                    ctx = dict(self.env.context)
                    ctx.pop('default_immediate_transfer', None)
                    self = self.with_context(ctx)

                    # Sanity checks.
                    if not self.env.context.get('skip_sanity_check', False):
                        self._sanity_check()

                    self.message_subscribe([self.env.user.partner_id.id])

                    # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
                    # moves and/or the context and never call `_action_done`.
                    if not self.env.context.get('button_validate_picking_ids'):
                        self = self.with_context(button_validate_picking_ids=self.ids)
                    res = self._pre_action_done_hook()
                    if res is not True:
                        return res

                    # Call `_action_done`.
                    pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
                    if self.env.context.get('picking_ids_not_to_backorder'):
                        pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                            lambda p: p.picking_type_id.create_backorder != 'always'
                        )
                    pickings_to_backorder = self - pickings_not_to_backorder
                    pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
                    pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

                    if self.user_has_groups('stock.group_reception_report'):
                        pickings_show_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
                        lines = pickings_show_report.move_ids.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
                        if lines:
                            # don't show reception report if all already assigned/nothing to assign
                            wh_location_ids = self.env['stock.location']._search([('id', 'child_of', pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids), ('usage', '!=', 'supplier')])
                            if self.env['stock.move'].search([
                                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                                    ('product_qty', '>', 0),
                                    ('location_id', 'in', wh_location_ids),
                                    ('move_orig_ids', '=', False),
                                    ('picking_id', 'not in', pickings_show_report.ids),
                                    ('product_id', 'in', lines.product_id.ids)], limit=1):
                                action = pickings_show_report.action_view_reception_report()
                                action['context'] = {'default_picking_ids': pickings_show_report.ids}
                                return action
                    return True

                        
            # raise UserError("Hamza")
        # crate landed cost from GRN import operation type
        elif self.picking_type_id.id == 10 and self.currency_rate:
            # landed_cost = self.env['landed.cost.apporoval'].search([('po_no','=',self.origin)])
            # if landed_cost:
            #     if not landed_cost.landed_cost_attachd or not landed_cost.landed_cost_expense == []:
            #     # if landed_cost.landed_cost_approval != True:
            #         raise UserError("aaa Can't validate this IQC, Landed Cost not updated yet")
            # raise UserError("hghghg")
            # self.create_landed_cost_entry()
            ctx = dict(self.env.context)
            ctx.pop('default_immediate_transfer', None)
            self = self.with_context(ctx)

            # Sanity checks.
            if not self.env.context.get('skip_sanity_check', False):
                self._sanity_check()

            self.message_subscribe([self.env.user.partner_id.id])

            # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
            # moves and/or the context and never call `_action_done`.
            if not self.env.context.get('button_validate_picking_ids'):
                self = self.with_context(button_validate_picking_ids=self.ids)
            res = self._pre_action_done_hook()
            if res is not True:
                return res

            # Call `_action_done`.
            pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
            if self.env.context.get('picking_ids_not_to_backorder'):
                pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                    lambda p: p.picking_type_id.create_backorder != 'always'
                )
            pickings_to_backorder = self - pickings_not_to_backorder
            pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
            pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

            if self.user_has_groups('stock.group_reception_report'):
                pickings_show_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
                lines = pickings_show_report.move_ids.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
                if lines:
                    # don't show reception report if all already assigned/nothing to assign
                    wh_location_ids = self.env['stock.location']._search([('id', 'child_of', pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids), ('usage', '!=', 'supplier')])
                    if self.env['stock.move'].search([
                            ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                            ('product_qty', '>', 0),
                            ('location_id', 'in', wh_location_ids),
                            ('move_orig_ids', '=', False),
                            ('picking_id', 'not in', pickings_show_report.ids),
                            ('product_id', 'in', lines.product_id.ids)], limit=1):
                        action = pickings_show_report.action_view_reception_report()
                        action['context'] = {'default_picking_ids': pickings_show_report.ids}
                        return action
            return True
        # validation for currecny rate for GRN import operation type 
        elif self.picking_type_id.id == 10 and self.currency_rate == 0.00:
            raise UserError("GRN with Currency Rate Value 0.0!!! Unable to validate")
        # without landed cost aproval operation types
        else:
            ctx = dict(self.env.context)
            ctx.pop('default_immediate_transfer', None)
            self = self.with_context(ctx)

            # Sanity checks.
            if not self.env.context.get('skip_sanity_check', False):
                self._sanity_check()

            self.message_subscribe([self.env.user.partner_id.id])

            # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
            # moves and/or the context and never call `_action_done`.
            if not self.env.context.get('button_validate_picking_ids'):
                self = self.with_context(button_validate_picking_ids=self.ids)
            res = self._pre_action_done_hook()
            if res is not True:
                return res

            # Call `_action_done`.
            pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
            if self.env.context.get('picking_ids_not_to_backorder'):
                pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                    lambda p: p.picking_type_id.create_backorder != 'always'
                )
            pickings_to_backorder = self - pickings_not_to_backorder
            pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
            pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

            if self.user_has_groups('stock.group_reception_report'):
                pickings_show_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
                lines = pickings_show_report.move_ids.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
                if lines:
                    # don't show reception report if all already assigned/nothing to assign
                    wh_location_ids = self.env['stock.location']._search([('id', 'child_of', pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids), ('usage', '!=', 'supplier')])
                    if self.env['stock.move'].search([
                            ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                            ('product_qty', '>', 0),
                            ('location_id', 'in', wh_location_ids),
                            ('move_orig_ids', '=', False),
                            ('picking_id', 'not in', pickings_show_report.ids),
                            ('product_id', 'in', lines.product_id.ids)], limit=1):
                        action = pickings_show_report.action_view_reception_report()
                        action['context'] = {'default_picking_ids': pickings_show_report.ids}
                        return action
            return True


        
class stock_landed_cost(models.Model):
    _inherit = 'stock.landed.cost'

    def button_validate(self):
        
        # for rec in self.picking_ids:
        #     landed_cost_approval_search = self.env['landed.cost.apporoval'].search([('grn_no','=',rec.id)])
        #     if landed_cost_approval_search:
        #         if self.vendor_bill_id:
        #             landed_cost_approval_search['landed_cost_attachd'] = [(4, self.vendor_bill_id.id)]
        #         if self.expense_bill_id: 
        #             # Noman
        #             landed_cost_approval_search['landed_cost_expense'] = [(4, self.expense_bill_id.id)]
        #     else:
        #         raise UserError("Landed Cost Not Found, Please check slected GRN in Landed Cost Module")
        
        self._check_can_validate()
        cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
        if cost_without_adjusment_lines:
            cost_without_adjusment_lines.compute_landed_cost()
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            cost = cost.with_company(cost.company_id)
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
                'move_type': 'entry',
            }
            valuation_layer_ids = []
            cost_to_add_byproduct = defaultdict(lambda: 0.0)
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                linked_layer = line.move_id.stock_valuation_layer_ids[:1]

                # Prorate the value at what's still in stock
                cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                if not cost.company_id.currency_id.is_zero(cost_to_add):
                    valuation_layer = self.env['stock.valuation.layer'].create({
                        'value': cost_to_add,
                        'unit_cost': 0,
                        'quantity': 0,
                        'remaining_qty': 0,
                        'stock_valuation_layer_id': linked_layer.id,
                        'description': cost.name,
                        'stock_move_id': line.move_id.id,
                        'product_id': line.move_id.product_id.id,
                        'stock_landed_cost_id': cost.id,
                        'company_id': cost.company_id.id,
                    })
                    linked_layer.remaining_value += cost_to_add
                    valuation_layer_ids.append(valuation_layer.id)
                # Update the AVCO
                product = line.move_id.product_id
                if product.cost_method == 'average':
                    cost_to_add_byproduct[product] += cost_to_add
                # Products with manual inventory valuation are ignored because they do not need to create journal entries.
                if product.valuation != "real_time":
                    continue
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

            # batch standard price computation avoid recompute quantity_svl at each iteration
            products = self.env['product.product'].browse(p.id for p in cost_to_add_byproduct.keys())
            for product in products:  # iterate on recordset to prefetch efficiently quantity_svl
                if not float_is_zero(product.quantity_svl, precision_rounding=product.uom_id.rounding):
                    product.with_company(cost.company_id).sudo().with_context(disable_auto_svl=True).standard_price += cost_to_add_byproduct[product] / product.quantity_svl

            move_vals['stock_valuation_layer_ids'] = [(6, None, valuation_layer_ids)]
            # We will only create the accounting entry when there are defined lines (the lines will be those linked to products of real_time valuation category).
            cost_vals = {'state': 'done'}
            if move_vals.get("line_ids"):
                move = move.create(move_vals)
                cost_vals.update({'account_move_id': move.id})
            cost.write(cost_vals)
            if cost.account_move_id:
                move._post()

            if cost.vendor_bill_id and cost.vendor_bill_id.state == 'posted' and cost.company_id.anglo_saxon_accounting:
                all_amls = cost.vendor_bill_id.line_ids | cost.account_move_id.line_ids
                for product in cost.cost_lines.product_id:
                    accounts = product.product_tmpl_id.get_product_accounts()
                    input_account = accounts['stock_input']
                    all_amls.filtered(lambda aml: aml.account_id == input_account and not aml.reconciled).reconcile()

        return True
            
                        # raise UserError(landed_cost_approval_search.name)            
    

class Product(models.Model):
     
    _inherit = 'product.product'
    landed_cost_product = fields.Boolean(string="Landed Cost Product")
