from odoo import models, fields, api

class Discipline(models.Model):
    _name = 'discipline'
    _description = 'Discipline'

    name = fields.Char(string='PWM ID',size=7,required=True)
    name_des = fields.Char(string='Name', required=True)

    # @api.model
    # def _get_name(self):
    #     # Return pwmid instead of the name for the display
    #     return self.pwmid


