# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import config, human_size, ImageProcess, str2bool, consteq
import base64



class ProductTemplate(models.Model):
    _inherit = 'res.partner'
    
    
    customer_license_id =fields.Many2many('customer.license',string='Customer License')


    # def _compute_customer_license(self):
    #     for record in self:
    #             customer_licenses = self.env['customer.license'].search([('customer_name', '=', record.name)])
    #             record['customer_license_id'] = customer_licenses.customer_name.name