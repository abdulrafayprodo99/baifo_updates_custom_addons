from odoo import models,fields,api,_
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    # _rec_names_search = ['name']
    _rec_name = "name"
    notes = fields.Html('Terms and Conditions', readonly=False)

    