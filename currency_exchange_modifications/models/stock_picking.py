from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    currency_rate =fields.Float(string="Currency Rate", store=True, compute="compute_currency_rate",readonly=False)
    currency_name = fields.Char(string="Currency Name", compute = "compute_currency_name")


    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for picking in self:
            for move in picking.move_ids:
                if round(move.quantity_done,2) > round(move.product_uom_qty,2):
                    raise ValidationError(_(
                        "In picking %s, the quantity done (%s) cannot be greater than the planned quantity (%s) for product %s."
                    ) % (
                        picking.name,
                        move.quantity_done,
                        move.product_uom_qty,
                        move.product_id.display_name
                    ))
        return res


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
            pass