# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import config, human_size, ImageProcess, str2bool, consteq
import base64
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    currency_rate =fields.Float(string="Currency Rate", store=True, compute="compute_currency_rate",readonly=False)
    currency_name = fields.Char(string="Currency Name", compute = "compute_currency_name")

    @api.depends("origin")
    def compute_currency_name(self):
        
        for rec in self:
            rec['currency_name'] = False
            purchase_order = self.env['purchase.order'].search([('name','=',rec.origin)])
            if purchase_order:
                for po in purchase_order:
                    rec['currency_name'] = po.currency_id.name

    @api.depends('origin')
    def compute_currency_rate(self):
        for rec in self:
            # raise UserError("working")
            purchase_order = self.env['purchase.order'].search([('name','=',rec.origin)])
            if purchase_order:
                for po in purchase_order:
                    if po.currency_id.id != 157:
                        rate = self.env['res.currency.rate'].search([('currency_id.id','=',po.currency_id.id),('name','=',datetime.now().date())])

                        if rate:
                            rec['currency_rate']  = rate.inverse_company_rate
                        else:
                            rec['currency_rate'] = 0
                

    def apply_currency_rate(self):
        for rec in self:
            if rec.currency_rate:
                purchase_order = self.env['purchase.order'].search([('name','=',rec.origin)])
                for po in purchase_order:
                    if po.currency_id.id != 157:
                        rate = self.env['res.currency.rate'].search([('currency_id.id','=',po.currency_id.id),('name','=',datetime.now().date())])
                        if rate:
                            a = rate.write({
                                'inverse_company_rate': rec.currency_rate,
                                'currency_id': po.currency_id.id,
                            })
                        else:
                            self.env['res.currency.rate'].create({
                                'currency_id': po.currency_id.id,
                                'name': datetime.now().date(),
                                'inverse_company_rate': rec.currency_rate,
                            })

   
class AccountMove(models.Model):
    _inherit = 'account.move'

    
    current_currency_rate =fields.Float(string="Current Currency Rate", store=True, compute="compute_currency_rate",readonly=False)
    currency_rate =fields.Float(string="Currency Rate", store=True,readonly=False)
    


    @api.depends('currency_id')
    def compute_currency_rate(self):
        for rec in self:
            # if rec.move_type == "out_invoice":
                rate = self.env['res.currency.rate'].search([('currency_id','=',rec.currency_id.id),('name','=',rec.invoice_date)])

                if rate:
                    rec['current_currency_rate']  = rate.inverse_company_rate
                else:
                    rec['current_currency_rate'] = 0

    

    def apply_currency_rate(self):
        for rec in self:
            if rec.currency_rate:
                if rec.move_type == "out_invoice" or rec.move_type == "in_invoice":
                    if rec.currency_id.id != 157:
                        rate = self.env['res.currency.rate'].search([('currency_id','=',rec.currency_id.id),('name','=',rec.invoice_date)])
                        # raise UserError(rate.inverse_company_rate) 
                        if rate:
                            a = rate.write({
                                'inverse_company_rate': rec.currency_rate,
                                'currency_id': rec.currency_id.id,
                            })
                            # raise UserError(a)
                        else:
                            self.env['res.currency.rate'].create({
                                'currency_id': rec.currency_id.id,
                                'name': rec.invoice_date,
                                'inverse_company_rate': rec.currency_rate,
                            })

   
class AccountPayment(models.Model):
    _inherit = 'account.payment'


    currency_rate =fields.Float(string="Currency Rate", store=True, compute="compute_currency_rate",readonly=False)
    
    @api.depends('currency_id')
    def compute_currency_rate(self):
        for rec in self:
            if rec.payment_type in ["outbound","inbound"]:
                rate = self.env['res.currency.rate'].search([('currency_id','=',rec.currency_id.id),('name','=',rec.date)])

                if rate:
                    rec['currency_rate']  = rate.inverse_company_rate
                else:
                    rec['currency_rate'] = 0
    

    def apply_currency_rate(self):
        for rec in self:
            if rec.currency_rate:
                if rec.payment_type in ["outbound","inbound"]:
                    if rec.currency_id.id != 157:
                        rate = self.env['res.currency.rate'].search([('currency_id','=',rec.currency_id.id),('name','=',rec.date)])
                        if rate:
                            a = rate.write({
                                'inverse_company_rate': rec.currency_rate,
                                'currency_id': rec.currency_id.id,
                            })
                        else:
                            self.env['res.currency.rate'].create({
                                'currency_id': rec.currency_id.id,
                                'name': rec.date,
                                'inverse_company_rate': rec.currency_rate,
                            })

