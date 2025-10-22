from odoo import fields, models

class ProductNewField(models.Model):
    _inherit = "product.template"
    
    brand = fields.Selection([
            ('explosives', 'Explosives'),
            ('semi_explosives','Seismic Explosives'),
            ('kgs', 'Kgs'),
            ('anfo', 'Anfo'),
            ('plain', 'Plain Detonator'),
            ('electric', 'Electric Detonator'),
            ('seismic', 'Seismic Detonators'),
            ('binels', 'Binels'),
            ('delay', 'Delay Detonator'),
            ('safety', 'Safety Fuse'),
            ('thermo_tube', 'Thermo Tube'),
            ('other', 'Other Items')
        ],
        string="Brand Name"
    )
    brand_id=fields.Many2one('product.brand','Brand Name')
