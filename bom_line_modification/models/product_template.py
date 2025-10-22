from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Create the custom field on product.template
    default_purchase_rate = fields.Float(
        string="Default Purchase Rate",
        help="Custom purchase rate for the product."
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Create a related field on product.product pointing to the custom field on product.template
    default_purchase_rate = fields.Float(
        string="Default Purchase Rate", 
        related='product_tmpl_id.default_purchase_rate', 
        store=True,
        help="The custom purchase rate from the template."
    )



# from odoo import fields, models, api

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    # Related field to fetch default_purchase_rate from product.product
    default_purchase_rate = fields.Float(
        string="Default Purchase Rate",
        related='product_id.product_tmpl_id.default_purchase_rate',  # Fetch from product.product
        store=True,
        readonly=True,
    )

    # Computed field to calculate total cost
    total_cost = fields.Float(
        string="Total Cost",
        compute='_compute_total_cost',
        help="Total cost (product_qty * default_purchase_rate)"
    )

    @api.depends('default_purchase_rate')
    def _compute_total_cost(self):
        for line in self:
            if line.product_qty and line.default_purchase_rate:
                line.total_cost = line.product_qty * line.default_purchase_rate
            else:
                line.total_cost = 0.0
