# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_prepared_sale(self):
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
        
        self['approval_state_sale']='prepared'
        self['prepare_sale'] = self.write_uid.id
        self['prepare_sale_timestamp'] = fields.Datetime.now()
        self['readonly_check'] = True