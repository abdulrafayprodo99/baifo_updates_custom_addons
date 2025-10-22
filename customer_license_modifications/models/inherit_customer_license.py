from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class CustomerLicense(models.Model):
    _inherit = "customer.license"
    

    validity_from = fields.Date(string="Validity From", required=True)
    validity_to = fields.Date(string="Validity To", required=True)
    name = fields.Char(string="Name",required=True)
    customer_code_new = fields.Char(string="Customer Code New",required = True)
    customer_name = fields.Many2one('res.partner', string='Customer',required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('approved', 'Approved')
    ], string="Status", default='draft', tracking=True)

    def action_verify(self):
        self.state = 'verified'

    def action_approve(self):
        if self.state != 'verified':
            raise ValidationError("You can only approve a verified license.")
        self.state = 'approved'




    @api.model
    def create(self, vals):
        if isinstance(vals,dict):
            vals_list = [vals]
        for vals in vals_list:
            new_validity_from = vals.get("validity_from")
            new_validity_to = vals.get("validity_to")
            new_name = vals.get("name")

            if new_validity_from and new_validity_to and new_name:
                new_validity_from = fields.Date.to_date(new_validity_from)
                new_validity_to = fields.Date.to_date(new_validity_to)

                if new_validity_from == new_validity_to:
                    raise ValidationError("Validity From and Validity To cannot be the same.")

                same_license_records = self.env["customer.license"].search([("name", "=", new_name)])

                for record in same_license_records:
                    old_validity_from = fields.Date.to_date(record.validity_from)
                    old_validity_to = fields.Date.to_date(record.validity_to)

                    if new_validity_from == old_validity_from and new_validity_to == old_validity_to:
                        raise ValidationError("Record against these dates already exists.")

                    if old_validity_from <= new_validity_to <= old_validity_to:
                        raise ValidationError("Record against these dates already exists.")

        return super(CustomerLicense, self).create(vals)


    # def write(self, vals):
    #     new_validity_from = vals.get("validity_from", self.validity_from)
    #     new_validity_to = vals.get("validity_to", self.validity_to)
    #     new_name = vals.get("name", self.name)

    #     if new_validity_from and new_validity_to and new_name:
    #         new_validity_from = fields.Date.to_date(new_validity_from)
    #         new_validity_to = fields.Date.to_date(new_validity_to)

    #         if new_validity_from == new_validity_to:
    #             raise ValidationError("Validity From and Validity To cannot be the same.")

    #         same_license_records = self.env["customer.license"].search([("name", "=", new_name), ("id", "!=", self.id)])

    #         for record in same_license_records:
    #             old_validity_from = fields.Date.to_date(record.validity_from)
    #             old_validity_to = fields.Date.to_date(record.validity_to)

    #             if new_validity_from == old_validity_from and new_validity_to == old_validity_to:
    #                 raise ValidationError("Record against these dates already exists.")

    #             if old_validity_from <= new_validity_to <= old_validity_to:
    #                 raise ValidationError("Record against these dates already exists.")

    #     return super(CustomerLicense, self).write(vals)
    

    def write(self, vals):
        new_validity_from = vals.get("validity_from", self.validity_from)
        new_validity_to = vals.get("validity_to", self.validity_to)
        new_name = vals.get("name", self.name)

        if new_validity_from and new_validity_to and new_name:
            new_validity_from = fields.Date.to_date(new_validity_from)
            new_validity_to = fields.Date.to_date(new_validity_to)

            if new_validity_from == new_validity_to:
                raise ValidationError("Validity From and Validity To cannot be the same.")

            same_license_records = self.env["customer.license"].search([("name", "=", new_name), ("id", "!=", self.id)])

            for record in same_license_records:
                old_validity_from = record.validity_from and fields.Date.to_date(record.validity_from)
                old_validity_to = record.validity_to and fields.Date.to_date(record.validity_to)

                # Ensure the old validity dates are not None before comparing
                if old_validity_from and old_validity_to:
                    if new_validity_from == old_validity_from and new_validity_to == old_validity_to:
                        raise ValidationError("Record against these dates already exists.")

                    if old_validity_from <= new_validity_to <= old_validity_to:
                        raise ValidationError("Record against these dates already exists.")

        return super(CustomerLicense, self).write(vals)


