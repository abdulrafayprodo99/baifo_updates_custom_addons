from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    