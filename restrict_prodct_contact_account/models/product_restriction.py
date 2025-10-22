from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"



    published = fields.Boolean(string='Published', default=True, readonly=True)

    is_published = fields.Boolean(string='Published', default=True, readonly=True)



    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['is_published'] = False
            val['active'] = False
        return super().create(vals)

    # def write(self, vals):
    #     for val in vals:
    #         val['active'] = False
    #     return super().write(vals)
        # # Deactivate the product if 'published' is set to False
        # if 'published' in vals and not vals['published']:
        #     vals['active'] = False  # Deactivate the product if 'published' is False
        # # Call the super method to execute the original write logic
        # return super(ProductTemplate, self).write(vals)

    
    def action_prepared(self):
        # Update the approval state and prepared fields
        self.write({
            'approval_state': 'prepared',
            'prepared_by': self.env.user.id,  # Use env.user to get the current user
            'prepared_timestamp': fields.Datetime.now(),
            'active': False  # Set the product as inactive
        })

    
    def action_approve(self):
        # Prepare the values to update
        values = {
            'approval_state': 'approve',
            'Approve_by': self.env.user.id,  # Use env.user to get the current user
            'approve_timestamp': fields.Datetime.now(),
            'readonly_check': True,
            'active': True,  # Make the product active
            'is_published': True
        }
        product_variant = self.env['product.product'].search([
            ('name', '=', self.name),
            ('active', '=', False)
        ], limit=1) 

        if product_variant:
            product_variant.write({
                'active': True, 
                'is_published': True,
                'default_code':self.default_code
            })

        
        # Write the changes to the records
        self.write(values)



