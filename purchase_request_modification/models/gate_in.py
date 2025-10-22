from odoo import models,fields,api,SUPERUSER_ID,_
from odoo.exceptions import UserError


class GateVendorLine(models.Model):
    _inherit="gate.vendor.line"

    # specification =  fields.Text(string="Specification")

    
                

class GateIn(models.Model):
    _inherit="gate.in"
    vendor_type = fields.Selection([('vendor', 'Vendor'),('seles_return','Sales Return'), ('other', 'Other'),('outsource', 'Outsource'),('out', 'Gate Out')], string='Gate In Type' ,required=True)

    def action_to_prepared(self):
        for line in self.line_id:
            if line.qty == 0 or line.total_qty == 0:
                raise UserError(_("Quantity cannot be zero in line item"))
        super(GateIn, self).action_to_prepared()


    # @api.onchange('purchase_id')
    # def _onchange_all_po_line(self):
    #     order_line=[]
    #     self['line_id'] = False
    #     for record in self:
    #         if record.purchase_id:
    #             other_model_record = self.env['purchase.order'].search([('id','=', record.purchase_id.id)])
    #             # raise UserError(other_model_record)
    #             if other_model_record:
    #                 for rec in other_model_record:
    #                     record['partner_id'] = rec.partner_id.id    
    #                     for line in rec.order_line:
    #                         if line.qty_received < line.product_qty:
    #                             order_line.append((0,0,{
    #                                 'product_id': line.product_id.id,
    #                                 'product_uom_id': line.product_uom.id,
	# 			                    'total_qty' :line.product_qty - line.qty_received,
    #                                 'po_remainig_qty': line.remaining_quantity,
    #                                 'rem_qty': line.remaining_quantity,
    #                                 'specification': line.specification,
                                     
    #                             }))

    #             self['line_id'] = order_line


    