# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MaintenanceTeam(models.Model):
    _inherit = 'maintenance.team'


    emp_ids = fields.Many2many(
        'hr.employee', string="Team Members",
       )
    #  domain="[('company_ids', 'in', company_id)]"