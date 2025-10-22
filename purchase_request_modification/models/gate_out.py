from odoo import models,fields,api,SUPERUSER_ID,_
from odoo.exceptions import UserError
from datetime import datetime

class GateOut(models.Model):
    _inherit="gate.out"

    def action_to_prepared(self):
        for line in self.line_ids:
            if line.qty == 0:
                raise UserError(_("Quantity cannot be zero in line item"))
        super(GateOut, self).action_to_prepared()
 
    customer_type = fields.Selection([('customer', 'Customer'), ('other', 'Other'),('gate_in','Gate In'),('outsource', 'Outsource')], string='Gate Out Type')
    vehicle_number= fields.Char(string="Vehicle Number", _compute='_compute_seal_no', readonly=False,store=True)

    # @api.model
    # def create(self,vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('Gate_OUT') or _('New')
    #         vals['state'] = 'draft'
    #         vals['date_time']= datetime.now()
    #     res = super(GateOut,self).create(vals)
    #     return res



    # @api.model
    # def create(self,vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         if vals['location_name'] == 'ho':
    #             vals['name'] = self.env['ir.sequence'].next_by_code('Gate_OUT') or _('New')    
    #         # else:
    #         #     raise UserError(_("Location Name is Required"))
    #         if vals['location_name'] == 'facorty':
    #             vals['name'] = self.env['ir.sequence'].next_by_code('Gate_OUT_FAC') or _('New')
    #         # else:
    #             # raise UserError("Location Name is Required")
    #         vals['date_time']= datetime.now()
    #         vals['state']= 'draft'
    #     res = super(GateOut,self).create(vals)
    #     return res
    