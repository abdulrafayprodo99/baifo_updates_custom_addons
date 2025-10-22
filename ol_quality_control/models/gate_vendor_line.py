# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class GateInLine(models.Model):
    _inherit = 'gate.vendor.line'
    _description = "Gate Line"


    specs=fields.Text("Specification")

    @api.constrains('total_qty')
    def validate_total_qty(self):
        for rec in self:
            po_line = rec.gate_module_id.purchase_id.order_line.filtered(lambda x:x.product_id.id == rec.product_id.id and  x.specification == rec.specs )
            po_qty = po_line.product_qty
            if rec.total_qty > po_qty:
                raise UserError("Total quantity cannot be greater than purchase order quantity.") 
            if rec.qty > po_qty:
                raise UserError("Received quantity cannot be greater than total quantity.")


class GateINModule(models.Model):
    _inherit = "gate.in"
    _description = "Gate Module"

    @api.onchange("purchase_id")
    def _onchange_all_po_line(self):

        order_line=[]
        self['line_id'] = False
        for record in self:
            if record.purchase_id:
                other_model_record = self.env['purchase.order'].search([('id','=', record.purchase_id.id)])
                # raise UserError(other_model_record)
                if other_model_record:
                    for rec in other_model_record:
                        record['partner_id'] = rec.partner_id.id 
                        for line in rec.order_line:
                            order_line.append((0,0,{
                                'product_id': line.product_id.id,
                                'product_uom_id': line.product_uom.id,
                                'po_remainig_qty': line.product_qty - line.qty_received,
                                'specs':line.specification,
                                'total_qty':line.product_qty,
                            }))
                self['line_id'] = order_line

    