# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.onchange('partner_id')
    def update_attestation(self):
        for rec in self:
            rec.attestation=rec.partner_id.attestation_sq_id.id


    