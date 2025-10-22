from odoo import models,api,fields
from odoo.exceptions import UserError,ValidationError

class CollectionSummaryTarget(models.Model):
    _name = 'collection.summary.target'

    tag = fields.Many2one(string="Tags", comodel_name="res.partner.category")
    customer_id=fields.Many2one(string="Customer", comodel_name="res.partner")
    validate_from=fields.Date(string="Validate From")
    validate_to=fields.Date(string="Validate to")
    target=fields.Float(string="Projection")