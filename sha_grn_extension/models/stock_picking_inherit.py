# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    bill_create = fields.Boolean(string="Bill Created")