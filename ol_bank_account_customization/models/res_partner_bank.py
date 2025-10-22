from odoo import api, fields, models

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    branch_address = fields.Char(string="Branch Address")
