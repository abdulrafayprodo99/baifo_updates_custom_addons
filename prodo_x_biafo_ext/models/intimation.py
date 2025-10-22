# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Intimation(models.Model):
    _name = "intimation"
    _description = "Intimation"

    partner_id= fields.Many2one('res.partner',string="Customer",domain="[('type', '!=', 'private'),('customer_rank','!=',0)]",copy=False)
    delivery_address = fields.Many2one('res.partner',string="Delivery Address",domain="[('customer_rank','=',0)]",copy=False)
    customer_code = fields.Char(related="partner_id.x_studio_new_code", string="Code" ,copy=False)
    location= fields.Char(string="Location")
    cc = fields.Html('CC')
    name = fields.Char(string="Name",copy=False)
    
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s' % (rec.delivery_address.name,)))
        return result

    
    
    # @api.onchange('partner_id')
    # def Update_name(self):
    #     if self.partner_id:
    #         self['name'] = self.partner_id.name + ", " + self.location