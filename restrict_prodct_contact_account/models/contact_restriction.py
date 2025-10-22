from odoo import fields, models,  api

class ResPartner(models.Model):
    _inherit = 'res.partner'


    is_published = fields.Boolean(string='Published', default=True, readonly=True)



    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['is_published'] = False
            val['active'] = False
        return super().create(vals)

    

    def action_verify(self):
        # Set approval state to 'verify' and make the partner inactive
        self.write({
            'approval_state': 'verify',
            'verify_by': self.env.uid,  # Set verified by the current user
            'active': False,  # Mark the partner as inactive
        })
        
    def action_approve(self):
        # Set approval state to 'approve' and make the partner active
        self.write({
            'approval_state': 'approve',
            'Approve_by': self.env.uid,  # Set approved by the current user
            'readonly_check': False,  # Reset readonly_check to False
            'active': True,  # Mark the partner as active
            'is_published' : True
        })
