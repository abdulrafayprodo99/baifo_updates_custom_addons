from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class CustomerLicense(models.Model):
    _inherit = "mrp.bom"
    

