# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_prepare(self):
        
        if self.move_type == "out_invoice":
            # if self.invoice_date != self.date:               
            #     raise UserError("Invoice Date Should be Equal to Document date")
            # else:
            self['approval_state']='prepared'
            self['prepared_by'] = self.write_uid.id
            self['prepared_timestamp'] = fields.Datetime.now()
        else:
            self['approval_state']='prepared'
            self['prepared_by'] = self.write_uid.id
            self['prepared_timestamp'] = fields.Datetime.now()
            for pick in self.x_studio_grn_no_1:
                pick.bill_create = True
                # raise UserError(str(self.x_studio_grn_no_1[0].bill_create))
        
        # For Readonly
        self['readonly_check'] = True
        # self.generate_seq()

