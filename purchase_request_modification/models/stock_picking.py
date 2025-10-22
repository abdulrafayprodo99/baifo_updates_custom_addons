from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for rec in self:
            for line in rec.move_ids_without_package:
                if line.quantity_done <= 0:
                    raise ValidationError("Quantity Done must be greater than zero")
            return super(StockPicking, rec).button_validate()