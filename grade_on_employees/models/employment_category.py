from odoo import models,api,fields,_
from odoo.exceptions import UserError


class EmploymentCategory(models.Model):
    _name="employee.category"

    name = fields.Char(string="Employment Category")