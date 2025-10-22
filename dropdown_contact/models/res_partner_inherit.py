from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection(
        [('customer', 'Customer'), 
         ('vendor', 'Vendor'),
         ('both', 'Both'),
         ('contact', 'Contact'),
         ('employee', 'Employee')],  # New 'employee' option added
        string="Partner Type",
        required=True
    )

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        """Update the customer/supplier status based on the selected partner type."""
        if self.partner_type == 'customer':
            self.customer_rank = 1
            self.supplier_rank = 0
        elif self.partner_type == 'vendor':
            self.customer_rank = 0
            self.supplier_rank = 1
        elif self.partner_type == 'both':
            self.customer_rank = 1
            self.supplier_rank = 1
        elif self.partner_type == 'employee':
            # Specific behavior for 'employee'
            self.customer_rank = 0
            self.supplier_rank = 0
        else:
            # For 'contact', set both to 0
            self.customer_rank = 0
            self.supplier_rank = 0
