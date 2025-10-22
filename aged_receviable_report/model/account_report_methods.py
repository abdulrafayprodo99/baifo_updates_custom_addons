from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    prepared_by = fields.Many2one("res.users", string="Dispatch Prepared by", readonly=True,compute='_compute_field')
    gate_in_id_required =  fields.Boolean(compute="_compute_gate_in_id_required")

    def _compute_gate_in_id_required(self):
        for rec in self:
            if 'gate_in_id' not in rec.fields_separated:
                rec.gate_in_id_required = True
            else:
                rec.gate_in_id_required = False
                

    def _compute_field(self):
        for record in self:
            record.prepared_by = record.env.uid

    # def validate_vals_to_write(self,vals):

    #     if isinstance(vals,dict) and vals.get('picking_type_id', self.picking_type_id or False) and 'GRN' in self.env['stock.picking.type'].sudo().browse(vals.get('picking_type_id',self.picking_type_id or False).name) and not vals.get('gate_in_id',self.gate_in_id or False):
    #         raise UserError("Gate in is required for GRN")
    #     elif isinstance(vals,dict) and vals.get('gate_in_id',self.gate_in_id or False):
    #         gate_in = self.env['gate.in'].sudo().browse(vals.get('gate_in_id',self.gate_in_id or False))
            
    #         if not gate_in:
    #             raise UserError("Gate in not found")
    #         reserved = self.env['stock.picking'].sudo().search([('state','!=','cancel')])
    #         reserved = reserved.filtered(lambda x: gate_in.id in x.gate_in_id.ids )
    #         if reserved:
    #             raise UserError("Gate in is already reserved")
    # def create(self,vals):
    #     for rec in self:
    #         if isinstance(vals,list):
    #             for val in vals:
    #                 rec.validate_vals_to_write(val)
    #         elif isinstance(vals,dict):
    #             rec.validate_vals_to_write(vals)

    #     return super(StockPicking, self).create(vals)

    # def write(self,vals):
    #     for rec in self:
    #         if isinstance(vals,list):
    #             for val in vals:
    #                 rec.validate_vals_to_write(val)
    #         elif isinstance(vals,dict):
    #             rec.validate_vals_to_write(vals)
            
    #     return super(StockPicking, self).write(vals)

    @api.onchange('gate_in_id')
    def _onchange_gate_in_id(self):
        if not self:
            return
        if self.gate_in_id:
            reserved = self.env['stock.picking'].sudo().search([('state','!=','cancel'),('id','!=',self._origin.id)])
            reserved = reserved.filtered(lambda x: any(ele in x.gate_in_id.ids for ele in self.gate_in_id.ids) )

            if reserved:
                raise UserError("Gate in is already reserved")
    
    