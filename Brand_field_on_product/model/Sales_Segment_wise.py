from odoo import fields, models, api 
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'
    x_product_domain_location = fields.Boolean(string='Product Domain Location')


class ProductNewField(models.Model):
    _name="sales.segment.target"

    name = fields.Char(string="Name", readonly=True, default="New")
    tag=fields.Many2one(string="Sector", comodel_name="res.partner.category")
    validate_from=fields.Date(string="Validate From")
    validate_to=fields.Date(string="Validate to")
    target=fields.Float(string="Projection")
    customer_field=fields.Many2one(string="Customer", comodel_name="res.partner")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('SalesSegmentTarget.sequence') or 'New'
        return super().create(vals)
    
    # Add constraint to check if the new record's date range overlaps with any existing records
    @api.constrains('tag', 'validate_from', 'validate_to')
    def _check_date_overlap(self):
        for record in self:
            # Search for existing records with the same tag and overlapping date ranges
            existing_records = self.search([
                ('tag', '=', record.tag.id),
                ('id', '!=', record.id)
            ])
            if record.validate_from and record.validate_to:
                #                 ('validate_from', '<=', record.validate_to),
                # ('validate_to', '>=', record.validate_from)
                existing_records =  existing_records.filtered(lambda x : record.validate_from <=x.validate_from <= record.validate_to or record.validate_from <=x.validate_to <= record.validate_to )

            if existing_records:
                raise ValidationError(f"A target for the tag '{record.tag.name}' already exists within the time period "
                                      f"({existing_records[0].validate_from} to {existing_records[0].validate_to}). "
                                      "Please choose a different date range.")
            

            