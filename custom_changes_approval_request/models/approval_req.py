from odoo import models, fields,api
from odoo.exceptions import UserError

class CustomApprovalRequest(models.Model):
    _inherit = 'approval.request'

    # Override the request_status field and modify the label
    request_status = fields.Selection([
        ('new', 'To Prepare'),           # Keep as-is
        ('pending', 'Verified'),         # Changed 'Submitted' to 'Prepare'
        ('approved', 'Approved'),       # Keep as-is
        ('refused', 'Refused'),         # Keep as-is
        ('cancel', 'Cancel'),           # Keep as-is
    ], default="new", compute="_compute_request_status",
        store=True, tracking=True,
        group_expand='_read_group_request_status')

    subject = fields.Char(string="Subject")

    # @api.model
    # def create(self, vals):
    #     record =  super(CustomApprovalRequest, self).create(vals)
    #     # raise UserError("hit")
    #     record.write({
    #         'name': 'Custom Value'  # Set the 'name' field or any other field
    #     })
        
    #     return record
    def name_get(self):
        result = []
        for record in self:
            # Display empty name if the state is 'new'
            if record.request_status == 'new':
                display_name = ''
            else:
                # Use the name field as the display name in other states
                display_name = record.name or ''
            result.append((record.id, display_name))
        return result

    
