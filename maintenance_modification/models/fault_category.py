from odoo import models,api,fields,_
from odoo.exceptions import UserError, ValidationError

class Fault_Cat(models.Model):
    _name = "fault.category"
    _description = "Fault Category"
    _rec_name = 'fault_category_id'
    fault_category_name = fields.Char(string="Fault Category Name")
    fault_category_id = fields.Char(string="Fault Category ID")

    display_name = fields.Char(compute='_compute_display_name')

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"Fault Category {rec.id}"
            if rec.fault_category_name and rec.fault_category_id:
                rec.display_name = f"{rec.fault_category_id}-{rec.fault_category_name}"
                
                
    # Saif Task_ID: 38937          
    @api.constrains('fault_category_id')
    def _check_fault_category_id_length(self):
        for record in self:
            if record.fault_category_id and len(record.fault_category_id) > 4:
                raise ValidationError("The 'Fault Category ID' field must be 4 characters long.")
                