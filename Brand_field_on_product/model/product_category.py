from odoo import models, fields, api

# Rao Abdul Rehman

class ProductCategory(models.Model):
    _inherit="product.category"

    child_ids = fields.Many2many(string='Product Child Categories', comodel_name='product.category', relation='product_category_child_rel', column1='categ_id', column2='child_id')

    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if rec.parent_id:
                temp = rec
                while temp.parent_id:
                    temp = temp.parent_id
                    if not temp.parent_id:
                        temp['child_ids'] = [(4, rec.id)]
        return res