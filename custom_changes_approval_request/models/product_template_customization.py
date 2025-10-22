from odoo import fields, models,api, _
from odoo.exceptions import UserError

class ProductTemplateCustomization(models.Model):
    _inherit = 'product.template'

    def _prepare_variant_values(self, combination):
        self.ensure_one()
        return {
            'product_tmpl_id': self.id,
            'product_template_attribute_value_ids': [(6, 0, combination.ids)],
            'active': self.active,
            'default_code':self.default_code
        }