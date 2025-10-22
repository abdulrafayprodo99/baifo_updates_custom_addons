from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(
        string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company'), ('aop', 'AOP')]
    )
    
