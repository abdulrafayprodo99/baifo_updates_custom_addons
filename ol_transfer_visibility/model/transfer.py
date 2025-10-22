from odoo import models,api,fields
from odoo.exceptions import UserError


class TransferVisibility(models.Model):
    _inherit = "stock.picking.type"
    
    field_custom = fields.Many2many("ir.model.fields",domain="[('model_id.model', '=', 'stock.picking')]")
    fields_comma_separated = fields.Char(string="Fields Comma Separated", readonly=True)
    
    @api.onchange("field_custom")
    def update_fields_comma_separated(self):
        for record in self:
            selected_field_names = record.field_custom.mapped('name')
            record.fields_comma_separated = ', '.join(selected_field_names)
    
    @api.model
    def create(self, vals):
        if 'field_custom' in vals:
            field_custom_ids = vals.get('field_custom')
            field_custom_records = self.env['ir.model.fields'].browse(field_custom_ids[0][2])
            vals['fields_comma_separated'] = ', '.join(field_custom_records.mapped('name'))
        return super(TransferVisibility, self).create(vals)
        

    def write(self, vals):
        if 'field_custom' in vals:
            field_custom_ids = vals.get('field_custom')
            field_custom_records = self.env['ir.model.fields'].browse(field_custom_ids[0][2])
            vals['fields_comma_separated'] = ', '.join(field_custom_records.mapped('name'))
        return super(TransferVisibility, self).write(vals)

class Tranfer(models.Model):
    _inherit = 'stock.picking'
    fields_separated = fields.Char(
        string="Fields Comma Separated",
        related='picking_type_id.fields_comma_separated',
        readonly=True,
        store=False,
    )
    
    # def button_validate(self):
    #     res = super(Tranfer, self).button_validate()
    #     picking= self.env['stock.picking'].search([('origin','=',self.origin),('picking_type_id.name','=','Inventory Transfer - Quarantine to WH')])
    #     if picking:
    #         # raise UserError(str())
    #         picking.write({'import_grn_ref':self.name,'gate_in_id':self.gate_in_id.ids})
    #     return res
