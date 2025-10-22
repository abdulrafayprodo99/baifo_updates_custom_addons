# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from num2words import num2words

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def amount_to_words(self, amount):
        # Converts amount to words
        return num2words(amount, lang='en').capitalize() + " only."
