from odoo import api, models, fields
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    

    
    # picking_id = fields.Many2one('stock.picking', string="Picking", related='move_id.picking_id')

    name_3 = fields.Char(string="Info", compute='_compute_name_3')

    @api.depends('account_id')
    def _compute_name_3(self):
        for line in self:
            picking_name = line.ref or ''  # Picking name (which includes extra info)
            product_ref = line.product_id.default_code or ''  # Product internal reference
            product_name = line.product_id.name or ''  # Product name

            # Strip the part after the first ' - ' in picking_name
            if ' - ' in picking_name:
                picking_name = picking_name.split(' - ')[0]  # Keep only the first part before ' - '

            # Format the final output as "picking_name  - product_ref - product_name"
            line.name_3 = f"{picking_name}  - {product_ref} - {product_name}"