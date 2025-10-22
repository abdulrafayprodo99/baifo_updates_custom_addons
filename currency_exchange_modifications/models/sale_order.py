from odoo import models, fields, api,_,Command
from odoo.exceptions import UserError

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from odoo.tools.sql import create_index

from odoo.addons.payment import utils as payment_utils
from itertools import groupby

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    currency_rate = fields.Float('Rate', compute='_compute_currency_rate', store=True)
    currency_name =  fields.Char(string="Currency Name", compute='_compute_currency_name', store=True)

    @api.depends('pricelist_id')
    def _compute_currency_rate(self):
        for record in self:
            rate = record.env['res.currency.rate'].search([
                            ('currency_id', '=', record.currency_id.id),
                            ('name', '=', record.date_order),
                        ])
            if rate:
                record.currency_rate =  rate.inverse_company_rate
            else:
                record.currency_rate = 0.0

    @api.depends('pricelist_id')
    def _compute_currency_name(self):
        for record in self:
            if record.pricelist_id:
                record.currency_name = record.pricelist_id.currency_id.name
            else:
                record.currency_name = ''

    
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        jounral_id = False  
        if self.sale_order_type == "local":            
            jounral_id = 1
        elif self.sale_order_type == "export":            
            jounral_id = 40
        else:
            jounral_id = 41
            
        res = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'currency_rate': self.currency_rate,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(self.partner_invoice_id)).id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_user_id': self.user_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [Command.set(self.transaction_ids.ids)],
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
            'journal_id':jounral_id
        }
        return res
    



    # def _create_invoices(self, grouped=False, final=False, date=None, **kwargs):
    #     """ Create invoice(s) for the given Sales Order(s).

    #     :param bool grouped: if True, invoices are grouped by SO id.
    #         If False, invoices are grouped by keys returned by :meth:`_get_invoice_grouping_keys`
    #     :param bool final: if True, refunds will be generated if necessary
    #     :param date: unused parameter
    #     :param kwargs: additional parameters, e.g., 'do_ref'
    #     :returns: created invoices
    #     :rtype: `account.move` recordset
    #     :raises: UserError if one of the orders has no invoiceable lines.
    #     """
    #     do_ref = kwargs.get('do_ref')
        
    #     if not do_ref:
    #         return super()._create_invoices(grouped=grouped, final=final, date=date, **kwargs)
        
    #     if not self.env['account.move'].check_access_rights('create', False):
    #         try:
    #             self.check_access_rights('write')
    #             self.check_access_rule('write')
    #         except AccessError:
    #             return self.env['account.move']
        
    #     # Check if an invoice with this do_ref already exists
    #     if self.env['account.move'].search([('do_ref', '=', do_ref)], limit=1):
    #         return self.env['account.move']

    #     # 1) Create invoices.
    #     invoice_vals_list = []
    #     invoice_item_sequence = 0
    #     for order in self:
    #         order = order.with_company(order.company_id).with_context(lang=order.partner_invoice_id.lang)

    #         invoice_vals = order._prepare_invoice()
    #         invoiceable_lines = order._get_invoiceable_lines(final)

    #         if not any(not line.display_type for line in invoiceable_lines):
    #             continue

    #         invoice_line_vals = []
    #         down_payment_section_added = False
    #         for line in invoiceable_lines:
    #             if not down_payment_section_added and line.is_downpayment:
    #                 invoice_line_vals.append(
    #                     Command.create(
    #                         order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
    #                     ),
    #                 )
    #                 down_payment_section_added = True
    #                 invoice_item_sequence += 1
    #             invoice_line_vals.append(
    #                 Command.create(
    #                     line._prepare_invoice_line(sequence=invoice_item_sequence)
    #                 ),
    #             )
    #             invoice_item_sequence += 1

    #         invoice_vals['invoice_line_ids'] += invoice_line_vals
            
    #         # Add do_ref to invoice values
    #         invoice_vals['do_ref'] = do_ref
            
    #         invoice_vals_list.append(invoice_vals)

    #     if not invoice_vals_list and self._context.get('raise_if_nothing_to_invoice', True):
    #         raise UserError(self._nothing_to_invoice_error_message())

    #     # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
    #     if not grouped:
    #         new_invoice_vals_list = []
    #         invoice_grouping_keys = self._get_invoice_grouping_keys()
    #         invoice_vals_list = sorted(
    #             invoice_vals_list,
    #             key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]
    #         )
    #         for _grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
    #             origins = set()
    #             payment_refs = set()
    #             refs = set()
    #             ref_invoice_vals = None
    #             for invoice_vals in invoices:
    #                 if not ref_invoice_vals:
    #                     ref_invoice_vals = invoice_vals
    #                 else:
    #                     ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
    #                 origins.add(invoice_vals['invoice_origin'])
    #                 payment_refs.add(invoice_vals['payment_reference'])
    #                 refs.add(invoice_vals['ref'])
    #             ref_invoice_vals.update({
    #                 'ref': ', '.join(refs)[:2000],
    #                 'invoice_origin': ', '.join(origins),
    #                 'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
    #             })
    #             new_invoice_vals_list.append(ref_invoice_vals)
    #         invoice_vals_list = new_invoice_vals_list

    #     # 3) Create invoices.
    #     if len(invoice_vals_list) < len(self):
    #         SaleOrderLine = self.env['sale.order.line']
    #         for invoice in invoice_vals_list:
    #             sequence = 1
    #             for line in invoice['invoice_line_ids']:
    #                 line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
    #                 sequence += 1

    #     moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

    #     # 4) Convert refunds if necessary
    #     if final:
    #         moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
    #     for move in moves:
    #         move.message_post_with_view(
    #             'mail.message_origin_link',
    #             values={'self': move, 'origin': move.line_ids.sale_line_ids.order_id},
    #             subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'))
    #     return moves




    def _create_invoices(self, grouped=False, final=False, date=None, **kwargs):
        """ Create invoice(s) for the given Sales Order(s). """
        do_ref = kwargs.get('do_ref')
        delivery_address = kwargs.get('delivery_address')

        if not do_ref:
            return super()._create_invoices(grouped=grouped, final=final, date=date, **kwargs)

        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        if self.env['account.move'].search([('do_ref', '=', do_ref)], limit=1):
            return self.env['account.move']

        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self:
            order = order.with_company(order.company_id).with_context(lang=order.partner_invoice_id.lang)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    invoice_line_vals.append(
                        Command.create(
                            order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
                        ),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    Command.create(
                        line._prepare_invoice_line(sequence=invoice_item_sequence)
                    ),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals['do_ref'] = do_ref

            # Update partner_shipping_id from kwargs if provided
            if delivery_address:
                invoice_vals.update({'partner_shipping_id': delivery_address})
            else:
                invoice_vals.update({'partner_shipping_id': order.partner_shipping_id.id})

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and self._context.get('raise_if_nothing_to_invoice', True):
            raise UserError(self._nothing_to_invoice_error_message())

        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]
            )
            for _grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view(
                'mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.sale_line_ids.order_id},
                subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'))
        return moves
