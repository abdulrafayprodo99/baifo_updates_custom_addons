# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import config, human_size, ImageProcess, str2bool, consteq
import base64


class Shipment(models.Model):
    _name = 'hs.code'
    _description = "Hs Code"

    name = fields.Char(string="name", store=True)
    total_per = fields.Float(string="Total Percentage" , compute="compute_total_")
    line_ids = fields.One2many("hs.code.line", "hs_code_id", string="Line Items", store=True)

    @api.depends('line_ids')
    def compute_total_(self):
        for rec in self:
            total = 0 
            for line in rec.line_ids:
                total += line.tax_per
            rec['total_per'] = total

class ShipmentLine(models.Model):
    _name = 'hs.code.line'
    _description = "HS Code"

    hs_code_id = fields.Many2one("hs.code",  string="HS Code", store=True)
    product_id = fields.Many2one('product.template', string="Product")
    tax_per = fields.Char(string="Tax Percentage" , store=True)

class ProductTemplate(models.Model):
    _inherit = "product.template"


    hs_code_id = fields.Many2one('hs.code', string="HS Code")
   
    
    
           
