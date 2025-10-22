from odoo import fields, models

class ProductBrand(models.Model):
    _name = "product.brand"
    _description='Product Brand'
    _order  = "sequence Desc"

    name =fields.Char('Name')


    sequence= fields.Integer(string='Sequence')
    
   
