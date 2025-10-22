from odoo import api, fields, models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError



class LocationModel(models.Model):
    _name = "asset.location"
    _description = "Port Location Model"
    
    name = fields.Char(string='Name',required=True)
    id__ =  fields.Char("Code")
    
    
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.id__,rec.name)))
        return result

    

class AccountAsset(models.Model):
    _inherit="account.asset"
    asset_tag = fields.Char(string="Asset Tag")
    asset_location_id = fields.Many2one('asset.location' , string="Location")
    employee_id  = fields.Many2one('hr.employee', string="Employee")
