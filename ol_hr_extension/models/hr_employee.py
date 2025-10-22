# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    analytic_distribution = fields.Many2one(
        'account.analytic.account',"Analytic Account")
    

