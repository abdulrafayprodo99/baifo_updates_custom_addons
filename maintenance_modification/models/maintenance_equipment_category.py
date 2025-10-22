from odoo import models,api,fields,_
from odoo.exceptions import UserError, ValidationError

class Maintenance_Equip_Categ(models.Model):
    _inherit = "maintenance.equipment.category"

    equip_category_name = fields.Char(string="Equipment Category Name")
   
    # Saif Code Start Task_ID: 38937
    # equip_category_id = fields.Integer(string="Equipment Category ID")
    equip_category_id = fields.Char(string="Equipment Category ID")
    
    
            
    @api.constrains('equip_category_id')
    def _check_equip_category_id_length(self):
        for record in self:
            if record.equip_category_id and len(record.equip_category_id) > 4:
                raise ValidationError("The 'Equipment Category ID' field must be 4 characters long.")